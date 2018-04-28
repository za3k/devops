echo "uptime.$(hostname):1|c" | 
netcat -u -w 4 -i 4 graph.za3k.com 8125
