Please find the routing table screenshot for every node in the folder for Part A.
Please find the traceroute from H1-H2 and H2-H1 via screenshot present in the folder for Part A.

To configure static routes, the script in this folder contains the commands.

We enable ip forwarding on each node using the command:

H1 echo 1 > /proc/sys/net/ipv4/ip_forward
R1 echo 1 > /proc/sys/net/ipv4/ip_forward
R2 echo 1 > /proc/sys/net/ipv4/ip_forward
R3 echo 1 > /proc/sys/net/ipv4/ip_forward
R4 echo 1 > /proc/sys/net/ipv4/ip_forward
H2 echo 1 > /proc/sys/net/ipv4/ip_forward

We add IP addresses to each of the interfaces using:

R1 ip addr add 163.0.0.2/20 dev R1-eth1
R1 ip addr add 164.0.0.2/20 dev R1-eth2
R2 ip addr add 165.0.0.2/20 dev R2-eth1
R3 ip addr add 166.0.0.2/20 dev R3-eth1
R4 ip addr add 165.0.0.1/20 dev R4-eth1
R4 ip addr add 166.0.0.1/20 dev R4-eth2


We then configure routes on each of the nodes using the commands:

H1 ip route add 163.0.0.0/20 via 162.0.0.2 dev H1-eth0
H1 ip route add 164.0.0.0/20 via 162.0.0.2 dev H1-eth0
H1 ip route add 165.0.0.0/20 via 162.0.0.2 dev H1-eth0
H1 ip route add 166.0.0.0/20 via 162.0.0.2 dev H1-eth0
H1 ip route add 167.0.0.0/20 via 162.0.0.2 dev H1-eth0

R1 ip route add 165.0.0.0/20 via 163.0.0.1 dev R1-eth1
R1 ip route add 166.0.0.0/20 via 164.0.0.1 dev R1-eth2
R1 ip route add 167.0.0.0/20 via 163.0.0.1 dev R1-eth1

R2 ip route add 162.0.0.0/20 via 163.0.0.2 dev R2-eth0
R2 ip route add 164.0.0.0/20 via 163.0.0.2 dev R2-eth0
R2 ip route add 166.0.0.0/20 via 165.0.0.1 dev R2-eth1
R2 ip route add 167.0.0.0/20 via 165.0.0.1 dev R2-eth1

R3 ip route add 162.0.0.0/20 via 164.0.0.2 dev R3-eth0
R3 ip route add 163.0.0.0/20 via 164.0.0.2 dev R3-eth0
R3 ip route add 165.0.0.0/20 via 166.0.0.1 dev R3-eth1
R3 ip route add 167.0.0.0/20 via 166.0.0.1 dev R3-eth1

R4 ip route add 162.0.0.0/20 via 166.0.0.2 dev R4-eth2
R4 ip route add 163.0.0.0/20 via 165.0.0.2 dev R4-eth1
R4 ip route add 164.0.0.0/20 via 166.0.0.2 dev R4-eth2

H2 ip route add 162.0.0.0/20 via 167.0.0.2 dev H2-eth0
H2 ip route add 163.0.0.0/20 via 167.0.0.2 dev H2-eth0
H2 ip route add 164.0.0.0/20 via 167.0.0.2 dev H2-eth0
H2 ip route add 165.0.0.0/20 via 167.0.0.2 dev H2-eth0
H2 ip route add 166.0.0.0/20 via 167.0.0.2 dev H2-eth0

#FORWARD RELAYING: H1 to H2
R2 iptables -t nat -A POSTROUTING -o R2-eth1 -j MASQUERADE
R2 iptables -A FORWARD -i R2-eth0 -o R2-eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT
R2 iptables -A FORWARD -i R2-eth0 -o R2-eth1 -j ACCEPT
	
#REVERSE REALYING:- H2 to H1
R4 iptables -A FORWARD -i R4-eth0 -o R4-eth2 -j ACCEPT
R4 iptables -A FORWARD -i R4-eth0 -o R4-eth2 -m state --state RELATED,ESTABLISHED -j ACCEPT
R4 iptables -t nat -A POSTROUTING -o R4-eth2 -j MASQUERADE

For example: 
	H1 ip route add 167.0.0.1/20 via 162.0.0.2 dev H1-eth0
	H1 will send data packets to subnet 167.0.0.1/20 via HOP 162.0.0.2


	