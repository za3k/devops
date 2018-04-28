#!/bin/sh
send_stats(){
    while read conv; do
	    echo "ping.$(hostname).$conv" | 
	    netcat -u -w 0 -i 4 graph.za3k.com 8125
    done
}
PACKETS=5
HOST=8.8.8.8
# Limit time to 1sec/packet total
ping $HOST -c${PACKETS} -w ${PACKETS} | awk "BEGIN {FS=\"[=]|[ ]\"} {if(NR>1 && NR<=1+${PACKETS})print \$10}" | while read latency; do
  echo "ping.latency:${latency}|g"
done | send_stats
