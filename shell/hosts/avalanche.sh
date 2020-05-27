#!/bin/sh
export HOST=avalanche
export USER=root
. lib/main.sh
. lib/logs.sh
. lib/debian.sh
. lib/ssh.sh
#. nginx.lib.sh
#. letsencrypt.lib.sh

set -ex

debian_ensure_sudo

logs_setup

# Firewall
put_file "config/firewalls/avalanche.sh" "/usr/local/bin/avalanche.sh" '755'
run      "sh /usr/local/bin/avalanche.sh"
put_file "config/firewalls/iptables" "/etc/network/if-pre-up.d/ip_tables" '755'
put_file "config/backup/backup-avalanche.sh" "/etc/cron.daily/backup-avalanche" '755'

# Set up authorization for backup avalanche -> germinate
ssh_ensure_key '/var/local/germinate-backup'
HOST=germinate USER=avalanche append_public_key '/home/avalanche/.ssh/authorized_keys' $PUBLIC_KEY
put_file "config/backup/sshconfig-avalanche" "/root/.ssh/config" '600'
# Set up backup avalanche -> germinate
debian_package rsync
put_file "config/backup/generic-backup.sh" "/var/local/generic-backup.sh" '755'
put_file "config/backup/backup-exclude-avalanche" "/var/local/backup-exclude" '644'
put_file "config/backup/backup-avalanche.sh" "/etc/cron.daily/backup-avalanche" '755'
# github-backup setup is manual. Look on github and at cron entry. Backs up to germinate:/data/github

# Start a webserver
if nginx_ensure; then
    nginx_remove_default_sites
    nginx_restart # IPv[46] listener only changes on restart
else
    nginx_remove_default_sites
fi
letsencrypt_ensure

# avalanche.za3k.com
#nginx.ensure_site('config/nginx/avalanche.za3k.com', cert='config/certs/avalanche.za3k.com.pem', key='config/keys/avalanche.za3k.com.key', domain="avalanche.za3k.com", letsencrypt=True, csr="config/certs/avalanche.za3k.com.csr")
#util.put_dir('data/avalanche/public', '/var/www/public', mode='755', user='zachary')

#nginx.restart()
