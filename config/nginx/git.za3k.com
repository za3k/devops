# These servers only listen on HTTPS, redirect HTTP requests
server {
    listen 	   [::]:80;
    server_name    git.za3k.com;
    return         302 https://$host$request_uri;
}
    
server {
    listen [::]:443 ssl;
    server_name git.za3k.com;

    ssl_certificate /etc/ssl/certs/git.za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/git.za3k.com.key;

    # Smart HTTP git config. Based on:
    # https://www.toofishes.net/blog/git-smart-http-transport-nginx/
    #location ~ /git(/.*) {
    location / {
        include       fastcgi_params;
        fastcgi_pass  unix:/var/run/fcgiwrap.socket;
        fastcgi_param SCRIPT_FILENAME     /usr/lib/git-core/git-http-backend;
        # export all repositories under GIT_PROJECT_ROOT
        # fastcgi_param GIT_HTTP_EXPORT_ALL "";
        fastcgi_param GIT_PROJECT_ROOT    /git;
	fastcgi_param PATH_INFO $uri;
    }
}
