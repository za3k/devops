#!/bin/sh
/var/local/generic-backup.sh germinate-backup:/data/snapshots.daily/forget
ssh germinate-backup sudo /var/local/snapshot forget
