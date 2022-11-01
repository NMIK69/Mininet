#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    def build(self, **_opts):

        # add routers
        r1 = self.addHost('r1', cls=LinuxRouter, ip='10.0.0.1/24')
        r2 = self.addHost('r2', cls=LinuxRouter, ip='10.1.0.1/24')

        # add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')


        # connet switches with routers
        self.addLink(
            s1,
            r1,
            intfName2='r1-eth1',
            params2={'ip': '10.0.0.1/24'}
        )

        self.addLink(
            s2,
            r1,
            intfName2='r1-eth2',
            params2={'ip': '10.0.1.1/24'}
        )

        self.addLink(
            s3,
            r2,
            intfName2='r2-eth1',
            params2={'ip': '10.1.0.1/24'}
        )

        self.addLink(
            s4,
            r2,
            intfName2='r2-eth2',
            params2={'ip': '10.1.1.1/24'}
        )

        # add router link/connection
        self.addLink(
            r1,
            r2,
            intfName1='r1-eth3',
            intfName2='r2-eth3',
            params1={'ip': '10.100.0.1/24'},
            params2={'ip': '10.100.0.2/24'}
        )


        # add hosts in network 1
        n1h1 = self.addHost(
            name='n1h1',
            ip='10.0.0.10/24',
            defaultRoute='via 10.0.0.1'
        )
        n1h2 = self.addHost(
            name='n1h2',
            ip='10.0.0.20/24',
            defaultRoute='via 10.0.0.1'
        )
        n1h3 = self.addHost(
            name='n1h3',
            ip='10.0.0.30/24',
            defaultRoute='via 10.0.0.1'
        )


        # add hosts in network 2
        n2h1 = self.addHost(
            name='n2h1',
            ip='10.0.1.10/24',
            defaultRoute='via 10.0.1.1'
        )
        n2h2 = self.addHost(
            name='n2h2',
            ip='10.0.1.20/24',
            defaultRoute='via 10.0.1.1'
        )
        n2h3 = self.addHost(
            name='n2h3',
            ip='10.0.1.30/24',
            defaultRoute='via 10.0.1.1'
        )
        n2h4 = self.addHost(
            name='n2h4',
            ip='10.0.1.40/24',
            defaultRoute='via 10.0.1.1'
        )


        # add hosts in network 3
        n3h1 = self.addHost(
            name='n3h1',
            ip='10.1.0.10/24',
            defaultRoute='via 10.1.0.1'
        )
        n3h2 = self.addHost(
            name='n3h2',
            ip='10.1.0.20/24',
            defaultRoute='via 10.1.0.1'
        )
        n3h3 = self.addHost(
            name='n3h3',
            ip='10.1.0.30/24',
            defaultRoute='via 10.1.0.1'
        )

        # add hosts in network 4
        n4h1 = self.addHost(
            name = 'n4h1',
            ip='10.1.1.10/24',
            defaultRoute='via 10.1.1.1'
        )
        n4h2 = self.addHost(
            name = 'n4h2',
            ip='10.1.1.20/24',
            defaultRoute='via 10.1.1.1'
        )
        n4h3 = self.addHost(
            name = 'n4h3',
            ip='10.1.1.30/24',
            defaultRoute='via 10.1.1.1'
        )
        n4h4 = self.addHost(
            name = 'n4h4',
            ip='10.1.1.40/24',
            defaultRoute='via 10.1.1.1'
        )

        # Add host switch links for network 1
        self.addLink(n1h1, s1)
        self.addLink(n1h2, s1)
        self.addLink(n1h3, s1)

        # add host switch links for network 2
        self.addLink(n2h1, s2)
        self.addLink(n2h2, s2)
        self.addLink(n2h3, s2)
        self.addLink(n2h4, s2)
        
        # add host switch links for network 3
        self.addLink(n3h1, s3)
        self.addLink(n3h2, s3)
        self.addLink(n3h3, s3)

        # add host switch links for network 4
        self.addLink(n4h1, s4)
        self.addLink(n4h2, s4)
        self.addLink(n4h3, s4)
        self.addLink(n4h4, s4)

        


def run():
    topo = NetworkTopo()
    net = Mininet(topo=topo)

    # connect subnets of different routers
    net['r1'].cmd("ip route add 10.1.0.0/24 via 10.100.0.2 dev r1-eth3")
    net['r1'].cmd("ip route add 10.1.1.0/24 via 10.100.0.2 dev r1-eth3")

    net['r2'].cmd("ip route add 10.0.0.0/24 via 10.100.0.1 dev r2-eth3")
    net['r2'].cmd("ip route add 10.0.1.0/24 via 10.100.0.1 dev r2-eth3")

    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
