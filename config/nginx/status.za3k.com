# Same but these will only EVER listen on HTTPS (cannot be changed, 301 is designed to be cached forever)
server {
    listen [::]:80;
    server_name    status.za3k.com;
    location ~ /.well-known {
        allow all;
        root /var/www/well-known/status.za3k.com;
    }
    location / {
        return         301 https://$host$request_uri;
    }
}
    
server {
    listen [::]:443 ssl;
    server_name status.za3k.com;

    ssl_certificate /etc/ssl/certs/status.za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/status.za3k.com.key;

    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/ssl/private/letsencrypt.cer;

    add_header Strict-Transport-Security "max-age=315360000; includeSubDomains"; # HSTS

    index service.status;
    root /var/www/za3k;

    # See https://www.digitalocean.com/community/tutorials/understanding-and-implementing-fastcgi-proxying-in-nginx
    # This is clobbering all previous settings -- nothing can be inherited.
    # Do not add any fastcgi_param line inside the location blocks for this reason
    include /etc/nginx/fastcgi_params;
    fastcgi_param PATH_TRANSLATED $document_root$fastcgi_script_name;
    fastcgi_param SCRIPT_FILENAME $document_root$processor;

    #fastcgi_param REQUEST_METHOD $request_method;
    location ~ \.status$ {
        set $processor /cgi-bin/status.cgi;
        fastcgi_pass  unix:/var/run/fcgiwrap.socket;
    }
}