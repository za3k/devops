#!/bin/sh
/var/local/generic-backup.sh burn-backup:/data/archive/equilibrate.latest
ssh burn-backup sudo /var/local/equilibrate.snapshot
