server {
    listen [::]:80;
    server_name    isrickandmortyout.com www.isrickandmortyout.com;
    index index.html;
    root /var/www/rickandmorty;
    location / {
    }
}
