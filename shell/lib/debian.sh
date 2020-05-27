#!/bin/sh
. lib/main.sh
debian_ensure_sudo() {
    USER="" HOST=$HOST run "which sudo >/dev/null" && return 0
    USER="" HOST=$HOST run "[ 0 -eq `id -u` ]" || return 0
    USER="" HOST=$HOST run "apt-get install -y sudo"
    return $?
}
debian_ensure_root() {
    ssh $HOST "0 -eq `id -u` | which sudo >/dev/null"
    return $?
}

debian_package() {
    :
}
