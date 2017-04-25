We first need to configure each of the hosts and routers by copying below mentioned files to each ones config inside ~/avnigam/configs
This would enable the zebra and ripd capabilities for each Hosts and Routers.

#Enable zebra=yes and ripd=yes in /etc/quagga/daemons file
#cp /usr/share/doc/quagga/examples/zebra.conf.sample /etc/quagga/zebra.conf
#cp /usr/share/doc/quagga/examples/ripd.conf.sample /etc/quagga/ripd.conf
	
restart the quagga service: /etc/init.d/quagga restart

Then enable IP forwarding variableas to 1
H1 echo 1 > /proc/sys/net/ipv4/ip_forward
R1 echo 1 > /proc/sys/net/ipv4/ip_forward
R2 echo 1 > /proc/sys/net/ipv4/ip_forward
R3 echo 1 > /proc/sys/net/ipv4/ip_forward
R4 echo 1 > /proc/sys/net/ipv4/ip_forward
H2 echo 1 > /proc/sys/net/ipv4/ip_forward

To configure every router/host with Quagga ripd daemons, following commands have been used:
	
login to any router/host
1. cd /miniNExT/util
2. ./mx R1  #launch any host/router
3. netstat -na #find the port of running ripd
4. telnet localhost 2602  #remote access for localhost/ripd process
# You will be prompted for password (zebra)
5. en #Enable
6. configure terminal #to configure the ripd terminal
7. router rip #Enables RIP as a routing protocol
8. network R1-eth0 #Configure each of  the interfaces of the router/host directly connected to your network which you want to advertise.
9. write #Save the config
10.	exit #Come out of the terminal


a) The screen shots of the kernel and quagga routing table are present in this folder.

b) The screen shots of the traceroute command output is present in this folder.

c) The screen shots of the ping command output is present in this folder.

d) The convergence time is 2 secs which is figured out by writing a small ping code in start.py 


a) To bring down the link, the following command within the start.py has been used:
net.configLinkStatus('R1','R2','down')

b) The time to re-establish connectivity is 28 secs which is figured out by writing a small code in start.py.

c) The screen shots of the traceroute command output after the link has been brought down is present in this folder.