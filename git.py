#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import cd, run, env, sudo, put, get, cd, settings, hosts
from fabric.contrib import files
from cuisine import dir_ensure, select_package, package_ensure

def runorsuch(*args, **kwargs):
    user = kwargs.get("user", None)
    if user is None:
        del kwargs["user"]
        run(*args, **kwargs)
    else:
        sudo(*args, **kwargs)

def ensure_git():
    select_package("apt")
    already_installed = package_ensure(["git"])

def ensure_clone(remote, target, user=None):
    if files.exists(target):
        with cd(target):
            runorsuch('git pull', user=user)
    else:
        clone(remote, target, user=user)

def ensure_clone_github(repository, target, user=None, use_https=True):
    if use_https:
        remote="https://github.com/{repository}.git".format(repository=repository)
    else:
        remote="git@github.com:{repository}.git".format(repository=repository)
    ensure_clone(remote, target, user=user)

def ensure_clone_za3k(repository, target, user=None, use_https=True):
    if use_https:
        remote="https://git.za3k.com/{repository}.git".format(repository=repository)
    else:
        remote="deadtree.xen.prgmr.com:/git/{repository}.git".format(repository=repository)
    ensure_clone(remote, target, user=user)

def clone(remote, target, user=None):
    runorsuch('git clone "{remote}" "{target}"'.format(remote=remote, target=target), user=user)

def canonical_location(name):
    dir_ensure("/source", mode='1755')
    return "/source/{name}".format(name=name)
