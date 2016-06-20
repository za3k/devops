#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import run, env, sudo, put, get, cd, settings, hosts
from cuisine import dir_ensure, group_ensure, group_user_ensure, mode_sudo, select_package, package_ensure, user_ensure
import crypto

def ensure():
    """Ensure nginx is installed"""
    select_package("apt")
    already_installed = package_ensure(["nginx"]) # On debian will automatically be enabled
    ensure_sites_available()
    put('config/nginx/nginx.conf', '/etc/nginx', use_sudo=True)
    put('config/nginx/fastcgi_params', '/etc/nginx', use_sudo=True)
    crypto.ensure_dhparams('/etc/ssl/dhparams-nginx.pem')
    with mode_sudo():
        dir_ensure("/var/www", mode='1777') # make sure anyone can add a site
    return already_installed

def ensure_sites_available():
    with mode_sudo():
        dir_ensure('/etc/nginx/sites-available', mode='1777') # make sure anyone can add a site
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
        sudo("ln -s -f {config} /etc/nginx/sites-enabled".format(config=placed_config))

def ensure_fcgiwrap(children=4):
    select_package("apt")
    package_ensure(["fcgiwrap"]) # On debian will automatically be enabled
    # fcgi can't run status script because its default user (www-data) has no login shell--not sure why exactly but work around it by making a new user
    user_ensure('fcgiwrap')
    group_ensure('fcgiwrap')
    group_user_ensure('fcgiwrap', 'fcgiwrap')
    sudo('sed -i "s/www-data/fcgiwrap/" /lib/systemd/system/fcgiwrap.service')
    sudo('echo "FCGI_CHILDREN={}" > /etc/default/fcgiwrap'.format(children))
    sudo('/etc/init.d/fcgiwrap restart')
