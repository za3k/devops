# These servers only listen on HTTPS, redirect HTTP requests
server {
    listen [::]:80;
    server_name    status.za3k.com;
    location ~ /.well-known {
        allow all;
        root /var/www/well-known/status.za3k.com;
    }
    location / {
        return         302 https://$host$request_uri;
    }
}

server {
    listen [::]:443;
    server_name    status.za3k.com;

    ssl_certificate /etc/ssl/certs/status.za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/status.za3k.com.key;
    location / {
        root /var/www/public/pub/status/;
        index mon.txt;
        default_type text/plain;
        charset UTF-8; 

        add_header Refresh "60; url=$scheme://$host$request_uri";
    }
}
