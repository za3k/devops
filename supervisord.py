#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

#from cuisine import package_ensure
from fabric.api import sudo, put

def ensure():
    package_ensure("supervisor")

def ensure_config(path):
    package_ensure("supervisor")
    put(path, "/etc/supervisor/conf.d", mode='644', use_sudo=True)

def update():
    sudo("supervisorctl update")
