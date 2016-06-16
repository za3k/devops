#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import cd, run, env, sudo, put, get, cd, settings, hosts
from fabric.contrib import files
from cuisine import dir_ensure, select_package, package_ensure

def ensure_git():
    select_package("apt")
    already_installed = package_ensure(["git"])

def ensure_clone(remote, target):
    if files.exists(target):
        with cd(target):
            run('git pull')
    else:
        clone(remote, target)

def ensure_clone_github(repository, target, use_https=True):
    if use_https:
        remote="https://github.com/{repository}.git".format(repository=repository)
    else:
        remote="git@github.com:{repository}.git".format(repository=repository)
    ensure_clone(remote, target)

def ensure_clone_za3k(repository, target, use_https=True):
    if use_https:
        remote="https://git.za3k.com/{repository}.git".format(repository=repository)
    else:
        remote="deadtree.xen.prgmr.com:/git/{repository}.git".format(repository=repository)
    ensure_clone(remote, target)

def clone(remote, target):
    run('git clone "{remote}" "{target}"'.format(remote=remote, target=target))

def canonical_location(name):
    dir_ensure("/source", mode='1755')
    return "/source/{name}".format(name=name)
