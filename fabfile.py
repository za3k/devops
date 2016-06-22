#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import run, env, sudo, put, get, cd, settings, hosts
from fabric.contrib import files
from cuisine import dir_ensure, dir_exists, group_ensure, group_user_ensure, mode_sudo, package_ensure, user_ensure
from StringIO import StringIO
import apt, git, mx, nginx, ruby, ssh, util

env.shell = '/bin/sh -c'
env.use_ssh_config = True

def avalanche():
    """Avalanche doesn't really run anything except the printserver, it's a point of presence."""

    # Set up the firewall
    put("config/firewalls/avalanche.sh", "/usr/local/bin", use_sudo=True)
    sudo("sh /usr/local/bin/avalanche.sh")

    pass

def burn():
    """Burn is the backup machine and cannot be configured automatically for safety reasons.
    It runs:
        git.za3k.com: HTTPS access for cloning
        burn.za3k.com: SCP access for backups and git commits
    """
    # Daily
    #    * rsync -rltp "$@" --delete --chmod=D755,F644 /data/archive/tarragon.latest/home/zachary/books/ /data/books
    pass

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
    """Deadtree is the main services machine. It can be taken down at any time and rebuilt."""
    apt.sudo_ensure() # cuisine.package_ensure is broken otherwise
    
    # Set up /etc/skel
    sudo("mkdir /etc/skel/.ssh || true")
    sudo("chmod 700 /etc/skel/.ssh")

    # Add a 'nobody' user
    user_ensure('nobody')
    group_ensure('nobody')
    group_user_ensure('nobody', 'nobody')
    sudo('usermod -s /bin/false nobody')

    # Set up the firewall
    put("config/firewalls/deadtree.sh", "/usr/local/bin", use_sudo=True)
    sudo("sh /usr/local/bin/deadtree.sh")

    # Set up nginx
    already_installed = nginx.ensure()
    nginx.ensure_site('config/nginx/default', cert='config/certs/za3k.com.pem', key='config/keys/blog.za3k.com.key')
    nginx.ensure_fcgiwrap(children=4)
    if not already_installed:
        nginx.restart() # IPv[46] listener only changes on restart

    # Set up authorization to back up to the data server
    #public_key = ssh.ensure_key('/root/.ssh/id_rsa')
    #with settings(user='deadtree', host_string='burn'):
    #    #put(public_key, '/home/zachary/test_authorized_keys')
    #    files.append('/home/deadtree/.ssh/authorized_keys', public_key)

    # blog.za3k.com
    package_ensure(["php5-fpm", "mysql-server", "php5-mysql"])

    nginx.ensure_site('config/nginx/blog.za3k.com', cert='config/certs/blog.za3k.com.pem', key='config/keys/blog.za3k.com.key')
    git.ensure_clone_za3k('za3k_blog', '/var/www/za3k_blog', user='fcgiwrap')
    # Replace a database-specific password or make it more obvious it's not used? Currently we're using user ACLs and this gets ignored anyway
    # Load the blog database from backup at /srv/mysql -> /var/lib/mysql [MANUAL]
    sudo('systemctl restart mysql')

    # colony on the moon
    # email -> imap (dovecot)
    #       -> smtp (postfix)
    #       -> spamassassin
    #       -> postgres
    # etherpad.za3k.com
    # forsale
    nginx.ensure_site('config/nginx/forsale')
    put('data/forsale', '/var/www', mode='755', use_sudo=True)
    sudo('chown -R nobody:nobody /var/www/forsale')

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
    util.put('data/jsfail', '/var/www', 'jsfail', mode='755')

    # justusemake.com
    nginx.ensure_site('config/nginx/justusemake.com', cert='config/certs/justusemake.com.pem', key='config/keys/justusemake.com.key')
    put('data/justusemake', '/var/www', mode='755', use_sudo=True)
    sudo('chown -R nobody:nobody /var/www/justusemake')

    # library.za3k.com -> website
    #                  -> sync script
    #                  -> card catalog
    user_ensure('library')
    group_ensure('library')
    group_user_ensure('library', 'library')
    with mode_sudo():
        dir_ensure('/var/www/library', mode='755')
    sudo("chown library:library /var/www/library")
    put("config/library/library.sync", "/etc/cron.daily", mode='755', use_sudo=True)
    sudo("/etc/cron.daily/library.sync")
    nginx.ensure_site('config/nginx/library.za3k.com', cert='config/certs/library.za3k.com.pem', key='config/keys/library.za3k.com.key')

    # logs (nginx) and analysis (analog)
    # mint sync
    # moreorcs.com
    user_ensure('moreorcs')
    group_ensure('moreorcs')
    group_user_ensure('moreorcs', 'moreorcs')
    nginx.ensure_site('config/nginx/moreorcs.com', cert='config/certs/moreorcs.com.pem', key='config/keys/moreorcs.com.key')
    git.ensure_clone_github('za3k/moreorcs', '/var/www/moreorcs', user='moreorcs')

    # nanowrimo.za3k.com
    nginx.ensure_site('config/nginx/nanowrimo.za3k.com', cert='config/certs/nanowrimo.za3k.com.pem', key='config/keys/nanowrimo.za3k.com.key')
    util.put('data/nanowrimo', '/var/www', user='nobody', mode='755')

    # nntp.za3k.com
    # petchat.za3k.com
    nginx.ensure_site('config/nginx/petchat.za3k.com')
    if not files.exists('/var/www/petchat'):
        git.ensure_clone_za3k('petchat', '/var/www/petchat', user='nobody')

    # publishing.za3k.com
    # redis.za3k.com -> redis [disabled]
    #                -> webdis
    # status.za3k.com
    # thinkingtropes.com
    nginx.ensure_site('config/nginx/thinkingtropes.com')
    util.put('data/thinkingtropes', '/var/www', user='nobody', mode='755')

    # thisisashell.com [disabled]
    # twitter archive
    # vlad the remailer [disabled]
    # za3k.com
    user_ensure('za3k')
    group_ensure('za3k')
    group_user_ensure('za3k', 'za3k')
    nginx.ensure_site('config/nginx/za3k.com', cert='config/certs/za3k.com.pem', key='config/keys/za3k.com.key')
    git.ensure_clone_za3k('za3k', '/var/www/za3k', user='za3k')
    # Markdown .md
    ruby.ensure()
    ruby.ensure_gems(["redcarpet"])
    # Status page
    package_ensure(["parallel", "curl"])

    # znc
    nginx.reload()
