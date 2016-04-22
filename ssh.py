#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

import StringIO
from fabric.api import run, env, sudo, put, get, cd, settings, hosts
from fabric.contrib import files

def ensure_key(path='/root/.ssh/id_rsa'):
    if not files.exists(path):
        create_key(path)
    return get_public_key(path)

def create_key(path):
    run('ssh-keygen -f "{path}" -N ""'.format(path=path))

def get_public_key(path):
    output = StringIO.StringIO()
    get(path + '.pub', output)
    public_key = output.getvalue()
    output.close()
    return public_key
