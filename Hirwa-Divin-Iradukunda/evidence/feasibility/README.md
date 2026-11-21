# Feasibility experiment: fail2ban hook and shared jail

**Question.** Can a node learn of each local fail2ban ban (with the banned address), and can it apply a shared ban through fail2ban that blocks SSH *without* being reported again? Can the node also end a shared ban itself, as expiry requires?

**Why this question.** Every requirement in Section 2 depends on it. If fail2ban could not call the node, or if shared bans were reported again, nodes would miss local bans or keep re-reporting each other's bans in a loop.

**Setup.** Two Docker containers on one laptop, built from [Dockerfile](Dockerfile) (Debian 12, fail2ban 1.0.2, Python 3.11.2):

- `campus`: SSH server and fail2ban with two jails ([config/jail.local](config/jail.local)).
  - `sshd` is the normal local jail: it bans after 5 failures within an hour, and its actions both add a firewall rule and run [hook.py](hook.py).
  - `shared` is where a node puts shared bans: it adds a firewall rule but has no hook, its filter never matches, and its bans never end on their own.
- `attacker`: makes SSH password logins as a user that does not exist.

[hook.py](hook.py) stands in for the node: it only records each call. Containers are a stand-in for the virtual machines in Section 2.

**Procedure.** [run.sh](run.sh) runs these steps and writes [output.txt](output.txt):

0. One failed login.
1. Six more login attempts (the first two failed; the other four were refused because the ban had started); check the ban and the hook log.
2. Shared-ban a documentation address (203.0.113.7); check the hook log.
3. Remove the local ban.
4. Shared-ban the attacker; try SSH; check the hook log.
5. End the shared ban; try SSH.

**Evidence.** [output.txt](output.txt), run on November 17, 2026 (second run, which also printed the SSH and fail2ban logs; the first run's transcript was overwritten).

**Findings.**

| # | Finding | Where in output.txt |
|---|---|---|
| 1 | fail2ban banned the attacker and called the hook once with its address and jail: `ban ip=172.18.0.3 jail=sshd` | Step 1 result |
| 2 | A ban in the `shared` jail did not call the hook, so shared bans are not reported again | Steps 2 and 4 results |
| 3 | A shared ban alone blocked SSH: the attacker got `Connection refused` while only the shared ban applied | Step 4 |
| 4 | Removing the shared ban restored access (the attacker reached the password check again) | Step 5 |
| 5 | Local and shared bans are kept in separate firewall chains (`f2b-sshd`, `f2b-shared`) | Firewall rules |
| 6 | fail2ban counts matching log lines, not login attempts: each failed login wrote 3 or 4 lines to the SSH log, about 2 of which matched the filter, so the 5th match and the ban came within 3 failed logins | SSH log lines; fail2ban log |
| 7 | The hook also runs when a local ban ends (`unban ... jail=sshd`) | Step 4 result |
| 8 | After a local unban, a match from before the unban (18:20:29) still counted, so the second failed login after the unban (step 5) caused a new local ban | fail2ban log, 18:20:29–18:20:51 |

**Decisions that follow.**

- Use the hook for local bans and a separate `shared` jail for shared bans (findings 1–5).
- The node ends shared bans itself, which is how report expiry will work (finding 4).
- The node ignores `unban` calls in the six-week prototype: a report stays valid until it expires (finding 7). Withdrawal stays in Semester II.
- Acceptance checks must say "make failed logins until fail2ban bans the address", not "fail 5 logins" (finding 6).

**Limits.** One run of each step, in containers rather than virtual machines, with fail2ban's all-ports firewall rule (the design will use an SSH-only rule so bans never block node traffic), with one attacker and an invalid user name. Logins for an existing user may write a different number of lines. Timing was not measured.

**Run.** Needs Docker and permission to use it (root or the `docker` group). From this folder: `sudo ./run.sh`. It downloads the `debian:12-slim` image and Debian packages on the first run, takes 1–2 minutes, overwrites `output.txt`, and removes its containers and network at the end.
