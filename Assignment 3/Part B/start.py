#!/usr/bin/python

"""
Example network of Quagga routers
(QuaggaTopo + QuaggaService)
"""

import sys
import atexit
import time

# patch isShellBuiltin
import mininet.util
import mininext.util
mininet.util.isShellBuiltin = mininext.util.isShellBuiltin
sys.modules['mininet.util'] = mininet.util

from mininet.util import dumpNodeConnections
from mininet.node import OVSController
from mininet.log import setLogLevel, info

from mininext.cli import CLI
from mininext.net import MiniNExT

from topo import QuaggaTopo

net = None


def startNetwork():
    "instantiates a topo, then starts the network and prints debug information"

    info('** Creating Quagga network topology\n')
    topo = QuaggaTopo()

    info('** Starting the network\n')
    global net
    net = MiniNExT(topo, controller=OVSController)
    net.start()

    info('** Dumping host connections\n')
    dumpNodeConnections(net.hosts)

    info('** Testing network connectivity\n')
    net.ping(net.hosts)

    info('** Setting up ip address\n')
    net.hosts[2].cmdPrint('ip addr add 163.0.0.2/20 dev R1-eth1')
    net.hosts[2].cmdPrint('ip addr add 164.0.0.2/20 dev R1-eth2')
    net.hosts[3].cmdPrint('ip addr add 165.0.0.2/20 dev R2-eth1')
    net.hosts[4].cmdPrint('ip addr add 166.0.0.2/20 dev R3-eth1')
    net.hosts[5].cmdPrint('ip addr add 165.0.0.1/20 dev R4-eth1')
    net.hosts[5].cmdPrint('ip addr add 166.0.0.1/20 dev R4-eth2')
    
    info('** Dumping host processes\n')
    for host in net.hosts:
        host.cmdPrint("ps aux")
	host.cmdPrint("echo 1 > /proc/sys/net/ipv4/ip_forward")

    info('Pinging for Convergence\n')
    for i in range(1, 5):
	time.sleep(1)
	h1, h2  = net.hosts[0], net.hosts[1]
	print h1.cmd('ping -c1 %s' % h2.IP())
	print time.time()	

    print h1.cmd('traceroute %s' % h2.IP())
    print h2.cmd('traceroute %s' % h1.IP())

    net.configLinkStatus('R1','R2','down')
    info('Pinging for Convergence\n')
    for i in range(1, 40):
        time.sleep(1)
        h1, h2  = net.hosts[0], net.hosts[1]
        print h1.cmd('ping -c1 %s' % h2.IP())
        print time.time()
    
    print h1.cmd('traceroute %s' % h2.IP())
    print h2.cmd('traceroute %s' % h1.IP())

    info('** Running CLI\n')
    CLI(net)


def stopNetwork():
    "stops a network (only called on a forced cleanup)"

    if net is not None:
        info('** Tearing down Quagga network\n')
        net.stop()

if __name__ == '__main__':
    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    setLogLevel('info')
    startNetwork()
