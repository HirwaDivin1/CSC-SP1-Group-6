#!/bin/sh
# Feasibility experiment: can fail2ban (1) call our hook with the banned address,
# and (2) apply a "shared" ban that blocks SSH WITHOUT calling the hook again?
# Also checks that the node can end a shared ban itself (needed for expiry).
# Usage: ./run.sh   (needs Docker; writes the transcript to output.txt)
set -u
cd "$(dirname "$0")"
IMG=blocklist-feasibility NET=blocklist-net
OUT=output.txt
exec > "$OUT" 2>&1

say() { printf '\n=== %s ===\n' "$*"; }
campus() { docker exec campus "$@"; }
try_ssh() {  # one password login attempt from the attacker; prints how it ended
  docker exec attacker sh -c 'sshpass -p wrong-password ssh -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null -o PubkeyAuthentication=no \
    -o PreferredAuthentications=password -o NumberOfPasswordPrompts=1 \
    -o ConnectTimeout=4 test@campus true 2>&1 | grep -v "^Warning: Permanently" | tail -1'
}
hooklog() { campus sh -c 'cat /var/log/blocklist-hook.log 2>/dev/null || echo "(hook never ran)"'; }

say "Run started $(date -u '+%Y-%m-%dT%H:%M:%SZ') on $(uname -sr)"
docker --version

docker rm -f campus attacker >/dev/null 2>&1
docker network rm "$NET" >/dev/null 2>&1
docker build -q -t "$IMG" . >/dev/null || { echo "BUILD FAILED"; exit 1; }
docker network create "$NET" >/dev/null
docker run -d --name campus --network "$NET" --cap-add NET_ADMIN --cap-add NET_RAW \
  "$IMG" /usr/local/bin/campus-start.sh >/dev/null
docker run -d --name attacker --network "$NET" "$IMG" sleep infinity >/dev/null
ATTACKER_IP=$(docker inspect -f "{{(index .NetworkSettings.Networks \"$NET\").IPAddress}}" attacker)

for i in $(seq 1 30); do campus fail2ban-client ping >/dev/null 2>&1 && break; sleep 1; done
say "Versions inside the campus container"
campus fail2ban-client --version
campus python3 --version
campus sh -c '. /etc/os-release; echo "$PRETTY_NAME"'
echo "attacker address: $ATTACKER_IP"

say "Step 0: before any failures, the attacker reaches the SSH password check"
try_ssh

say "Step 1: attacker makes 6 failed logins (threshold is 5)"
for i in 1 2 3 4 5 6; do printf 'attempt %s: ' "$i"; try_ssh; done
for i in $(seq 1 20); do campus fail2ban-client status sshd | grep -q "$ATTACKER_IP" && break; sleep 1; done
campus fail2ban-client status sshd
say "Step 1 result: hook log (expect one 'ban' line with the attacker address, jail=sshd)"
hooklog
say "Step 1: attacker tries again while locally banned"
try_ssh

say "Step 2: node applies a shared ban for a documentation address (203.0.113.7)"
campus fail2ban-client set shared banip 203.0.113.7
sleep 3
campus fail2ban-client status shared
say "Step 2 result: hook log (expect NO new line: a shared ban must not be reported again)"
hooklog

say "Step 3: remove the local ban, confirm the attacker can reach SSH again"
campus fail2ban-client set sshd unbanip "$ATTACKER_IP"
sleep 2
try_ssh

say "Step 4: node applies a shared ban for the attacker; attacker tries SSH"
campus fail2ban-client set shared banip "$ATTACKER_IP"
sleep 2
try_ssh
say "Step 4 result: hook log (expect no new 'ban' line for jail=shared)"
hooklog

say "Step 5: node ends the shared ban itself (what expiry will do); attacker tries SSH"
campus fail2ban-client set shared unbanip "$ATTACKER_IP"
sleep 2
try_ssh
say "Step 5 result: hook log (expect no line for jail=shared)"
hooklog

say "SSH log lines from the attacker (how many lines fail2ban could count per attempt)"
campus sh -c "grep -F '$ATTACKER_IP' /var/log/auth.log | sed 's/^.*sshd\[[0-9]*\]: //'"
say "fail2ban's own log of what it found and banned"
campus sh -c "grep -E 'Found|Ban|Unban' /var/log/fail2ban.log | sed 's/^[0-9-]* //'"

say "Firewall rules at the end"
campus sh -c 'iptables -S 2>/dev/null | grep f2b || echo "(no f2b rules)"'

say "Run finished $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
docker rm -f campus attacker >/dev/null 2>&1
docker network rm "$NET" >/dev/null 2>&1
