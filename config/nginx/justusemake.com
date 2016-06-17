# These servers only listen on HTTPS, redirect HTTP requests
server {
    listen [::]:80;
    server_name    justusemake.com;
    return         302 https://$host$request_uri;
}

server {
    listen [::]:443 ssl;
    server_name justusemake.com;

    ssl_certificate /etc/ssl/certs/justusemake.com.pem;
    ssl_certificate_key /etc/ssl/private/justusemake.com.key;

    location / {
        root   /var/www/justusemake;
    }
}
