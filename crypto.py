#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import run, env, sudo, put, get, cd, settings, hosts
from fabric.contrib import files
from cuisine import dir_ensure, group_ensure, mode_sudo
import random, string

def put_cert(cert):
    with mode_sudo():
        dir_ensure('/etc/ssl/certs', mode='1777')
    return put(cert, '/etc/ssl/certs', mode='0644')[0]

def put_key(key, **kwargs):
    with mode_sudo():
        dir_ensure('/etc/ssl/private', mode='1777')
    return put(key, '/etc/ssl/private', mode='0640', **kwargs)[0]

def ensure_dhparams(path='/etc/ssl/dhparams.pem', size=2048):
    if not files.exists(path):
        sudo('openssl dhparam -out "{dhparams}" {size}'.format(dhparams=path, size=size))

def random_password(size=16, valid_characters=(string.ascii_letters + string.digits)):
    return ''.join(random.choice(valid_characters) for _ in range(size))

