"""
Example topology of Quagga routers
"""

import inspect
import os
from mininext.topo import Topo
from mininext.services.quagga import QuaggaService

from collections import namedtuple

QuaggaHost = namedtuple("QuaggaHost", "name ip loIP")
net = None


class QuaggaTopo(Topo):

    "Creates a topology of Quagga routers"

    def __init__(self):
        """Initialize a Quagga topology with 5 routers, configure their IP
           addresses, loop back interfaces, and paths to their private
           configuration directories."""
        Topo.__init__(self)

        # Directory where this file / script is located"
        selfPath = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))  # script directory

        # Initialize a service helper for Quagga with default options
        quaggaSvc = QuaggaService(autoStop=False)

        # Path configurations for mounts
        quaggaBaseConfigPath = selfPath + '/configs/'

        # List of Quagga host configs
        quaggaHosts = []
        quaggaHosts.append(QuaggaHost(name='H1', ip='162.0.0.1/20',
                                      loIP='10.0.1.1/24'))
        quaggaHosts.append(QuaggaHost(name='R1', ip='162.0.0.2/20',
                                      loIP='10.0.2.1/24'))
        quaggaHosts.append(QuaggaHost(name='R2', ip='163.0.0.1/20',
                                      loIP='10.0.3.1/24'))
        quaggaHosts.append(QuaggaHost(name='R3', ip='164.0.0.1/20',
                                      loIP='10.0.3.1/24'))
        quaggaHosts.append(QuaggaHost(name='R4', ip='167.0.0.2/20',
                                      loIP='10.0.4.1/24'))
        quaggaHosts.append(QuaggaHost(name='H2', ip='167.0.0.1/20',
                                      loIP=None))
	qc = []	
        # Setup each Quagga router, add a link between it and the IXP fabric
        for host in quaggaHosts:

            # Create an instance of a host, called a quaggaContainer
            qc.append(self.addHost(name=host.name,
                                           ip=host.ip,
                                           hostname=host.name,
                                           privateLogDir=True,
                                           privateRunDir=True,
                                           inMountNamespace=True,
                                           inPIDNamespace=True,
                                           inUTSNamespace=True))

            # Configure and setup the Quagga service for this node
            quaggaSvcConfig = \
                {'quaggaConfigPath': quaggaBaseConfigPath + host.name}
            self.addNodeService(node=host.name, service=quaggaSvc,
                                nodeConfig=quaggaSvcConfig)

	self.addLink(qc[0], qc[1])
	self.addLink(qc[1], qc[2])
	self.addLink(qc[1], qc[3])
	self.addLink(qc[5], qc[4])
	self.addLink(qc[2], qc[4])
	self.addLink(qc[3], qc[4])

