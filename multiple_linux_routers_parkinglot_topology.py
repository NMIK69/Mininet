#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import argparse


routers = []
hosts = []
router_names = []
host_names = []
host_ips = []
rc_ips = [] # router connect ip adresses
N = 5

class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    def build(self, **_opts):
        
        recv = self.addHost('recv', cls=LinuxRouter, ip='10.100.0.1/24')
        
        ''''
            each hosts connects to their router on eth1
            router to the left connects to eth2
            router to the right connects to eth3
        '''


        #init routers and hosts and connect them
        for i in range(N):
            #make parameters
            router_name = "r"+str(i+1)
            host_name = "h"+str(i+1)
            ip_addr_router = "10.0."+str(i + 1)+".1/24"
            ip_addr_router_no_cidr = "via 10.0."+str(i + 1)+".1"
            ip_addr_host = "10.0."+str(i + 1)+".2"
            router_interface_name = "r"+str(i+1)+"-eth1"


            #add router
            router= self.addNode(router_name, cls=LinuxRouter, ip=ip_addr_router)
            routers.append(router)

            #make corresponding host to router and add default addr over router
            host = self.addHost(name=host_name, ip=ip_addr_host+'/24', defaultRoute=ip_addr_router_no_cidr)
            hosts.append(host)

            ##connect host to router
            self.addLink(host, router, intfName2=router_interface_name,  params2={'ip':ip_addr_router})



        #connect adjacent routers
        for i in range(N-1):
            router_connection_net_left = "10."+str(i+1)+".0.1/24"
            router_connection_net_right = "10."+str(i+1)+".0.2/24"


            left_interface_name = "r"+str(i+1)+"-eth2"
            right_interface_name = "r"+str(i+2)+"-eth3"

            self.addLink(routers[i], routers[i+1], intfName1=left_interface_name, intfName2=right_interface_name, 
                params1={'ip':router_connection_net_left}, params2={'ip':router_connection_net_right}
            )

        # add r1 to recv connection
        self.addLink(recv, routers[0], intfName1='recv-eth2', intfName2='r1-eth3', 
                params1={'ip':'10.100.0.1/24'}, params2={'ip':'10.100.0.2/24'}
            )



def run():
    topo = NetworkTopo()
    net = Mininet(topo=topo)

    # add routing across all routers
    '''
        for r1
        -->
        add h2-hn via r2
        add r3-rn via r2

        for r2
        <--
        add h1 via r1
        -->
        add h3-hn via r3
        add r4-rn via r3

        for r3
        <--
        add h1-h2 via r2
        add r1 via r2
        -->
        add h4-hn via r4
        add r5-rn via r4

        for r4
        <--
        add h1-h3 via r3
        add r1-r2 via r3
        -->
        add h5-hn via r5
        add r6-rn via r5

        .
        .
        .

    '''
    
    for i in range(N):
        host_names.append('h'+str(i+1))
        router_names.append('r'+str(i+1))
        host_ips.append('10.0.'+str(i+1)+'.0/24')
        rc_ips.append('10.'+str(i+1))


    for i in range(N):
        rn = 'r'+str(i+1)

        if i > 0:
            # add router connection to recv
            net[rn].cmd('ip route add 10.100.0.0/24 via '+rc_ips[i-1]+'.0.1 dev '+rn+'-eth3')

        # for recv add router connection
        net['recv'].cmd('ip route add '+rc_ips[i]+'.0.0/24 via 10.100.0.2 dev recv-eth2')
        #connect recv to all hosts
        net['recv'].cmd('ip route add '+host_ips[i]+' via 10.100.0.2 dev recv-eth2')



        for j in range(N):

            # add connections
            if j < i:
                # add routing for hosts to the left
                net[rn].cmd('ip route add '+host_ips[j]+' via '+rc_ips[i-1]+'.0.1 dev '+rn+'-eth3')

            if j < i - 1:    
                #add routing for routers to the left
                net[rn].cmd('ip route add '+rc_ips[j]+'.0.0/24 via '+rc_ips[i-1]+'.0.1 dev '+rn+'-eth3')

            if j > i:
                # add routing for hosts to the right
                net[rn].cmd('ip route add '+host_ips[j]+' via '+rc_ips[i]+'.0.2 dev '+rn+'-eth2')

            if j > i and j < (N-1):    
                #add routing for routers to the right
                net[rn].cmd('ip route add '+rc_ips[j]+'.0.0/24 via '+rc_ips[i]+'.0.2 dev '+rn+'-eth2')


    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--hosts", type=int, default=5)
    args = parser.parse_args()
    N = args.hosts

    setLogLevel('info')
    run()