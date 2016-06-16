server {
    listen [::]:80;
    listen [::]:443 ssl;
    server_name moreorcs.com www.moreorcs.com;

    ssl_certificate /etc/ssl/certs/moreorcs.com.pem;
    ssl_certificate_key /etc/ssl/private/moreorcs.com.key;

    location / {
        root   /var/www/moreorcs/www;
    }
}
