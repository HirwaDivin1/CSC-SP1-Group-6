# One image plays both roles in the feasibility experiment:
#   campus   - SSH server + fail2ban, with a local jail that reports and a shared jail that must not
#   attacker - only uses the SSH client (sshpass) to make failed logins
FROM debian:12-slim

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      openssh-server openssh-client sshpass fail2ban rsyslog iptables python3 procps \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /etc/fail2ban/jail.d/defaults-debian.conf \
 && mkdir -p /run/sshd /opt/blocklist \
 && touch /var/log/auth.log /var/log/blocklist-shared.log

COPY config/jail.local /etc/fail2ban/jail.local
COPY config/action.d/blocklist-report.conf /etc/fail2ban/action.d/blocklist-report.conf
COPY config/filter.d/blocklist-shared.conf /etc/fail2ban/filter.d/blocklist-shared.conf
COPY hook.py /opt/blocklist/hook.py
COPY campus-start.sh /usr/local/bin/campus-start.sh
RUN chmod +x /opt/blocklist/hook.py /usr/local/bin/campus-start.sh
