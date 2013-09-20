#!/bin/sh

PID=$(netstat -ntlup | grep python | grep `cat .config | grep "listen_port" | awk '{print $3}'` | awk '{print $7}' | cut -d/ -f1)

kill -9 $PID

exit 0
