server {
    listen 80;
    listen [::]:80;
    server_name    invent.za3k.com default_server;

    location / {
        root /var/www/public;
        index about.html;
        default_type text/plain;
        add_header  X-Robots-Tag "noindex, nofollow, nosnippet, noarchive";
        autoindex     on;
    }
}
