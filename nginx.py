#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import run, env, sudo, put, get, cd, settings, hosts
from cuisine import dir_ensure, select_package, package_ensure
import crypto

def ensure():
    select_package("apt")
    package_ensure(["nginx"]) # On debian will automatically be enabled
    ensure_sites_available()
    put('config/nginx/nginx.conf', '/etc/nginx/nginx.conf')
    crypto.ensure_dhparams('/etc/ssl/dhparams-nginx.pem', size=4096)

def ensure_sites_available():
    dir_ensure('/etc/nginx/sites-available')
    dir_ensure('/etc/nginx/sites-enabled')

def restart():
    sudo("systemctl restart nginx")

def reload():
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

def ensure_default():
    ensure_site('config/nginx/default', cert='config/certs/za3k.com.pem', key='config/keys/blog.za3k.com.key')
