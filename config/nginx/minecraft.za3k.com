server {
    listen [::]:80;
    server_name minecraft.za3k.com;

    root   /var/www/minecraft-www;
    index index.txt;
}
