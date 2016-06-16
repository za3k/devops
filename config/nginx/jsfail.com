server {
    listen [::]:80;
    server_name jsfail.com;

    location / {
        root   /var/www/jsfail;
    }
}
