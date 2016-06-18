# Interactive card catalog and permalinks
#upstream card_catalog {
#    server 127.0.0.1:2050;
#}

# These servers only listen on HTTPS, redirect HTTP requests
server {
    listen [::]:80;
    server_name    library.za3k.com;
    return         302 https://$host$request_uri;
}

server {
    listen [::]:443 ssl;
    server_name library.za3k.com;

    ssl_certificate /etc/ssl/certs/library.za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/library.za3k.com.key;
      
    #location ~* /(qr\.png|permalink|cardCatalog|card.css|update) {
    #    proxy_pass http://card_catalog;
    #}
    location / {
        root /var/www/library;
        add_header  X-Robots-Tag "noindex, nofollow, nosnippet, noarchive";
        autoindex on;
    }
}
