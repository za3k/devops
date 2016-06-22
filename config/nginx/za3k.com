# Same but these will only EVER listen on HTTPS (cannot be changed, 301 is designed to be cached forever)
server {
    listen [::]:80;
    server_name    za3k.com;
    return         301 https://$host$request_uri;
}
    
server {
    listen [::]:80;
    server_name status.za3k.com;
    return         301 https://za3k.com/service.status;
}

server {
    listen [::]:443 ssl;
    server_name za3k.com;

    ssl_certificate /etc/ssl/certs/za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/za3k.com.key;

    add_header Strict-Transport-Security "max-age=315360000"; # HSTS

    index index.html index.md;
    root /var/www/za3k;

    #location /github {
    #    alias /var/www/github;
    #    gzip on;
    #    gunzip on; # Enables use of .gz files in directory
    #}
    location /~colony {
        alias /var/www/colony;
        autoindex on;
    }
    location /~logs {
        alias /var/www/logs;
        autoindex on;
    }
    location /~twitter_archive {
        alias /var/www/twitter_archive;
        autoindex on;
    }
    # See https://www.digitalocean.com/community/tutorials/understanding-and-implementing-fastcgi-proxying-in-nginx
    # This is clobbering all previous settings -- nothing can be inherited.
    # Do not add any fastcgi_param line inside the location blocks for this reason
    include /etc/nginx/fastcgi_params;
    fastcgi_param PATH_TRANSLATED $document_root$fastcgi_script_name;
    fastcgi_param SCRIPT_FILENAME $document_root$processor;

    #fastcgi_param REQUEST_METHOD $request_method;
    location ~ \.md$ {
        set $processor /cgi-bin/markdown/Markdown.cgi;
        fastcgi_pass  unix:/var/run/fcgiwrap.socket;
    }
    #location ~ \.view$ {
    #    set $processor /cgi-bin/view.cgi;
    #    fastcgi_pass  unix:/var/run/fcgiwrap.socket;
    #}
    location ~ \.status$ {
        set $processor /cgi-bin/status.cgi;
        fastcgi_pass  unix:/var/run/fcgiwrap.socket;
    }
}
