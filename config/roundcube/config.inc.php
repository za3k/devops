<?php

/* Local configuration for Roundcube Webmail */

// ----------------------------------
// SQL DATABASE
// ----------------------------------
// Database connection string (DSN) for read+write operations
// Format (compatible with PEAR MDB2): db_provider://user:password@host/database
// Currently supported db_providers: mysql, pgsql, sqlite, mssql, sqlsrv, oracle
// For examples see http://pear.php.net/manual/en/package.database.mdb2.intro-dsn.php
// NOTE: for SQLite use absolute path (Linux): 'sqlite:////full/path/to/sqlite.db?mode=0646'
//       or (Windows): 'sqlite:///C:/full/path/to/sqlite.db'
$config['db_dsnw'] = 'sqlite:////var/www/roundcube.db?mode=0646';

// ----------------------------------
// LOGGING/DEBUGGING
// ----------------------------------
// system error reporting, sum of: 1 = log; 4 = show
$config['debug_level'] = 5;

// log driver:  'syslog', 'stdout' or 'file'.
$config['log_driver'] = 'syslog';


// -----
// SMTP
// -----

// SMTP server host (for sending mails).
// Enter hostname with prefix tls:// to use STARTTLS, or use
// prefix ssl:// to use the deprecated SSL over SMTP (aka SMTPS)
// Supported replacement variables:
// %h - user's IMAP hostname
// %n - hostname ($_SERVER['SERVER_NAME'])
// %t - hostname without the first part
// %d - domain (http hostname $_SERVER['HTTP_HOST'] without the first part)
// %z - IMAP domain (IMAP hostname without the first part)
// For example %n = mail.domain.tld, %t = domain.tld
$config['smtp_server'] = 'tls://smtp.za3k.com';

// SMTP HELO host
// Hostname to give to the remote server for SMTP 'HELO' or 'EHLO' messages
// Leave this blank and you will get the server variable 'server_name' or
// localhost if that isn't defined.
$config['smtp_helo_host'] = 'za3k.com';

// SMTP username (if required) if you use %u as the username Roundcube
// will use the current username for login
$config['smtp_user'] = '%u';

// SMTP password (if required) if you use %p as the password Roundcube
// will use the current user's password for login
$config['smtp_pass'] = '%p';

// SMTP port (default is 25; use 587 for STARTTLS or 465 for the
// deprecated SSL over SMTP (aka SMTPS))
$config['smtp_port'] = 587;


// ----------------------------------
// IMAP
// ----------------------------------
// The IMAP host chosen to perform the log-in.
// Leave blank to show a textbox at login, give a list of hosts
// to display a pulldown menu or set one host as string.
// To use SSL/TLS connection, enter hostname with prefix ssl:// or tls://
// Supported replacement variables:
// %n - hostname ($_SERVER['SERVER_NAME'])
// %t - hostname without the first part
// %d - domain (http hostname $_SERVER['HTTP_HOST'] without the first part)
// %s - domain name after the '@' from e-mail address provided at login screen
// For example %n = mail.domain.tld, %t = domain.tld
// WARNING: After hostname change update of mail_host column in users table is
//          required to match old user data records with the new host.
$config['default_host'] = 'localhost';

// provide an URL where a user can get support for this Roundcube installation
// PLEASE DO NOT LINK TO THE ROUNDCUBE.NET WEBSITE HERE!
$config['support_url'] = '';

// This key is used for encrypting purposes, like storing of imap password
// in the session. For historical reasons it's called DES_key, but it's used
// with any configured cipher_method (see below).
$config['des_key'] = 'wkqrP4xlsQ98Ogie9BcHg6Sa';

// Name your service. This is displayed on the login screen and in the window title
$config['product_name'] = 'za3k.com webmail';

// Set identities access level:
// 0 - many identities with possibility to edit all params
// 1 - many identities with possibility to edit all params but not email address
// 2 - one identity with possibility to edit all params
// 3 - one identity with possibility to edit all params but not email address
// 4 - one identity with possibility to edit only signature
$config['identities_level'] = 3;

// ----------------------------------
// PLUGINS
// ----------------------------------
// List of active plugins (in plugins/ directory)
$config['plugins'] = array('hide_blockquote', 'managesieve', 'markasjunk', 'autologon');

// store spam messages in this mailbox
// NOTE: Use folder names with namespace prefix (INBOX. on Courier-IMAP)
$config['junk_mbox'] = 'Spam';

// Make use of the built-in spell checker. It is based on GoogieSpell.
$config['enable_spellcheck'] = false;
