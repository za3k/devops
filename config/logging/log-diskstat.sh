NC="netcat"
LOG=/var/log/diskstat

mkdir -p $LOG
send_stats () {
    # usage: send_stats $name $value $target_unit
    while read conv; do
    #echo "disks.$(hostname).$conv" >/dev/stderr
    echo "disks.$(hostname).$conv" | 
    $NC -u -w 4 -i 4 graph.za3k.com 8125
    done
}

date >> $LOG/temp
hddtemp $DRIVES >> $LOG/temp 2>/dev/null

{
DRIVES_BY_ID=$(find /dev/disk/by-id -regextype grep -regex '.*/ata-.*' -not -regex '.*/ata-.*-part.*')
hddtemp $DRIVES_BY_ID 2>/dev/null | sed 's/\/dev\/disk\/by-id\/ata-\(.*\): [^:]*: \([0-9]*\).C$/hdd.temp.\1:\2|g/'
} | send_stats

date >> $LOG/smart
for drive in $DRIVES; do
    smartctl -a $drive >> $LOG/smart 2>&1
done

date >> $LOG/df
df -h >> $LOG/df 2>&1

# Find root FS usage
df --block-size=1 --output=target,size,used --exclude-type=tmpfs --exclude-type=devtmpfs --exclude-type=aufs | tail -n +2 | grep '^/\s' | awk "{printf(\"df.root.used:%s|g\n\", \$3)}" | send_stats "df.root.used"
df --block-size=1 --output=target,size,used --exclude-type=tmpfs --exclude-type=devtmpfs --exclude-type=aufs | tail -n +2 | grep '^/\s' | awk "{printf(\"df.root.size:%s|g\n\", \$2)}" | send_stats "df.root.size"

# Try curling www.example.com
#CURLTIME=$(docker run --dns 4.2.2.2 --rm curltest bash -c 'time -p curl -o /dev/null -s www.example.com' 2>&1 | grep real | awk '{print $2}')
#echo "speedtest.curltime:$CURLTIME|g" | $NC -u -4 -w 4 -i 4 graph.za3k.com 8125
 
