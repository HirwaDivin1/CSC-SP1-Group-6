#!/usr/bin/env python3
"""Stand-in for the node's ban hook in the feasibility experiment.

fail2ban runs this as: hook.py <ban|unban> <ip> <jail>
In the prototype it would send a report to the local node; here it only records
the call, so the experiment can check which bans would have been reported.
"""
import sys
import time

event, ip, jail = sys.argv[1], sys.argv[2], sys.argv[3]
with open("/var/log/blocklist-hook.log", "a") as f:
    f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {event} ip={ip} jail={jail}\n")
