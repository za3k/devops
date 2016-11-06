# Dead Tree Publishing
upstream publishing {
    server 127.0.0.1:9007;
}

# These servers only listen on HTTPS, redirect HTTP requests
server {
    listen [::]:80;
    server_name    publishing.za3k.com;
    location ~ /.well-known {
        allow all;
        root /var/www/well-known/publishing.za3k.com;
    }
    location / {
        return         302 https://$host$request_uri;
    }
}

server {
    listen [::]:443 ssl;
    server_name publishing.za3k.com;

    ssl_certificate /etc/ssl/certs/publishing.za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/publishing.za3k.com.key;

    client_max_body_size 500M;
    proxy_read_timeout 10m;
    proxy_send_timeout 10m;
    send_timeout 10m;

    location / {
      proxy_pass http://publishing;
    }
}
