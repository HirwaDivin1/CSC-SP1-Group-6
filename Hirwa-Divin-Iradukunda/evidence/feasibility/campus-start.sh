#!/bin/sh
# Start logging, the SSH server and fail2ban inside the campus container, then wait.
rsyslogd
/usr/sbin/sshd
fail2ban-client start
exec sleep infinity
