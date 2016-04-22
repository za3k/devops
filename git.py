#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import run, env, sudo, put, get, cd, settings, hosts
from cuisine import dir_ensure, select_package, package_ensure

def ensure_git():
    select_package("apt")
    already_installed = package_ensure(["git"])

def clone_github(target, repository, use_https=True):
    if use_https:
        remote="https://github.com/{repository}.git".format(repository=repository)
    else:
        remote="git@github.com:{repository}.git".format(repository=repository)
    clone(target, remote)

def clone_deadtree(target, repository, use_https=True):
    if use_https:
        remote="https://git.za3k.com/{repository}.git".format(repository=repository)
    else:
        remote="deadtree.xen.prgmr.com:/git/{repository}.git".format(repository=repository)
    clone(target, remote)

def clone(target, remote):
    ensure()
    run('git clone "{remote}" "{target}"'.format(target=target, remote=remote))

def canonical_location(name):
    dir_ensure("/source", mode='1755')
    return "/source/{name}".format(name=name)
