#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import cd, get, local, put, run, settings
from fabric.contrib import files
from cuisine import dir_ensure, dir_exists, group_ensure, group_user_ensure, select_package, user_ensure, package_ensure
import crypto, postgres

def ensure(restore=True):
    ensure_email_contents(restore=True)
    postfix_database_password = crypto.random_password()
    dovecot_database_password = crypto.random_password()
    ensure_database(postfix_password=postfix_database_password,
                    dovecot_password=dovecot_database_password,
                    restore=restore)
    _postfix(postfix_database_password)
    _dovecot(dovecot_database_password)
    _dkim_milter()
    _spamassassin()
    run("systemctl restart opendkim")
    run("systemctl restart postfix")
    run("systemctl restart dovecot")

def ensure_database(postfix_password, dovecot_password, restore):
    postgres.ensure()
    if postgres.db_exists('email'):
      postgres.alter_password('postfix', postfix_password)
      postgres.alter_password('dovecot', dovecot_password)
      return
    postgres.ensure_user('postfix', postfix_password)
    postgres.ensure_user('dovecot', dovecot_password)
    postgres.alter_password('postfix', postfix_password)
    postgres.alter_password('dovecot', dovecot_password)
    
    if restore:
      with settings(user='email', host_string='burn'):
        get('/data/dbs/email/restore.db', '/tmp/email.db')
      postgres.restore('/tmp/email.db')
    else:
      postgres.restore('data/email/empty_email.db')

def ensure_email_contents(restore):
    """Restore the old email database if needed"""
    user_ensure('vmail')
    group_ensure('vmail')
    group_user_ensure('vmail', 'vmail')
    run("usermod -d /var/mail vmail")
    #run('usermod -s /bin/false vmail')
    if not dir_exists('/var/mail/vmail') and restore:
      #with settings(user='email', host_string='burn'):
      #  get('/data/vmail', '/tmp')
      put('/tmp/vmail', '/var/mail')
    run('chown -R vmail:vmail /var/mail/vmail')

def _replace(path, string, replacement):
    """A crappy string replacement function
    
    Doesn't escape things"""
    run("sed -i'' -e s/{}/{}/g {}".format(string, replacement, path)) 

def _postfix(database_password):
    select_package("apt")
    already_installed = package_ensure(["postfix", "postfix-pgsql"]) # On debian will automatically be enabled
    crypto.put_cert('config/certs/smtp.za3k.com.pem')
    crypto.put_key('config/keys/smtp.za3k.com.key')
    crypto.ensure_dhparams('/etc/ssl/dhparams-postfix.pem', size=1024)
    put('config/postfix/main.cf', '/etc/postfix', mode='644')
    put('config/postfix/master.cf', '/etc/postfix', mode='644')
    put('config/postfix/mailname', '/etc', mode='644')
    put('config/postfix/pgsql-virtual-aliases.cf', '/etc/postfix', mode='600')
    put('config/postfix/pgsql-virtual-mailbox.cf', '/etc/postfix', mode='600')
    _replace('/etc/postfix/pgsql-virtual-aliases.cf', 'POSTFIX_DATABASE_PASSWORD', database_password)
    _replace('/etc/postfix/pgsql-virtual-mailbox.cf', 'POSTFIX_DATABASE_PASSWORD', database_password)

def _dovecot(database_password):
    select_package("apt")
    package_ensure(["dovecot-imapd", "dovecot-lmtpd", "dovecot-pgsql", "dovecot-sieve", "dovecot-managesieved"]) # On debian will automatically be enabled
    crypto.put_cert('config/certs/imap.za3k.com.pem')
    crypto.put_key('config/keys/imap.za3k.com.key')
    put('config/dovecot/dovecot.conf', '/etc/dovecot/dovecot.conf', mode='644')
    put('config/dovecot/dovecot-sql.conf', '/etc/dovecot/dovecot-sql.conf', mode='600')
    _replace('/etc/dovecot/dovecot-sql.conf', 'DOVECOT_DATABASE_PASSWORD', database_password)
    dir_ensure("/etc/dovecot/sieve.d")
    run("chown vmail:vmail /etc/dovecot/sieve.d")

def _dkim_milter():
    select_package("apt")
    package_ensure("opendkim", "opendkim-tools")
    put("config/dkim/opendkim.conf", "/etc", mode='644')
    dir_ensure("/etc/opendkim")
    run("chmod 755 /etc/opendkim")
    put("config/dkim/KeyTable", "/etc/opendkim", mode='644')
    put("config/dkim/SigningTable", "/etc/opendkim", mode='644')
    put("config/dkim/TrustedHosts", "/etc/opendkim", mode='644')
    put("config/dkim/opendkim", "/etc/default", mode='644')
    run("mkdir -p /etc/opendkim/keys/za3k.com && chmod 755 /etc/opendkim/keys && chmod 755 /etc/opendkim/keys/za3k.com")
    put("/srv/keys/dkim/za3k.com/default.private", "/etc/opendkim/keys/za3k.com", mode='600')
    put("/srv/keys/dkim/za3k.com/default.txt", "/etc/opendkim/keys/za3k.com", mode='644')
    run("chown opendkim:opendkim -R /etc/opendkim")

def _spamassassin():
    select_package("apt")
    package_ensure(["spamassassin"])
    run("sa-update || true")
    put("config/dovecot/spamassassin.sieve", "/etc/dovecot/sieve.d", mode='644')
    with cd("/etc/dovecot/sieve.d"):
        run("sievec spamassassin.sieve")
    put("config/spamassassin/spamassassin", "/etc/default", mode='644')
    put("config/spamassassin/spamassassin-localspam", "/etc/cron.daily", mode='755')
    put("config/spamassassin/local.cf", "/etc/spamassassin", mode='644')
    run("systemctl restart spamassassin")
