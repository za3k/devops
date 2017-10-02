#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function
from fabric.api import run, env, sudo, put, get, cd, settings, hosts
from fabric.contrib import files
from cuisine import dir_ensure, group_ensure, group_user_ensure, user_ensure
import crypto
import path, git, util

well_known_base = '/var/www/well-known'

def _reload_nginx():
    return "/usr/sbin/nginx -s reload"

def ensure():
    git.ensure_git()
    # Make sure the user exists
    user_ensure('acme')
    group_ensure('acme')
    group_user_ensure('acme', 'acme')

    # Allow the acme user to reload nginx when updating certs
    files.append('/etc/sudoers', 'acme    ALL=(root) NOPASSWD: {reload_nginx}'.format(reload_nginx=_reload_nginx()), use_sudo=True)

    # Make sure acme.sh is installed for the acme user
    if not path.has('acme.sh', user='acme'):
        git.ensure_clone_github('Neilpang/acme.sh', '/home/acme/acme.sh', user='acme')
        with cd("/home/acme/acme.sh"):
            sudo("./acme.sh --install", user='acme')
    dir_ensure(well_known_base)
    sudo("chown acme:acme {well_known} && chmod 755 {well_known}".format(well_known=well_known_base)) # Can't change attributes without sudo in a sticky (not write) directory... annoying
    util.put("config/certs/lets-encrypt-x3-cross-signed.pem", "/etc/ssl/certs", user='root', mode='0644')

def add_csr(path, domain):
    well_known = well_known_base + '/' + domain
    sudo("mkdir -p {well_known} && chmod 755 {well_known}".format(well_known=well_known), user='acme')
    with cd("/home/acme"):
        with settings(warn_only=True):
            sudo(".acme.sh/acme.sh --signcsr --csr {path} -w {well_known}".format(path=path, well_known=well_known), user='acme')
        sudo("chown acme:acme /etc/ssl/certs/{domain}.pem".format(domain=domain))
        sudo(".acme.sh/acme.sh --installcert -d {domain} --certpath /etc/ssl/certs/{domain}.letsencrypt.pem --fullchainpath /etc/ssl/certs/{domain}.pem --renew-hook '{reload_nginx}'".format(path=path, domain=domain, reload_nginx=_reload_nginx()), user='acme')
        #sudo("cat /etc/ssl/certs/{domain}.letsencrypt.pem /etc/ssl/certs/lets-encrypt-x3-cross-signed.pem >/etc/ssl/certs/{domain}.pem".format(path=path, domain=domain), user='acme')
    return '/etc/ssl/certs/{domain}.key'.format(domain=domain)
