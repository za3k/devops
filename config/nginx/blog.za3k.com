# These servers only listen on HTTPS, redirect HTTP requests
server {
    listen [::]:80;
    server_name    blog.za3k.com;
    location ~ /.well-known {
        allow all;
        root /var/www/well-known/blog.za3k.com;
    }
    location / {
        return         302 https://$host$request_uri;
    }
}

server {
    listen [::]:443 ssl;
    server_name blog.za3k.com;

    ssl_certificate /etc/ssl/certs/blog.za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/blog.za3k.com.key;

    index index.php index.html;
    root /var/www/za3k_blog;
      
    # php
    location /wp-admin {
        auth_basic "wpadmin";
        auth_basic_user_file /etc/wp_basic_auth.conf;
    }
    location ~ /wp-admin/.*php$|wp-login.php$ {
        auth_basic "wpadmin";
        auth_basic_user_file /etc/wp_basic_auth.conf;

        try_files $uri =404;
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        client_max_body_size 28m;

        # With php-fpm:
        fastcgi_pass unix:/var/run/php/php7.3-fpm.sock;
        fastcgi_index index.php;
    }
    location ~ /wp-content.*\.php$ {
        return 403;
    }
    location ~ /xmlrpc.php$ {
        return 403;
    }
    location ~ /xmlrpc.php$ {
        return 403;
    }
    location / {
        try_files $uri $uri/ /index.php?$args;
    }
    location ~ \.php$ {
        try_files $uri =404;
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        client_max_body_size 28m;

        # With php-fpm:
        fastcgi_pass unix:/var/run/php/php7.3-fpm.sock;
        fastcgi_index index.php;
    }
    location /review {
      index index.html index.md;
      alias /var/www/za3k_blog2;
    }

}

