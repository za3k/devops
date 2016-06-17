server {
    listen	       [::]:80;
    server_name    petchat.za3k.com;

    location / {
        root   /var/www/petchat;
    }
}
