# Same but these will only EVER listen on HTTPS (cannot be changed, 301 is designed to be cached forever)
server {
    listen [::]:80;
    server_name    za3k.com;
    location ~ /.well-known {
        allow all;
        root /var/www/well-known/za3k.com;
    }
    location / {
        return         301 https://$host$request_uri;
    }
}
    
server {
    listen [::]:443 ssl;
    server_name za3k.com;

    ssl_certificate /etc/ssl/certs/za3k.com.pem;
    ssl_certificate_key /etc/ssl/private/za3k.com.key;

    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/ssl/private/letsencrypt.cer;

    add_header Strict-Transport-Security "max-age=315360000; includeSubDomains"; # HSTS

    index index.html index.md;
    root /var/www/za3k;

    location = /archived.html { return 302 /archive/; }
    location = '/new latin bible.txt' { return 302 /archive/new_latin_bible.txt; }
    location = /mygames.md { return 302 /games/; }
    location = /archive/conspiracies.md { return 302 /games/conspiracies; }
    location = /archive/deadly.md { return 302 /games/deadly; }
    location = /archive/doodle_adventures.md { return 302 /games/doodle_adventures; }
    location = /archive/emperical_zendo.md { return 302 /games/emperical_zendo; }
    location = /archive/faux_pas.md { return 302 /games/faux_pas; }
    location = /archive/invincible1.md { return 302 /games/invincible1; }
    location = /archive/invincible.md { return 302 /games/invincible; }
    location = /archive/invincible.css { return 302 /games/invincible.css; }
    location = /archive/logic_potions.md { return 302 /games/logic_potions; }
    location = /archive/lootboxes.md { return 302 /games/lootboxes; }
    location = /archive/ninjas1.md { return 302 /games/ninjas1; }
    location = /archive/ninjas.md { return 302 /games/ninjas; }
    location = /archive/stupid_russia.md { return 302 /games/stupid_russia; }
    location = /archive/stupid_russia.py { return 302 /games/stupid_russia.py; }
    location = /archive/ultimate_archwizard.md { return 302 /games/ultimate_archwizard; }
    location = /archive/ultimate_archwizard_gm.md { return 302 /games/ultimate_archwizard_gm; }
    location = /archive/colony.md { return 302 /games/colony; }
    location = /games.md { return 302 /videogames; }
    location = /stylish.view { return 302 /archive/stylish.view; }
    location = /aldenmarsh/party { return 302 /aldenmarsh/party/players1; }
    location = /aldenmarsh/party/ { return 302 /aldenmarsh/party/players1; }

    location /github/ {
        alias /var/www/github/;
        gzip on;
        gunzip on; # Enables use of .gz files in directory
        autoindex on;
    }
    location /~colony {
        alias /var/www/colony;
        autoindex on;
    }
    location /~logs {
        alias /var/www/logs;
        autoindex on;
    }
    location /~twitter_archive {
        alias /var/www/twitter_archive;
        autoindex on;
    }
    # See https://www.digitalocean.com/community/tutorials/understanding-and-implementing-fastcgi-proxying-in-nginx
    # This is clobbering all previous settings -- nothing can be inherited.
    # Do not add any fastcgi_param line inside the location blocks for this reason
    include /etc/nginx/fastcgi_params;
    fastcgi_param PATH_TRANSLATED $document_root$fastcgi_script_name;
    fastcgi_param SCRIPT_FILENAME $document_root$processor;

    #fastcgi_param REQUEST_METHOD $request_method;
    location ~ \.md$ {
        try_files $uri archive/$uri =404;
        set $processor /cgi-bin/markdown/Markdown.cgi;
        fastcgi_pass  unix:/var/run/fcgiwrap.socket;
    }
    location ~ \.view$ {
        set $processor /cgi-bin/view.cgi;
        fastcgi_pass  unix:/var/run/fcgiwrap.socket;
    }
    location ~ \.sc.txt$ {
        set $processor /cgi-bin/sc.txt.cgi;
        fastcgi_pass  unix:/var/run/fcgiwrap.socket;
    }
    location ~ {
        try_files $uri $uri/ $uri.html archive/$uri.html $uri.md; # the last parameter is a magic redirect
    }
}
