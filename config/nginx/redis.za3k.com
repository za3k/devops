# HTTP redis access
upstream redis {
    server 127.0.0.1:9010;
}

# These servers only listen on HTTPS, redirect HTTP requests
server {
    listen [::]:80;
    server_name    redis.za3k.com;
    return         302 https://$host$request_uri;
}

server {
    listen [::]:443 ssl;
    server_name redis.za3k.com;

    ssl_certificate /etc/ssl/certs/redis.za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/redis.za3k.com.key;

    location / {
        proxy_pass http://redis;
    }
}
