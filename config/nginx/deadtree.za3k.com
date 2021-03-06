# These servers only listen on HTTPS, redirect HTTP requests
server {
    listen [::]:80;
    server_name    deadtree.za3k.com;
    location ~ /.well-known {
        allow all;
        root /var/www/well-known/deadtree.za3k.com;
    }
    location / {
        return         302 https://$host$request_uri;
    }
}


server {
    listen [::]:443 ssl;
    server_name deadtree.za3k.com;

    ssl_certificate /etc/ssl/certs/deadtree.za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/deadtree.za3k.com.key;

    location / {
    root /var/www/public;
    index about.html;
    default_type text/plain;
    autoindex     on;
    }
}
