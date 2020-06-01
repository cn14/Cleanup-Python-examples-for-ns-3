#  Network topology
#  #
#  #             n0   R    n1
#  #             |    _    |
#  #             ====|_|====
#  #                router
#  # - R sends RA to n0's subnet (2001:1::/64);
#  # - R sends RA to n1's subnet (2001:2::/64);
#  # - n0 ping6 n1.
#  #
#  # - Tracing of queues and packet receptions to file "radvd.tr"

import ns.core
import ns.internet
import ns.csma


def main(argv):
        print ("RadvdExample")

        cmd = ns.core.CommandLine ()
        cmd.AddValue ("verbose", "turn on log components")
        cmd.verbose = False
        cmd.Parse (argv)
        verbose = bool(cmd.verbose)

        if verbose:
          ns.core.LogComponentEnable ("Ipv6L3Protocol", ns.core.LOG_LEVEL_ALL)
          ns.core.LogComponentEnable ("Ipv6RawSocketImpl", ns.core.LOG_LEVEL_ALL)
          ns.core.LogComponentEnable ("Icmpv6L4Protocol", ns.core.LOG_LEVEL_ALL)
          ns.core.LogComponentEnable ("Ipv6StaticRouting", ns.core.LOG_LEVEL_ALL)
          ns.core.LogComponentEnable ("Ipv6Interface", ns.core.LOG_LEVEL_ALL)
          ns.core.LogComponentEnable ("RadvdApplication", ns.core.LOG_LEVEL_ALL)
          ns.core.LogComponentEnable ("Ping6Application", ns.core.LOG_LEVEL_ALL)
            
        print ("Create nodes.")
        n0 = ns.network.Node()
        r  = ns.network.Node()
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
        internetv6.Install(all)

        print ("Create channels.")
        csma = ns.csma.CsmaHelper()
        csma.SetChannelAttribute ("DataRate", ns.network.DataRateValue(ns.network.DataRate(5000000)))
        csma.SetChannelAttribute ("Delay", ns.core.TimeValue(ns.core.MilliSeconds(2)))
        d1 = csma.Install (net1) # n0 - R 
        d2 = csma.Install (net2) # R - n1 

        print ("Create networks and assign IPv6 Addresses.")
        ipv6 = ns.internet.Ipv6AddressHelper()

        # first subnet 
        ipv6.SetBase (ns.network.Ipv6Address("2001:1::"), ns.network.Ipv6Prefix (64))
        tmp = ns.network.NetDeviceContainer()
        tmp.Add (d1.Get (0)) # n0
        iic1 = ipv6.AssignWithoutAddress (tmp) # n0 interface

        tmp2 = ns.network.NetDeviceContainer()
        tmp2.Add (d1.Get (1)) # R 
        iicr1 = ipv6.Assign (tmp2) # R interface to the first subnet is just statically assigned 
        iicr1.SetForwarding (0, True)
        iic1.Add (iicr1)

        # second subnet R - n1
        ipv6.SetBase (ns.network.Ipv6Address ("2001:2::"), ns.network.Ipv6Prefix (64))
        tmp3 = ns.network.NetDeviceContainer()
        tmp3.Add (d2.Get (0)) # R 
        iicr2 = ipv6.Assign (tmp3)# R interface
        iicr2.SetForwarding (0, True)

        tmp4 = ns.network.NetDeviceContainer()
        tmp4.Add (d2.Get (1)) # n1
        iic2 = ipv6.AssignWithoutAddress (tmp4)
        iic2.Add (iicr2)

        # radvd configuration
        radvdHelper = ns.internet_apps.RadvdHelper ()

        # R interface (n0 - R) 
        # n0 will receive unsolicited (periodic) RA 
        radvdHelper.AddAnnouncedPrefix (iic1.GetInterfaceIndex (1), ns.network.Ipv6Address("2001:1::0"), 64)

        # R interface (R - n1) 
        # n1 will have to use RS, as RA are not sent automatically
        radvdHelper.AddAnnouncedPrefix(iic2.GetInterfaceIndex (1), ns.network.Ipv6Address("2001:2::0"), 64)
        radvdHelper.GetRadvdInterface (iic2.GetInterfaceIndex (1)).SetSendAdvert (False)

        radvdApps = radvdHelper.Install (r)
        radvdApps.Start (ns.core.Seconds (1.0))
        radvdApps.Stop (ns.core.Seconds (10.0))

        # Create a Ping6 application to send ICMPv6 echo request from n0 to n1 via R 
        packetSize = 1024
        maxPacketCount = 5
        interPacketInterval = ns.core.Seconds (1.)
        ping6 = ns.internet_apps.Ping6Helper() 

        # ping6.SetLocal (iic1.GetAddress (0, 1));
        ping6.SetRemote (ns.network.Ipv6Address ("2001:2::200:ff:fe00:4")) # should be n1 address after autoconfiguration
        ping6.SetIfIndex (iic1.GetInterfaceIndex (0))

        ping6.SetAttribute ("MaxPackets", ns.core.UintegerValue (maxPacketCount))
        ping6.SetAttribute ("Interval", ns.core.TimeValue (interPacketInterval))
        ping6.SetAttribute ("PacketSize", ns.core.UintegerValue (packetSize))
        apps = ping6.Install(ns.network.NodeContainer(net1.Get(0)))
        apps.Start (ns.core.Seconds (2.0))
        apps.Stop (ns.core.Seconds (7.0))

        ascii = ns.network.AsciiTraceHelper ()
        csma.EnableAsciiAll (ascii.CreateFileStream ("radvd.tr"))
        csma.EnablePcapAll ("radvd", True)

        print ("Run Simulation.")
        ns.core.Simulator.Run ()
        ns.core.Simulator.Destroy ()
        print ("Done.")


if __name__ == '__main__':
    import sys
    main (sys.argv)




