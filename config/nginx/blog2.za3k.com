server {
    listen [::]:80;
    server_name    blog2.za3k.com;

    index index.html index.md;
    root /var/www/za3k_blog2;
}
