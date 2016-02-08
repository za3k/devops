#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import run, env, sudo, put, get, cd, settings, hosts
from fabric.contrib import files
from cuisine import dir_ensure

def put_cert(cert):
    dir_ensure('/etc/ssl/certs')
    return put(cert, '/etc/ssl/certs')[0]

def put_key(key):
    dir_ensure('/etc/ssl/private')
    return put(key, '/etc/ssl/private')[0]

def ensure_dhparams(path='/etc/ssl/dhparams.pem', size=2048):
    if not files.exists(path):
        run('openssl dhparam -out "{dhparams}" {size}'.format(dhparams=path, size=size))
