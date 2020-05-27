#!/bin/sh
run() {
    [ $# -eq 0 ] && echo "Usage: HOST=<HOST> USER=<USER> run COMMAND..." && exit 1
    if [ -z "$USER" ]; then
        echo "[$HOST]" "$@" >&@
        cat | ssh $HOST "$@"
    elif [ "$USER" == "root" ]; then
        echo "[$USER@$HOST]" "$@" >&@
        cat | ssh $HOST "sudo $@"
    elif [ "$USER" != "root" ]; then
        echo "[$USER@$HOST]" "$@" >&@
        cat | ssh $HOST "sudo -u $USER $@"
    fi
}

put_file() {
    [ $# -ne 3 ] && echo "Usage: HOST=<HOST> OWNER=<OWNER> [OWNER_GROUP=<OWNER_GROUP>] put_file FROM TO MODE" && exit 1
    SOURCE="$1"
    DEST="$2"
    MODE="$3"
    OWNER=${OWNER-$USER}
    OWNER_GROUP=${OWNER_GROUP-$OWNER}
    cat "$SOURCE" | run "cat >$DEST && chown ${OWNER}:${OWNER_GROUP} && chmod $MODE"
}
