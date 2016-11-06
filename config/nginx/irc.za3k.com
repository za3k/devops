# IRC webapp qwebirc
upstream irc {
    server 127.0.0.1:9012;
}


# These servers only listen on HTTPS, redirect HTTP requests
server {
    listen [::]:80;
    server_name    irc.za3k.com;
    location ~ /.well-known {
        allow all;
        root /var/www/well-known/irc.za3k.com;
    }
    location / {
        return         302 https://$host$request_uri;
    }
}

server {
    listen	       [::]:443 ssl;
    server_name    irc.za3k.com;
    access_log off;

    ssl_certificate /etc/ssl/certs/irc.za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/irc.za3k.com.key;

    location / {
      proxy_pass http://irc;
    } 
}
