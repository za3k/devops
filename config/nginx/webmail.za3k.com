# These servers only listen on HTTPS, redirect HTTP requests
server {
    listen [::]:80;
    server_name    webmail.za3k.com;
    location ~ /.well-known {
        allow all;
        root /var/www/well-known/webmail.za3k.com;
    }
    location / {
        return         302 https://$host$request_uri;
    }
}


server {
    listen [::]:443 ssl;
    server_name webmail.za3k.com;

    ssl_certificate /etc/ssl/certs/webmail.za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/webmail.za3k.com.key;

    error_log /var/log/nginx/roundcube.error;
    access_log /var/log/nginx/roundcube.access;

    root /var/www/roundcube;
    auth_basic "http email";
    auth_basic_user_file "conf.d/corrupt.htaccess";
    index index.php index.html index.htm;

    location /login {
      return 301 https://webmail.za3k.com/index.php?_autologin=1;
    }

    location / {
        try_files $uri $uri/ /index.php;
    }

    location ~ ^/(README|INSTALL|LICENSE|CHANGELOG|UPGRADING)$ {
        deny all;
    }
    location ~ ^/(bin|SQL)/ {
        deny all;
    }

    include fastcgi_params;
    fastcgi_param REQUEST_METHOD $request_method;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;

    location ~ \.php$ {
        try_files $uri =404;
        gzip off;
        fastcgi_index index.php;
        fastcgi_pass unix:/var/run/php/php7.2-fpm.sock;
    }
}

