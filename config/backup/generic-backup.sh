#!/bin/bash
START=$(date +%s)
DEST="$1"
shift 1

[ -e /bin/log ] && echo "Beginning backup" | /bin/log backup

RSYNC_OPTIONS="-aAXv --progress --inplace -M--fake-super"
if [ -n "$BANDWIDTH" ]; then
    RSYNC_OPTIONS="--bwlimit $BANDWIDTH $RSYNC_OPTIONS"
fi

set -x
rsync $RSYNC_OPTIONS --one-file-system / "$DEST" --delete --delete-excluded --exclude-from=/var/local/backup-exclude "$@"
set +x
FINISH=$(date +%s)
echo "total time: $(( ($FINISH-$START) / 60 )) minutes, $(( ($FINISH-$START) % 60 )) seconds"

[ -e /bin/log ] && echo "Completed backup in $(( $FINISH-$START ))s" | /bin/log backup
