ipt() {
  iptables "$@"
  ip6tables "$@"
}

set -x

# Clear existing policy
ipt -F
ipt -X
ipt -t nat -F
ipt -t nat -X
ipt -t mangle -F
ipt -t mangle -X
ipt -t raw -F
ipt -t raw -X
ipt -t security -F
ipt -t security -X

# Default policies
ipt --policy INPUT DROP
ipt --policy OUTPUT ACCEPT
ipt --policy FORWARD DROP

# Allow established connections (incoming response)
ipt -A INPUT  -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow all ICMP, including ping
iptables -A INPUT -p icmp -j ACCEPT
ip6tables -A INPUT -p ipv6-icmp -j ACCEPT

# Allow loopback
ipt -A INPUT  -i lo    -j ACCEPT
# ipt -A OUTPUT -i lo    -j ACCEPT

# Make our tables
ipt -N TCP
ipt -N UDP
ipt -A INPUT -p udp -m conntrack --ctstate NEW -j UDP
# https://wiki.archlinux.org/index.php/Simple_stateful_firewall
# "NEW but not SYN is the only invalid TCP flag not covered by the INVALID state. The reason is because they are rarely malicious packets, and they should not just be dropped. Instead, we simply do not accept them, so they are rejected with a TCP RESET by the next rule."
ipt -A INPUT -p tcp --syn -m conntrack --ctstate NEW -j TCP

# Reject bad packets
ipt -A INPUT -m conntrack --ctstate INVALID -j DROP
# https://wiki.archlinux.org/index.php/Simple_stateful_firewall
# Mimic default linux closed port behavior if not specifically handled by TCP, UDP tables
iptables -A INPUT -p udp -j REJECT --reject-with icmp-port-unreachable
iptables -A INPUT -p tcp -j REJECT --reject-with tcp-reset
iptables -A INPUT -j REJECT --reject-with icmp-proto-unreachable
ip6tables -A INPUT -p tcp -j REJECT --reject-with tcp-reset
ip6tables -A INPUT -j REJECT --reject-with icmp6-adm-prohibited

# Allow SSH
ipt -A TCP    -p TCP --dport 22 -j ACCEPT
# Allow SMTP
ipt -A TCP    -p TCP --dport 25 -j ACCEPT
ipt -A TCP    -p TCP --dport 587 -j ACCEPT
# Allow IMAP
ipt -A TCP    -p TCP --dport 143 -j ACCEPT
# Allow ManageSieve
ipt -A TCP    -p TCP --dport 4190 -j ACCEPT
# Allow ZNC
ipt -A TCP    -p TCP --dport 10000 -j ACCEPT
# Allow DNS
# ipt -A UDP    -p UDP --dport 53 -j ACCEPT

mkdir -p /etc/iptables
iptables-save >/etc/iptables/iptables.rules
ip6tables-save >/etc/iptables/ip6tables.rules
