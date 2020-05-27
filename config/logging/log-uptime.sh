export NC="netcat"
echo "uptime.$(hostname):1|c" | 
$NC -u -w 4 -i 4 graph.za3k.com 8125
