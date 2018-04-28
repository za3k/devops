#!/bin/sh
/var/local/generic-backup.sh germinate-backup:/data/snapshots.daily/corrupt
ssh germinate-backup sudo /var/local/snapshot corrupt
