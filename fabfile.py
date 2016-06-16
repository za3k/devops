#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import run, env, sudo, put, get, cd, settings, hosts
from fabric.contrib import files
from cuisine import dir_ensure, dir_exists, group_ensure, group_user_ensure, mode_sudo, user_ensure
import apt, git, mx, nginx, ssh

env.shell = '/bin/sh -c'
env.use_ssh_config = True

# fab -H corrupt corrupt
# Run this on Debian 8
def corrupt():
    apt.sudo_ensure() # cuisine.package_ensure is broken otherwise
    with cd("/"): # Hack because /root is -x

        # Set up authorization to back up email to the data server
        public_key = ssh.ensure_key('/root/.ssh/id_rsa')
        with settings(user='email', host_string='burn'):
            files.append('/home/email/.ssh/authorized_keys', public_key)

        # Set up postgres, postfix, dovecot, spamassassin
        mx.ensure(restore=True)

        # Remind zachary to change their email password

        # Remind zachary to change their DNS records to point to the new MX server


# fab -H deadtree
# Run this on Debian 8
def deadtree():
    apt.sudo_ensure() # cuisine.package_ensure is broken otherwise
    
    # Set up /etc/skel
    sudo("mkdir /etc/skel/.ssh || true")
    sudo("chmod 700 /etc/skel/.ssh")

    # Set up nginx
    already_installed = nginx.ensure()
    nginx.ensure_site('config/nginx/default', cert='config/certs/za3k.com.pem', key='config/keys/blog.za3k.com.key')
    #nginx.ensure_fastcgi()
    #nginx.ensure_php5 cgi
    if not already_installed:
        nginx.restart() # IPv[46] listener only changes on restart

    # Set up authorization to back up to the data server
    #public_key = ssh.ensure_key('/root/.ssh/id_rsa')
    #with settings(user='deadtree', host_string='burn'):
    #    #put(public_key, '/home/zachary/test_authorized_keys')
    #    files.append('/home/deadtree/.ssh/authorized_keys', public_key)

    # Load git repos, and if we're not the authority, pull
    # blog.za3k.com
    # colony on the moon
    # email -> imap (dovecot)
    #       -> smtp (postfix)
    #       -> spamassassin
    #       -> postgres
    # etherpad.za3k.com
    # forsale
    # gipc daily sync
    # github personal backup
    # github repo list
    #                  -> updater
    # gmail backup
    # irc.za3k.com -> irc
    #              -> webchat (qwebirc)
    # jsfail.com
    user_ensure('jsfail')
    group_ensure('jsfail')
    group_user_ensure('jsfail', 'jsfail')
    nginx.ensure_site('config/nginx/jsfail.com')
    put('data/jsfail', '/var/www', mode='755', use_sudo=True)
    sudo('chown -R jsfail:jsfail /var/www/jsfail')

    # justusemake.com
    # library.za3k.com -> website
    #                  -> sync script
    #                  -> card catalog
    # logs (nginx) and analysis (analog)
    # mint sync
    # moreorcs.com
    user_ensure('moreorcs')
    group_ensure('moreorcs')
    group_user_ensure('moreorcs', 'moreorcs')
    nginx.ensure_site('config/nginx/default', cert='config/certs/za3k.com.pem', key='config/keys/blog.za3k.com.key')
    nginx.ensure_site('config/nginx/moreorcs.com', cert='config/certs/moreorcs.com.pem', key='config/keys/moreorcs.com.key')
    put("~/.ssh/id_rsa.pub", "/home/moreorcs/.ssh/authorized_keys", use_sudo=True)
    sudo("chown moreorcs:moreorcs /home/moreorcs/.ssh/authorized_keys")
    with settings(user='moreorcs'):
        git.ensure_clone_github('za3k/moreorcs', '/var/www/moreorcs')
    sudo('chown -R moreorcs:moreorcs /var/www/moreorcs')

    # nanowrimo.za3k.com
    # nntp.za3k.com
    # petchat.za3k.com
    # publishing.za3k.com
    # redis.za3k.com -> redis [disabled]
    #                -> webdis
    # status.za3k.com
    # thinkingtropes.com [disabled]
    # thisisashell.com [disabled]
    # twitter archive
    # vlad the remailer [disabled]
    # za3k.com
    # znc
    nginx.reload()
