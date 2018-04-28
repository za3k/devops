#!/bin/sh
/var/local/generic-backup.sh germinate-backup:/data/snapshots.daily/deadtree
ssh germinate-backup sudo /var/local/snapshot deadtree
