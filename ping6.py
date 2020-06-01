# Network topology
#
#       n0    n1
#       |     |
#       =================
#              LAN
#
# - ICMPv6 echo request flows from n0 to n1 and back with ICMPv6 echo reply
# - DropTail queues 
# - Tracing of queues and packet receptions to file "ping6.tr"

import ns.core
import ns.internet
import ns.internet_apps
import ns.network
import ns.csma


def main(argv):
    
        print("Ping6Example")

        cmd = ns.core.CommandLine()
        cmd.AddValue ("verbose", "turn on log components")
        cmd.verbose = False
        cmd.Parse (argv)
        verbose = bool(cmd.verbose)

        if  verbose :
            ns.core.LogComponentEnable ("Ping6Example", ns.core.LOG_LEVEL_INFO)
            ns.core.LogComponentEnable ("Ipv6EndPointDemux", ns.core.LOG_LEVEL_ALL)
            ns.core.LogComponentEnable ("Ipv6L3Protocol", ns.core.LOG_LEVEL_ALL)
            ns.core.LogComponentEnable ("Ipv6StaticRouting", ns.core.LOG_LEVEL_ALL)
            ns.core.LogComponentEnable ("Ipv6ListRouting", ns.core.LOG_LEVEL_ALL)
            ns.core.LogComponentEnable ("Ipv6Interface", ns.core.LOG_LEVEL_ALL)
            ns.core.LogComponentEnable ("Icmpv6L4Protocol", ns.core.LOG_LEVEL_ALL)
            ns.core.LogComponentEnable ("Ping6Application", ns.core.LOG_LEVEL_ALL)
            ns.core.LogComponentEnable ("NdiscCache", ns.core.LOG_LEVEL_ALL)

        print ("Create nodes.")
        n = ns.network.NodeContainer()
        n.Create(4)

        #  Install IPv4/IPv6 stack 
        internetv6 = ns.internet.InternetStackHelper()
        internetv6.SetIpv4StackInstall (False)
        internetv6.Install (n)
            
        print ("Create channels.")
        csma=ns.csma.CsmaHelper()
        csma.SetChannelAttribute("DataRate", ns.network.DataRateValue (ns.network.DataRate(5000000)))
        csma.SetChannelAttribute("Delay", ns.core.TimeValue (ns.core.MilliSeconds (2)))
        d = csma.Install(n)

        ipv6 = ns.internet.Ipv6AddressHelper()
        print ("Assign IPv6 addresses")
        i = ipv6.Assign(d)

        print ("Create applications.")

        # Create a Ping6 application to send ICMPv6 echo request from node zero to
        # all-nodes (ff02::1).
        #
        packetSize = 1024
        maxPacketCount = 5
        interPacketInterval = ns.core.Seconds(1.)
        ping6 = ns.internet_apps.Ping6Helper()

        # ping6.SetLocal (i.GetAddress (0, 1))
        # ping6.SetRemote(i.GetAddress(1, 1))
        ping6.SetIfIndex (i.GetInterfaceIndex (0))
        ping6.SetRemote (ns.network.Ipv6Address.GetAllNodesMulticast ())

        ping6.SetAttribute("MaxPackets", ns.core.UintegerValue(maxPacketCount))
        ping6.SetAttribute("Interval", ns.core.TimeValue(interPacketInterval))
        ping6.SetAttribute("PacketSize", ns.core.UintegerValue(packetSize))
        apps = ping6.Install(ns.network.NodeContainer(n.Get(0)))
        apps.Start(ns.core.Seconds(2.0))
        apps.Stop(ns.core.Seconds(10.0))

        ascii = ns.network.AsciiTraceHelper()
        csma.EnableAsciiAll(ascii.CreateFileStream("ping6.tr"))
        csma.EnablePcapAll("ping6", True)
            
        print ("Run simulation")
        ns.core.Simulator.Run()
        ns.core.Simulator.Destroy()
        print("Done")


if __name__ == '__main__':
    import sys
    main (sys.argv)


