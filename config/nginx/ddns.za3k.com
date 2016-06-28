# DDNS 
upstream ddns {
    server 127.0.0.1:9090;
}

# These servers only listen on HTTPS, redirect HTTP requests
server {
    listen [::]:80;
    server_name    ddns.za3k.com;
    return         302 https://$host$request_uri;
}

server {
    listen [::]:443 ssl;
    server_name ddns.za3k.com;

    ssl_certificate /etc/ssl/certs/ddns.za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/ddns.za3k.com.key;
      
    location / {
        proxy_pass http://ddns;
    }
}
