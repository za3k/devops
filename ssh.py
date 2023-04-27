#!/usr/bin/python2
import io
from fabric.api import run, env, sudo, put, get, cd, settings, hosts
from fabric.contrib import files

def ensure_key(path='/root/.ssh/id_rsa', use_sudo=False):
    if not files.exists(path, use_sudo=use_sudo):
        create_key(path, use_sudo=use_sudo)
    return get_public_key(path, use_sudo=use_sudo)

def create_key(path, use_sudo=False):
    command = 'ssh-keygen -f "{path}" -N ""'.format(path=path)
    if use_sudo:
        sudo(command)
    else:
        run(command)

def get_public_key(path, use_sudo=False):
    output = io.StringIO()
    get(path + '.pub', output, use_sudo=use_sudo)
    public_key = output.getvalue()
    output.close()
    return public_key
