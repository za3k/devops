#!/bin/sh
/var/local/generic-backup.sh burn-backup:/data/archive/corrupt.latest
ssh burn-backup sudo /var/local/corrupt.snapshot
