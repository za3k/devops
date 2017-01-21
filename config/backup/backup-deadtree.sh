#!/bin/sh
/var/local/generic-backup.sh burn-backup:/data/archive/deadtree.latest
ssh burn-backup sudo /var/local/deadtree.snapshot
