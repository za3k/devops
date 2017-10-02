#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import run, env, sudo, put, get, cd, settings, hosts
from cuisine import dir_ensure, group_ensure, group_user_ensure, mode_sudo, select_package, package_ensure, user_ensure
import crypto, util

def ensure():
    """Ensure nginx is installed"""
    select_package("apt")
    if sudo("which nginx", warn_only=True):
        # Temporary workaround for manual fix because I don't know how to deal with pinned package to get 'gunzip' and 'gzip' on nginx. Hoping to wait until this is the default.
        already_installed = True
    else:
        already_installed = package_ensure(["nginx"]) # On debian will automatically be enabled
    if not already_installed:
        remove_default_sites()
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

def remove_default_sites():
    sudo("rm /etc/nginx/sites-available/default")
    sudo("rm /etc/nginx/sites-enabled/default")

def restart():
    """Restart nginx. Should only be neccesary on ipv[46] switch."""
    if sudo("which systemctl", warn_only=True):
        sudo("systemctl restart nginx")
    else:
        sudo("service nginx restart")

def reload():
    """Reload nginx and apply new configuration"""
    #sudo("systemctl reload nginx")
    sudo("nginx -s reload")

def ensure_site(config_file, cert=None, csr=None, key=None, letsencrypt=False, domain=None, enabled=True):
    assert not (letsencrypt and not enabled) # Online verification won't work
    assert not (letsencrypt and not cert) # As a hack, use an expired cert to bootstrap
    assert not (letsencrypt and not csr) # We've opted to use CSR as the input to acme.sh
    assert not (letsencrypt and not domain) # we can't infer the well-known-path on disk without some extra help
    ensure_sites_available()
    placed_config = put(config_file, '/etc/nginx/sites-available')[0]
    if key is not None:
        crypto.put_key(key)
    if csr is not None:
        remote_csr = crypto.put_csr(csr)
    if cert is not None:
        crypto.put_cert(cert)
    if enabled:
        sudo("ln -s -f {config} /etc/nginx/sites-enabled".format(config=placed_config))
    if letsencrypt:
        import letsencrypt
        reload() # Awkward... we need this to enable a site enough for the well-known path to work
        letsencrypt.add_csr(remote_csr, domain)
        reload() # And allow the key

def ensure_fcgiwrap(children=4):
    select_package("apt")
    package_ensure(["fcgiwrap"]) # On debian will automatically be enabled
    # fcgi can't run status script because its default user (www-data) has no login shell--not sure why exactly but work around it by making a new user
    user_ensure('fcgiwrap', shell="/bin/sh")
    group_ensure('fcgiwrap')
    group_user_ensure('fcgiwrap', 'fcgiwrap')
    
    # Needed because of Debian bug https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=792705. Fastcgi 1.1.0-6 (unstable as of writing) fixes this bug.
    util.put("config/systemd/fcgiwrap.service", "/etc/systemd/system", mode='0644', user='root')
    # Not sure these two lines actually do anything
    sudo('sed -i "s/www-data/fcgiwrap/" /lib/systemd/system/fcgiwrap.service')
    sudo('echo "FCGI_CHILDREN={}" > /etc/default/fcgiwrap'.format(children))

    sudo('systemctl daemon-reload')
    sudo('/etc/init.d/fcgiwrap restart')
