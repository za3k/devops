#!/usr/bin/python2
from __future__ import absolute_import
from __future__ import print_function

from fabric.api import put, run, settings, sudo
#from cuisine import file_unlink, select_package, package_ensure
import apt

def ensure():
    select_package("apt")
    already_installed = package_ensure(["postgresql"]) # On debian will automatically be enabled

def dbs():
    command = '''psql -t -c "SELECT datname FROM pg_database WHERE datistemplate = false" | head -n-1 | sed -e "s/^ \+//"'''
    result = sudo(command, shell=True, user='postgres')
    if result.succeeded:
      return result.split("\n")
    return None

def db_exists(db_name):
    return db_name in (dbs() or [])

def restore(local_path):
    put(local_path, "/tmp/db", mode='600')
    run("chown postgres:postgres /tmp/db")
    sudo("psql </tmp/db", user='postgres')
    file_unlink("/tmp/db")
    
def ensure_user(user, password):
    """Does not overwrite password if the user exists"""
    with settings(warn_only=True):
      create_user(user, password) # Can fail

def create_user(user, password):
    run_query("CREATE USER {} WITH ENCRYPTED PASSWORD '{}'".format(user, password))

def alter_password(user, password):
    run_query("ALTER ROLE {} WITH LOGIN ENCRYPTED PASSWORD '{}'".format(user, password))

def ensure_granted(user, database, table):
    pass
    
def ensure_db(database, owner=None):
    with settings(warn_only=True):
      create_database(database, owner=owner) # Can fail

def create_database(database, owner=None):
    if owner is None:
      run_query("CREATE DATABASE {}")
    else:
      run_query("CREATE DATABASE {} WITH OWNER {}".format(database, owner))

def run_query(query, user='postgres'):
    sudo('psql -c "{}"'.format(query), user=user)

def ensure_backups():
    """This only puts the database backups in a more accessible location, we still need a main backup system"""
    put('config/postgres/pg_backup', '/etc/cron.daily', mode='755')
