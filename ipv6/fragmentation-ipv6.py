#  Network topology
#  #
#  #            n0   r    n1
#  #             |    _    |
#  #             ====|_|====
#  #                router
#  #
#  # - Tracing of queues and packet receptions to file "fragmentation-ipv6.tr"

import ns.core
import ns.internet
import ns.internet_apps
import ns.csma
import ns.network

def main(argv):
        print ("FragmentationIpv6Example")

        cmd = ns.core.CommandLine ()
        cmd.AddValue ("verbose", "turn on log components")
        cmd.verbose = False
        cmd.Parse (argv)
        verbose = bool(cmd.verbose)

        if verbose:
            ns.core.LogComponentEnable ("Ipv6L3Protocol", ns.core.LOG_LEVEL_ALL)
            ns.core.LogComponentEnable ("Icmpv6L4Protocol", ns.core.LOG_LEVEL_ALL)
            ns.core.LogComponentEnable ("Ipv6StaticRouting", ns.core.LOG_LEVEL_ALL)
            ns.core.LogComponentEnable ("Ipv6Interface", ns.core.LOG_LEVEL_ALL)
            ns.core.LogComponentEnable ("Ping6Application", ns.core.LOG_LEVEL_ALL)
            
        print("Create nodes.")
        n0 = ns.network.Node()
        r = ns.network.Node()
        n1 = ns.network.Node()

        net1 = ns.network.NodeContainer()
        net1.Add(n0)
        net1.Add(r)
        net2 = ns.network.NodeContainer()
        net2.Add(r)
        net2.Add(n1)
        all = ns.network.NodeContainer()
        all.Add(n0)
        all.Add(r)
        all.Add(n1)

        print ("Create IPv6 Internet Stack")
        internetv6 = ns.internet.InternetStackHelper()
        internetv6.Install (all)

        print ("Create channels.")
        csma = ns.csma.CsmaHelper() 
        csma.SetChannelAttribute ("DataRate", ns.network.DataRateValue (ns.network.DataRate(5000000)))
        csma.SetChannelAttribute ("Delay", ns.core.TimeValue (ns.core.MilliSeconds (2)))
        d1 = csma.Install (net1)
        d2 = csma.Install (net2)

        print ("Create networks and assign IPv6 Addresses.")
        ipv6 = ns.internet.Ipv6AddressHelper()
        ipv6.SetBase (ns.network.Ipv6Address ("2001:1::"), ns.network.Ipv6Prefix (64))
        i1 = ipv6.Assign (d1)
        i1.SetForwarding (1, True)
        i1.SetDefaultRouteInAllNodes (1)
        ipv6.SetBase  (ns.network.Ipv6Address ("2001:2::"), ns.network.Ipv6Prefix (64))
        i2 = ipv6.Assign (d2)
        i2.SetForwarding (0, True)
        i2.SetDefaultRouteInAllNodes (0)

        routingHelper = ns.internet.Ipv6StaticRoutingHelper()
        routingStream = ns.network.OutputStreamWrapper("fragmentation-ipv6.routes", ns.network.STD_IOS_OUT)
        routingHelper.PrintRoutingTableAt (ns.core.Seconds (0), n0, routingStream)

        #  Create a Ping6 application to send ICMPv6 echo request from n0 to n1 via r 
        packetSize = 4096
        maxPacketCount = 5
        interPacketInterval = ns.core.Seconds (1.0)
        ping6 = ns.internet_apps.Ping6Helper()

        ping6.SetLocal (i1.GetAddress (0, 1))
        ping6.SetRemote (i2.GetAddress (1, 1))

        ping6.SetAttribute ("MaxPackets", ns.core.UintegerValue (maxPacketCount))
        ping6.SetAttribute ("Interval", ns.core.TimeValue (interPacketInterval))
        ping6.SetAttribute ("PacketSize", ns.core.UintegerValue (packetSize))
        apps = ping6.Install (ns.network.NodeContainer(net1.Get (0)))
        apps.Start (ns.core.Seconds (2.0))
        apps.Stop (ns.core.Seconds (20.0))

        ascii = ns.network.AsciiTraceHelper()
        csma.EnableAsciiAll (ascii.CreateFileStream ("fragmentation-ipv6.tr"))
        csma.EnablePcapAll ("fragmentation-ipv6", True)

        print ("Run Simulation.")
        ns.core.Simulator.Run ()
        ns.core.Simulator.Destroy ()
        print ("Done.")


if __name__ == '__main__':
    import sys
    main (sys.argv)


