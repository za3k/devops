#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import run, env, sudo, put, get, cd, settings, hosts
from cuisine import dir_ensure, select_package, package_ensure

def ensure():
    """Ensure npm is installed"""
    select_package("apt")
    package_ensure(["npm"])

def ensure_package(package, version=None, local=True):
    """Ensure npm packages are installed"""
    if isinstance(package, basestring):
        package = package.split()
    res = {}
    for p in package:
        p = p.strip()
        if not p: continue
        if local:
            res[p] = ensure_package_local(package, version=version)
        else:
            res[p] = ensure_package_global(package, version=version)
    if len(res) == 1:
        return res.values()[0]
    else:
        return res

def ensure_package_local(package, version=None):
    """Ensure npm packages are installed"""
    status = run('npm --depth 0 ls {package} | tail -n+2 | head -n1 | grep {package} && echo OK')
    if not status.endswith("OK"): # Install
        run("npm install {package}".format(package=p))
        return True
    else: # Update
        if version is not None:
            run("npm install {package}@{version}".format(package=p, version=version))
        return False

def ensure_package_global(package, version=None):
    """Ensure npm packages are installed"""
    status = run('npm --depth 0 --global ls {package} | tail -n+2 | head -n1 | grep {package} && echo OK')
    if not status.endswith("OK"): # Install
        sudo("npm install -g {package}".format(package=p))
        return True
    else: # Update
        if version is not None:
            sudo("npm install -g {package}@{version}".format(package=p, version=version))
        return False
