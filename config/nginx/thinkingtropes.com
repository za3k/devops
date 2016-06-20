# Only listen on HTTPS
server {
    listen [::]:80;
    server_name    thinkingtropes.com;
    return         302 https://$host$request_uri;
}

# Make certificates once email is back up
#server {
#    listen [::]:443 ssl;
#    server_name    thinkingtropes.com;
#    ssl_certificate /etc/ssl/certs/thinkingtropes.com.pem;
#    ssl_certificate_key /etc/ssl/private/thinkingtropes.com.key;
#    location / {
#        root   /var/www/thinkingtropes;
#    }
#}
