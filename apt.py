#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import run
from cuisine import mode_user, select_package, package_ensure

def sudo_ensure():
    """Ensure the 'sudo' command is installed"""
    select_package("apt")
    with mode_user():
        package_ensure(["sudo"])
