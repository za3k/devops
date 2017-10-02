# These servers only listen on HTTPS, redirect HTTP requests
server {
    listen [::]:80;
    server_name    avalanche.za3k.com;
    location ~ /.well-known {
        allow all;
        root /var/www/well-known/avalanche.za3k.com;
    }
    location / {
        return         302 https://$host$request_uri;
    }
}


server {
    listen [::]:443 ssl ipv6only=off;

    server_name avalanche.za3k.com;

    ssl_certificate /etc/ssl/certs/avalanche.za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/avalanche.za3k.com.key;

    location / {
        root /var/www/public;
        index about.html;
        default_type text/plain;
        add_header  X-Robots-Tag "noindex, nofollow, nosnippet, noarchive";
        autoindex     on;
    }
    location /pub {
        root /public;
        index about.html;
        default_type text/plain;
        add_header  X-Robots-Tag "noindex, nofollow, nosnippet, noarchive";
        autoindex     on;
    }
}
