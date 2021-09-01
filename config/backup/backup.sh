#!/bin/sh
set -e
if [ -z "$HOST" ]; then
  HOST=`cat /proc/sys/kernel/hostname`
fi

/bin/sh /var/local/generic-backup.sh germinate-backup:/data/snapshots.daily/$HOST >/dev/null 2>/dev/null
ssh germinate-backup sudo /var/local/snapshot $HOST
