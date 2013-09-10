#!/bin/sh

kill -15 `ps aux | grep aswcp_daemon | grep -v grep | awk '{print $2}'`

exit 0
