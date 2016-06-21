# These servers only listen on HTTPS, redirect HTTP requests
server {
    listen [::]:80;
    server_name    blog.za3k.com;
    return         302 https://$host$request_uri;
}

server {
    listen [::]:443 ssl;
    server_name blog.za3k.com;

    ssl_certificate /etc/ssl/certs/blog.za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/blog.za3k.com.key;

    index index.php index.html;
    root /var/www/za3k_blog;
      
    # php
    location / {
        try_files $uri $uri/ /index.php?$args;
    }
    location ~ \.php$ {
        try_files $uri =404;
        fastcgi_split_path_info ^(.+\.php)(/.+)$;

        # With php5-fpm:
        fastcgi_pass unix:/var/run/php5-fpm.sock;
        fastcgi_index index.php;
    }
}

