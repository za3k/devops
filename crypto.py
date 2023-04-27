#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import run, sudo
from fabric.contrib import files
#from cuisine import dir_ensure, group_ensure, mode_sudo
import random, string, util

def put_csr(csr, user='root'):
    with mode_sudo():
        dir_ensure('/etc/ssl/csr', mode='1777')
    csr_name = csr.split("/")[-1]
    return util.put_file(csr, '/etc/ssl/csr/'+csr_name, mode='0644', user=user)[0]

def put_cert(cert, user='root'):
    with mode_sudo():
        dir_ensure('/etc/ssl/certs', mode='1777')
    if user is None:
        user = 'root'
    cert_name = cert.split("/")[-1]
    return util.put_file(cert, '/etc/ssl/certs/'+cert_name, mode='0644', user=user)[0]

def put_key(key, user='root'):
    with mode_sudo():
        dir_ensure('/etc/ssl/private', mode='1777')
    key_name = key.split("/")[-1]
    return util.put_file(key, '/etc/ssl/private/'+key_name, mode='0640', user=user)[0]

def ensure_dhparams(path='/etc/ssl/dhparams.pem', size=2048):
    if not files.exists(path):
        sudo('openssl dhparam -out "{dhparams}" {size}'.format(dhparams=path, size=size))

def random_password(size=16, valid_characters=(string.ascii_letters + string.digits)):
    return ''.join(random.choice(valid_characters) for _ in range(size))

