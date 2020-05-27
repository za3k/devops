#!/bin/sh
set -e
/var/local/generic-backup.sh germinate-backup:/data/snapshots.daily/equilibrate >/dev/null 2>/dev/null
ssh germinate-backup sudo /var/local/snapshot equilibrate
