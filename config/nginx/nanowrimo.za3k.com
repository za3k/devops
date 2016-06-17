# These servers only listen on HTTPS, redirect HTTP requests
server {
    listen [::]:80;
    server_name    nanowrimo.za3k.com;
    return         302 https://$host$request_uri;
}

server {
    listen [::]:443 ssl;
    server_name nanowrimo.za3k.com;

    ssl_certificate /etc/ssl/certs/nanowrimo.za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/nanowrimo.za3k.com.key;

    location / {
        root   /var/www/nanowrimo;
    }
}
