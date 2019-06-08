#!/bin/sh
/var/local/generic-backup.sh germinate-backup:/data/snapshots.daily/avalanche
ssh germinate-backup sudo /var/local/snapshot avalanche
