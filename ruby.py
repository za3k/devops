from __future__ import absolute_import
from __future__ import print_function

from fabric.api import sudo
from cuisine import select_package, package_ensure

def ensure():
    select_package("apt")
    already_installed = package_ensure(["ruby", "ruby-dev"]) # On debian will automatically be enabled

def ensure_gems(gems):
    for gem in gems:
        sudo("gem install {} --conservative".format(gem))
