#!/bin/sh
/var/local/generic-backup.sh germinate-backup:/data/snapshots.daily/equilibrate
ssh germinate-backup sudo /var/local/snapshot equilibrate
