#!/bin/sh
set -e
/var/local/generic-backup.sh germinate-backup:/data/snapshots.daily/corrupt >/dev/null 2>/dev/null
ssh germinate-backup sudo /var/local/snapshot corrupt
