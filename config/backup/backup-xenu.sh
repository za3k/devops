#!/bin/sh
/var/local/generic-backup.sh germinate-backup:/data/snapshots.daily/xenu-linux
ssh germinate-backup sudo /var/local/snapshot xenu-linux
