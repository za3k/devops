#!/bin/sh
. lib/main.sh

append_public_key() {
    [ $# -ne 3 ] && echo "<RUNENV> append_public_key FILE KEY" && exit 1
    DEST="$1"
    PUBLIC_KEY="$2"
    run "fgrep '$PUBLIC_KEY' $DEST || echo '$PUBLIC_KEY' >$DEST"
}

ssh_ensure_key() {
    [ $# -ne 3 ] && echo "<RUNENV> OWNER=<OWNER> [OWNER_GROUP=<OWNER_GROUP>] ssh_ensure_key FILE" && exit 1
    OWNER=${OWNER-$USER}
    OWNER_GROUP=${OWNER_GROUP-$OWNER}
    run '[ -f "$path" ] || ssh-keygen -f "{path}" -N && chown ${OWNER}:${OWNER_GROUP} ; cat "$path"'
}

ssh_get_public_key() {
  USER=root run "cat ${1}.pub"
}

