from __future__ import print_function
import sys
sys.dont_write_bytecode = True

from fabric.api import run, env, sudo, put, get, cd, settings, hosts
from fabric.contrib import files
from cuisine import dir_ensure, dir_exists, group_ensure, group_user_ensure, mode_sudo, package_ensure, user_ensure
from StringIO import StringIO
import apt, git, letsencrypt, mx, nginx, node, path, ruby, ssh, supervisord, util, znc

env.shell = '/bin/sh -c'
env.use_ssh_config = True

def avalanche():
    """Avalanche doesn't really run anything except the printserver, it's a point of presence."""

    # Set up the firewall
    put("config/firewalls/avalanche.sh", "/usr/local/bin", use_sudo=True)
    sudo("sh /usr/local/bin/avalanche.sh")
    put("config/firewalls/iptables", "/etc/network/if-pre-up.d/", use_sudo=True, mode='0755')

    # github-backup setup is manual. Look on github and at cron entry. Backs up to burn:/data/github

    # Start a webserver
    already_installed = nginx.ensure()
    if not already_installed:
        nginx.restart() # IPv[46] listener only changes on restart

    letsencrypt.ensure()

    # avalanche.za3k.com
    nginx.ensure_site('config/nginx/avalanche.za3k.com', cert='config/certs/avalanche.za3k.com.pem', key='config/keys/avalanche.za3k.com.key', domain="avalanche.za3k.com", letsencrypt=True, csr="config/certs/avalanche.za3k.com.csr")
    util.put('data/avalanche/public', '/var/www', 'zachary', mode='755')

    nginx.restart()

def burn():
    """Burn is the backup machine and cannot be configured automatically for safety reasons.
    It runs:
        git.za3k.com: HTTPS access for cloning
        burn.za3k.com: SCP access for backups and git commits
                       rsync access for backups and public data
    """
    # Daily
    #    * rsync -rltp "$@" --delete --chmod=D755,F644 /data/archive/tarragon.latest/home/zachary/books/ /data/books
    #    * rsync -rltp "$@" --delete --chmod=D755,F644 /data/archive/tarragon.latest/srv/za3k-db/ /data/dbs/za3k-db
    # gmail backup
    # letsencrypt for git.za3k.com cert
    pass

# fab -H corrupt corrupt
# Run this on Debian 8
def corrupt():
    apt.sudo_ensure() # cuisine.package_ensure is broken otherwise
    with cd("/"): # Hack because /root is -x
        # Set up the firewall
        put("config/firewalls/corrupt.sh", "/usr/local/bin")
        run("sh /usr/local/bin/corrupt.sh")
        put("config/firewalls/iptables", "/etc/network/if-pre-up.d/", use_sudo=True, mode='0755')

        # Set up authorization to back up email to the data server
        public_key = ssh.ensure_key('/var/local/burn-backup')
        with settings(user='zachary', host_string='burn'):
            files.append('/home/corrupt/.ssh/authorized_keys', public_key, use_sudo=True)
        put("config/backup/sshconfig-corrupt", "/root/.ssh/config")

        # Set up backup
        package_ensure(["rsync"])
        put("config/backup/generic-backup.sh", "/var/local", mode='0755')
        put("config/backup/backup-exclude-base", "/var/local/backup-exclude", mode='0644')
        put("config/backup/backup-corrupt.sh", "/etc/cron.daily/backup-corrupt", mode='0755')

        # Set up postgres, postfix, dovecot, spamassassin
        mx.ensure(restore=True)

        # Remind zachary to change their email password

        # Remind zachary to change their DNS records to point to the new MX server
        # Remind zachary to change their rDNS record to point to za3k.com

        # znc.za3k.com
        znc.ensure()

        # Start a webserver
        already_installed = nginx.ensure()
        if not already_installed:
            nginx.restart() # IPv[46] listener only changes on restart

        letsencrypt.ensure()

        # avalanche.za3k.com
        nginx.ensure_site('config/nginx/corrupt.za3k.com', cert='config/certs/corrupt.za3k.com.pem', key='config/keys/corrupt.za3k.com.key', domain="corrupt.za3k.com", letsencrypt=True, csr="config/certs/corrupt.za3k.com.csr")
        util.put('data/corrupt/public', '/var/www', 'root', mode='755')

        nginx.restart()


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
    put("config/firewalls/iptables", "/etc/network/if-pre-up.d/", use_sudo=True, mode='0755')

    # Set up authorization to back up to burn
    public_key = ssh.ensure_key('/var/local/burn-backup', use_sudo=True)
    with settings(user='zachary', host_string='burn'):
        files.append('/home/deadtree/.ssh/authorized_keys', public_key, use_sudo=True)
    util.put("config/backup/sshconfig-deadtree", "/root/.ssh/config", user='root')

    # Set up backup
    package_ensure(["rsync"])
    util.put("config/backup/generic-backup.sh", "/var/local", mode='0755', user='root')
    util.put("config/backup/backup-exclude-base", "/var/local/backup-exclude", mode='0644', user='root')
    util.put("config/backup/backup-deadtree.sh", "/etc/cron.daily/backup-deadtree", mode='0755', user='root')

    # Set up nginx
    already_installed = nginx.ensure()
    nginx.ensure_site('config/nginx/default', cert='config/certs/za3k.com.pem', key='config/keys/blog.za3k.com.key')
    nginx.ensure_fcgiwrap(children=4)
    if not already_installed:
        nginx.restart() # IPv[46] listener only changes on restart

    # Set up letsencrypt
    letsencrypt.ensure() 

    # Set up authorization to back up to the data server
    #public_key = ssh.ensure_key('/root/.ssh/id_rsa')
    #with settings(user='deadtree', host_string='burn'):
    #    #put(public_key, '/home/zachary/test_authorized_keys')
    #    files.append('/home/deadtree/.ssh/authorized_keys', public_key)

    # Set up logging reports
    package_ensure(["analog"])
    with mode_sudo():
        dir_ensure("/var/www/logs", mode=755)
    put("config/logs/generate-logs", "/etc/cron.daily", mode='755', use_sudo=True)
    put("config/logs/analog.cfg", "/etc", mode="644", use_sudo=True)

    # ddns.za3k.com (TCP port 80, web updater for DDNS)
    # ns.za3k.com (UDP port 53, DNS server)
    user_ensure('nsd')
    group_ensure('nsd')
    group_user_ensure('nsd', 'nsd')
    with mode_sudo():
        dir_ensure('/var/lib/nsd', mode='755')
    sudo("chown nsd:nsd /var/lib/nsd")
    package_ensure(["nsd"])
    with cd("/var/lib/nsd"):
        sudo("touch /var/lib/nsd/moreorcs.com.zone && chown nsd:nsd /var/lib/nsd/moreorcs.com.zone")
    node.ensure()
    put("config/ddns/moreorcs.com.zonetemplate", "/etc/nsd", mode='644', use_sudo=True)
    supervisord.ensure()
    git.ensure_clone_github('thingless/ddns', '/var/lib/nsd/ddns', user='nsd')
    supervisord.ensure_config("config/supervisor/ddns.conf")
    put("config/ddns/config.json", "/var/lib/nsd", mode='644', use_sudo=True)
    sudo("chown nsd:nsd /var/lib/nsd/config.json")
    # [Manual] Copy dnsDB.json from backup
    sudo("cd /var/lib/nsd && ln -sf ddns/index.txt index.txt && chown nsd:nsd index.txt")
    supervisord.update() # Run ddns
    package_ensure(["nsd"])
    put("config/ddns/nsd.conf", "/etc/nsd", mode='644', use_sudo=True)
    sudo("systemctl restart nsd")
    nginx.ensure_site('config/nginx/ddns.za3k.com', csr='config/certs/ddns.za3k.com.csr', key='config/keys/ddns.za3k.com.key', domain="ddns.za3k.com", letsencrypt=True, cert="config/certs/ddns.za3k.com.pem")
    nginx.reload()

    # blog.za3k.com
    package_ensure(["php5-fpm", "mysql-server", "php5-mysql"])

    nginx.ensure_site('config/nginx/blog.za3k.com', cert='config/certs/blog.za3k.com.pem', key='config/keys/blog.za3k.com.key', domain="blog.za3k.com", letsencrypt=True, csr="config/certs/blog.za3k.com.csr")

    git.ensure_clone_za3k('za3k_blog', '/var/www/za3k_blog', user='www-data')
    # [Manual] Edit /etc/php5/fpm/php.ini
    # upload_max_filesize = 20M
    # post_max_size = 26M
    # sudo("systemctl reload php5-fpm.service")

    # Yes, www-data and not fcgiwrap
    sudo("chown www-data:www-data -R /var/www/za3k_blog")
    sudo("find . -type d -exec chmod 755 {} \;")
    sudo("find . -type f -exec chmod 644 {} \;")

    # TODO: Replace a database-specific password or make it more obvious it's not used? Currently we're using user ACLs and this gets ignored anyway, I think?
    # [Manual] Load the blog database from backup at /srv/mysql -> /var/lib/mysql
    sudo('systemctl restart mysql')

    # deadtree.za3k.com
    nginx.ensure_site('config/nginx/deadtree.za3k.com', cert='config/certs/deadtree.za3k.com.pem', key='config/keys/deadtree.za3k.com.key', domain="deadtree.za3k.com", letsencrypt=True, csr="config/certs/deadtree.za3k.com.csr")
    util.put('data/deadtree/public', '/var/www', 'zachary', mode='755')

    # etherpad.za3k.com
    package_ensure(["sqlite3"])
    user_ensure('etherpad')
    group_ensure('etherpad')
    group_user_ensure('etherpad', 'etherpad')
    git.ensure_clone_github('ether/etherpad-lite', '/var/www/etherpad', commit='1.6.0', user='etherpad')
    nginx.ensure_site('config/nginx/etherpad.za3k.com', csr='config/certs/etherpad.za3k.com.csr', key='config/keys/etherpad.za3k.com.key', domain="etherpad.za3k.com", letsencrypt=True, cert="config/certs/etherpad.za3k.com.pem")
    util.put("config/etherpad/APIKEY.txt", "/var/www/etherpad", user='etherpad', mode='600')
    util.put("config/etherpad/settings.json", "/var/www/etherpad", user='etherpad', mode='644')
    if not files.exists("/var/www/etherpad/var/sqlite.db"):
        sudo("mkdir -p /var/www/etherpad/var", user='etherpad')
        with cd("/var/www/etherpad"):
            sudo("npm install sqlite3")
        sudo("rsync -av burn.za3k.com::etherpad --delete /var/www/etherpad/var", user='etherpad')
    supervisord.ensure()
    supervisord.ensure_config("config/supervisor/etherpad.conf")
    supervisord.update()

    # forsale
    nginx.ensure_site('config/nginx/forsale')
    util.put('data/forsale', '/var/www', user='nobody', mode='755')

    # gipc daily sync
    # github personal backup
    # github repo list
    put("config/github/github-metadata-sync", "/etc/cron.daily", mode='755', use_sudo=True)

    #                  -> updater
    # irc.za3k.com -> irc
    #              -> webchat (qwebirc)
    # jsfail.com
    user_ensure('jsfail')
    group_ensure('jsfail')
    group_user_ensure('jsfail', 'jsfail')
    nginx.ensure_site('config/nginx/jsfail.com')
    util.put('data/jsfail', '/var/www', 'jsfail', mode='755')

    # library.za3k.com -> website
    #                  -> sync script
    #                  -> card catalog
    # MUST be user 2001 to match remote rsync
    user_ensure('library', uid=2001)
    group_ensure('library', gid=2001)
    group_user_ensure('library', 'library')
    with mode_sudo():
        dir_ensure('/var/www/library', mode='755')
    files.append('/etc/sudoers', 'za3k    ALL=(root) NOPASSWD: /etc/cron.daily/library-sync', use_sudo=True)
    with settings(user='zachary', host_string='burn'):
        actual_key = ssh.get_public_key("/data/git/books.git/hooks/deadtree.library")
    ssh_line = 'command="{command}",no-port-forwarding,no-x11-forwarding,no-agent-forwarding {key}'.format(
        command="sudo /etc/cron.daily/library-sync",
        key=actual_key)
    files.append('/home/za3k/.ssh/authorized_keys', ssh_line, use_sudo=True)

    sudo("chown library:library /var/www/library")
    put("config/library/library-sync", "/etc/cron.daily", mode='755', use_sudo=True)
    sudo("/etc/cron.daily/library-sync")
    nginx.ensure_site('config/nginx/library.za3k.com', csr='config/certs/library.za3k.com.csr', key='config/keys/library.za3k.com.key', domain="library.za3k.com", letsencrypt=True, cert="config/certs/library.za3k.com.pem")

    # logs (nginx) and analysis (analog)
    # mint sync
    # moreorcs.com
    user_ensure('moreorcs')
    group_ensure('moreorcs')
    group_user_ensure('moreorcs', 'moreorcs')
    nginx.ensure_site('config/nginx/moreorcs.com', cert='config/certs/moreorcs.com.pem', key='config/keys/moreorcs.com.key', domain="moreorcs.com", letsencrypt=True, csr="config/certs/moreorcs.com.csr")
    git.ensure_clone_github('za3k/moreorcs', '/var/www/moreorcs', user='moreorcs')

    # nanowrimo.za3k.com
    nginx.ensure_site('config/nginx/nanowrimo.za3k.com', csr='config/certs/nanowrimo.za3k.com.csr', key='config/keys/nanowrimo.za3k.com.key', domain="nanowrimo.za3k.com", letsencrypt=True, cert="config/certs/nanowrimo.za3k.com.pem")
    util.put('data/nanowrimo', '/var/www', user='nobody', mode='755')

    # nntp.za3k.com - Discontinued
    # petchat.za3k.com
    nginx.ensure_site('config/nginx/petchat.za3k.com')
    if not files.exists('/var/www/petchat'):
        git.ensure_clone_za3k('petchat', '/var/www/petchat', user='nobody')

    # publishing.za3k.com
    # thinkingtropes.com
    nginx.ensure_site('config/nginx/thinkingtropes.com')
    util.put('data/thinkingtropes', '/var/www', user='nobody', mode='755')

    # thisisashell.com
    nginx.ensure_site('config/nginx/thisisashell.com', csr='config/certs/thisisashell.com.csr', key='config/keys/thisisashell.com.key', domain="thisisashell.com", letsencrypt=True, cert="config/certs/thisisashell.com.pem")

    # twitter archive
    # za3k.com
    user_ensure('za3k')
    group_ensure('za3k')
    group_user_ensure('za3k', 'za3k')
    nginx.ensure_site('config/nginx/za3k.com', cert='config/certs/za3k.com.pem', key='config/keys/za3k.com.key', domain="za3k.com", letsencrypt=True, csr="config/certs/za3k.com.csr")
    git.ensure_clone_za3k('za3k', '/var/www/za3k', user='za3k')
    with settings(user='zachary', host_string='burn'):
        actual_key = ssh.get_public_key("/data/git/za3k.git/hooks/deadtree_key")
    ssh_line = 'command="{command}",no-port-forwarding,no-x11-forwarding,no-agent-forwarding {key}'.format(
        command="/usr/bin/git -C /var/www/za3k pull",
        key=actual_key)
    files.append('/home/za3k/.ssh/authorized_keys', ssh_line, use_sudo=True)

    # Markdown .md
    ruby.ensure()
    ruby.ensure_gems(["redcarpet"])
    # Databases .view
    package_ensure(["sqlite3"])
    put("config/za3k/za3k-db-sync", "/etc/cron.daily", mode='755', use_sudo=True)
    sudo("/etc/cron.daily/za3k-db-sync")
    # colony on the moon
    sudo("rsync -av burn.za3k.com::colony --delete /var/www/colony", user='nobody')
    # .sc
    package_ensure(["sc"])
    # |-- status.za3k.com
    nginx.ensure_site('config/nginx/status.za3k.com', csr='config/certs/status.za3k.com.csr', key='config/keys/status.za3k.com.key', domain="status.za3k.com", letsencrypt=True, cert="config/certs/status.za3k.com.pem")
    sudo("mkdir -p /var/www/status && chmod 755 /var/www/status")
    util.put("/srv/keys/backup_check", "/var/www/status", user='fcgiwrap', mode='600')
    util.put("/srv/keys/comcast.env", "/etc", user='fcgiwrap', mode='600')
    #util.put("/srv/keys/backup_check.pub", "/var/www/status", user='fcgiwrap', mode='644')
    package_ensure(["parallel", "curl", "python-requests"])
    nginx.reload()

def equilibrate():
    """Equilibrate runs games."""
    # Out of scope: Set up DNS (including poll script), ssh, sudo

    # Set up the firewall
    put("config/firewalls/equilibrate.sh", "/usr/local/bin", use_sudo=True)
    sudo("sh /usr/local/bin/equilibrate.sh")
    put("config/firewalls/iptables", "/etc/network/if-pre-up.d/", use_sudo=True, mode='0755')

    # Set up authorization to back up email to the data server
    public_key = ssh.ensure_key('/var/local/burn-backup', use_sudo=True)
    with settings(user='zachary', host_string='burn'):
        files.append('/home/equilibrate/.ssh/authorized_keys', public_key, use_sudo=True)
    util.put("config/backup/sshconfig-equilibrate", "/root/.ssh/config", user='root')

    # Set up backup
    package_ensure(["rsync"])
    util.put("config/backup/generic-backup.sh", "/var/local", mode='0755', user='root')
    util.put("config/backup/backup-exclude-base", "/var/local/backup-exclude", mode='0644', user='root')
    util.put("config/backup/backup-equilibrate.sh", "/etc/cron.daily/backup-equilibrate", mode='0755', user='root')

def forget():
    """Forget does crawls"""
    # Set up the firewall
    put("config/firewalls/forget.sh", "/usr/local/bin", use_sudo=True)
    sudo("sh /usr/local/bin/forget.sh")
    put("config/firewalls/iptables", "/etc/network/if-pre-up.d/", use_sudo=True, mode='0755')

    # Set up authorization to back up email to the data server
    public_key = ssh.ensure_key('/var/local/forget-backup', use_sudo=True)
    with settings(user='zachary', host_string='burn'):
        files.append('/home/forget/.ssh/authorized_keys', public_key, use_sudo=True)
    util.put("config/backup/sshconfig-forget", "/root/.ssh/config", user='root')

    # Set up backup
    package_ensure(["rsync"])
    util.put("config/backup/generic-backup.sh", "/var/local", mode='0755', user='root')
    util.put("config/backup/backup-exclude-base", "/var/local/backup-exclude", mode='0644', user='root')
    util.put("config/backup/backup-forget.sh", "/etc/cron.daily/backup-equilibrate", mode='0755', user='root')

    # Start a webserver
    already_installed = nginx.ensure()
    if not already_installed:
        nginx.restart() # IPv[46] listener only changes on restart

    letsencrypt.ensure()

    # forget.za3k.com
    nginx.ensure_site('config/nginx/forget.za3k.com', cert='config/certs/forget.za3k.com.pem', key='config/keys/forget.za3k.com.key', domain="forget.za3k.com", letsencrypt=True, csr="config/certs/forget.za3k.com.csr")
    with mode_sudo():
        dir_ensure("/var/www/public", mode=755)
    util.put('data/forget/public', '/var/www', 'zachary', mode='755')

    nginx.restart()

def xenu():
    """Xenu runs minecraft."""
    # Set up the firewall
    put("config/firewalls/xenu.sh", "/usr/local/bin", use_sudo=True)
    sudo("sh /usr/local/bin/xenu.sh")
    put("config/firewalls/iptables", "/etc/network/if-pre-up.d/", use_sudo=True, mode='0755')

    # Set up authorization to back up
    public_key = ssh.ensure_key('/var/local/burn-backup', use_sudo=True)
    with settings(user='xenu-linux', host_string='burn'):
        files.append('/home/xenu-linux/.ssh/authorized_keys', public_key)
    sudo("mkdir -p /root/.ssh")
    util.put("config/backup/sshconfig-xenu", "/root/.ssh/config", user='root')

    # Set up backup
    package_ensure(["rsync"])
    util.put("config/backup/generic-backup.sh", "/var/local", mode='0755', user='root')
    util.put("config/backup/backup-exclude-xenu", "/var/local/backup-exclude", mode='0644', user='root')
    util.put("config/backup/backup-xenu.sh", "/etc/cron.daily/backup-xenu", mode='0755', user='root')

    # Minecraft prereqs
    package_ensure(["make", "tmux"])
    # Set up java for minecraft
    if not path.has('java'):
        sudo('echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | tee /etc/apt/sources.list.d/webupd8team-java.list')
        sudo('echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list')
        sudo('apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886')
        sudo('apt-get update')
        sudo('echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo /usr/bin/debconf-set-selections')
        package_ensure(["oracle-java8-installer"]) # fails

    # Set up nginx
    already_installed = nginx.ensure()
    if not already_installed:
        nginx.restart() # IPv[46] listener only changes on restart
    util.put("data/minecraft-www", "/var/www", user="minecraft")
    nginx.ensure_site('config/nginx/minecraft.za3k.com')
    nginx.reload()
