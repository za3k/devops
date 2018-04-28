server {
    listen [::]:80;
    server_name    imap.za3k.com;
    location ~ /.well-known {
        allow all;
        root /var/www/well-known/imap.za3k.com;
    }
    location / {
        return         404;
    }
}
