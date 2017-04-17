#!/bin/sh
/var/local/generic-backup.sh burn-backup:/data/archive/xenu-linux.latest
ssh burn-backup sudo /var/local/xenu-linux.snapshot
