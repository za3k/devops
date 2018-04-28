server {
    listen [::]:80;
    server_name    smtp.za3k.com;
    location ~ /.well-known {
        allow all;
        root /var/www/well-known/smtp.za3k.com;
    }
    location / {
        return         404;
    }
}
