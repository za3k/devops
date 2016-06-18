# NPM thisisashell.com app
upstream thisisashell {
    server 127.0.0.1:2049;
}

# Will only EVER listen on HTTPS (cannot be changed, 301 is designed to be cached forever)
server {
    listen [::]:80;
    server_name    thisisashell.com;
    return         301 https://$host$request_uri;
}

server {
    listen [::]:443 ssl;
    server_name thisisashell.com;
    access_log off;

    ssl_certificate /etc/ssl/certs/thisisashell.com.pem;
    ssl_certificate_key /etc/ssl/private/thisisashell.com.key;
  
    location / {
      proxy_pass http://thisisashell;
    }
}
