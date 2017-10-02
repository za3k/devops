#!/bin/sh
/var/local/generic-backup.sh burn-backup:/data/archive/forget.latest
ssh burn-backup sudo /var/local/forget.snapshot
