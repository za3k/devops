#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import run, env, sudo, put, get, cd, settings, hosts
from cuisine import dir_ensure, select_package, package_ensure
import crypto

def ensure():
    """Ensure nginx is installed"""
    select_package("apt")
    already_installed = package_ensure(["nginx"]) # On debian will automatically be enabled
    ensure_sites_available()
    put('config/nginx/nginx.conf', '/etc/nginx/nginx.conf')
    crypto.ensure_dhparams('/etc/ssl/dhparams-nginx.pem', size=4096)
    dir_ensure("/usr/share/nginx", mode='1755') # make sure anyone can add a site
    return already_installed

def ensure_sites_available():
    dir_ensure('/etc/nginx/sites-available')
    dir_ensure('/etc/nginx/sites-enabled')

def restart():
    """Restart nginx. Should only be neccesary on ipv[46] switch."""
    sudo("systemctl restart nginx")

def reload():
    """Reload nginx and apply new configuration"""
    sudo("systemctl reload nginx")

def ensure_site(config_file, cert=None, key=None, enabled=True):
    ensure_sites_available()
    placed_config = put(config_file, '/etc/nginx/sites-available')[0]
    if cert is not None:
        crypto.put_cert(cert)
    if key is not None:
        crypto.put_key(key)
    if enabled:
        run("ln -s -f {config} /etc/nginx/sites-enabled".format(config=placed_config))
