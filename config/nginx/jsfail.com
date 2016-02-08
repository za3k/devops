server {
    listen [::]:80;
    server_name jsfail.com;

    location / {
        root   /usr/share/nginx/jsfail;
    }
}
