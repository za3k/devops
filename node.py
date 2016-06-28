#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from cuisine import package_ensure
from fabric.api import cd, run, settings, sudo

def ensure():
    with settings(warn_only=True):
        result = run("which node")
        if result.return_code == 0:
            return
    with cd("/tmp"):
        run("wget https://nodejs.org/dist/latest-v6.x/node-v6.2.2.tar.gz")
        run("tar -xvzf node-v6.2.2.tar.gz")
        with cd("/tmp/node-v6.2.2"):
            run("./configure")
            run("make")
            sudo("make install")
