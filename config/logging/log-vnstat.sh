#!/bin/bash
export NC="netcat"
IFACE=enp3s0
send_stats () {
    # usage: send_stats $name $value $target_unit
    if [[ "$3" == "" ]]; then
        conv=$2
    else
        conv=$(units -o "%.0f" -t "$2" "$3")
    fi
    echo "vnstat.$(hostname).eth0:$conv|g" | $NC -u -w 2 graph.za3k.com 8125
}

# Example output of vnstat --oneline
# 1;eth0;10/08/16;7.30 GiB;1.75 GiB;9.04 GiB;129.26 KiB/s;Oct '16;108.62 GiB;28.02 GiB;136.65 GiB;211.28 KiB/s;1.76 TiB;322.10 GiB;2.07 TiB
stats=$(vnstat -i $IFACE --oneline)

now=$(echo "$stats" | awk -F';' '{print $3}')
rx_today=$(echo "$stats" | awk -F';' '{print $4}')
tx_today=$(echo "$stats" | awk -F';' '{print $5}')
total_today=$(echo "$stats" | awk -F';' '{print $6}')
traffic_today=$(echo "$stats" | awk -F';' '{print $7}')
rx_month=$(echo "$stats" | awk -F';' '{print $9}')
tx_month=$(echo "$stats" | awk -F';' '{print $10}')
total_month=$(echo "$stats" | awk -F';' '{print $11}')
traffic_month=$(echo "$stats" | awk -F';' '{print $12}')
rx_alltime=$(echo "$stats" | awk -F';' '{print $13}')
tx_alltime=$(echo "$stats" | awk -F';' '{print $14}')
total_alltime=$(echo "$stats" | awk -F';' '{print $15}')

send_stats 'month.tx' "$tx_month" "bytes"
send_stats 'month.rx' "$rx_month" "bytes"
send_stats 'month.total' "$total_month" "bytes"
send_stats 'month.traffic' "$traffic_month" "bytes/sec"

send_stats 'today.tx' "$tx_today" "bytes"
send_stats 'today.rx' "$rx_today" "bytes"
send_stats 'today.total' "$total_today" "bytes"
send_stats 'today.traffic' "$traffic_today" "bytes/sec"

send_stats 'alltime.tx' "$tx_alltime" "bytes"
send_stats 'alltime.rx' "$rx_alltime" "bytes"
send_stats 'alltime.total' "$total_alltime" "bytes"
