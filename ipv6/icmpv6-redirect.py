# Network topology
#
#             STA2
#              |
#              |
#   R1         R2
#   |          |
#   |          |
#   ------------
#           |
#           |
#          STA 1
#
# - Initial configuration :
#         - STA1 default route : R1
#         - R1 static route to STA2 : R2
#         - STA2 default route : R2
# - STA1 send Echo Request to STA2 using its default route to R1
# - R1 receive Echo Request from STA1, and forward it to R2
# - R1 send an ICMPv6 Redirection to STA1 with Target STA2 and Destination R2
# - Next Echo Request from STA1 to STA2 are directly sent to R2

import ns.network
import ns.core
import ns.internet
import ns.internet_apps
import ns.csma


def main(argv):
		cmd = ns.core.CommandLine()
		cmd.AddValue ("verbose", "turn on log components")
		cmd.verbose = False
		cmd.Parse(argv)
		verbose = bool(cmd.verbose)

		if verbose :
			ns.core.LogComponentEnable("Icmpv6RedirectExample", ns.core.LOG_LEVEL_INFO)
			ns.core.LogComponentEnable("Icmpv6L4Protocol", ns.core.LOG_LEVEL_INFO)
			ns.core.LogComponentEnable("Ipv6L3Protocol", ns.core.LOG_LEVEL_ALL)
			ns.core.LogComponentEnable("Ipv6StaticRouting", ns.core.LOG_LEVEL_ALL)
			ns.core.LogComponentEnable("Ipv6Interface", ns.core.LOG_LEVEL_ALL)
			ns.core.LogComponentEnable("Icmpv6L4Protocol", ns.core.LOG_LEVEL_ALL)
			ns.core.LogComponentEnable("NdiscCache", ns.core.LOG_LEVEL_ALL)

		print ("Creat nodes.")
		sta1 = ns.network.Node()
		r1 = ns.network.Node()
		r2 = ns.network.Node()
		sta2 = ns.network.Node()

		net1 = ns.network.NodeContainer()
		net1.Add(sta1)
		net1.Add(r1)
		net1.Add(r2)
		net2 = ns.network.NodeContainer()
		net2.Add(r2)
		net2.Add(sta2)
		all = ns.network.NodeContainer()  
		all.Add(sta1)
		all.Add(r1)
		all.Add(r2)
		all.Add(sta2)

		internetv6 = ns.internet.InternetStackHelper()
		internetv6.Install(all)

		print ("Create channels.")
		csma = ns.csma.CsmaHelper()
		csma.SetChannelAttribute("DataRate", ns.network.DataRateValue(ns.network.DataRate(5000000)))
		csma.SetChannelAttribute("Delay", ns.core.TimeValue(ns.core.MilliSeconds(2)))
		ndc1 = csma.Install(net1)
		ndc2 = csma.Install(net2)

		print ("Assign IPv6 Addresses.")
		ipv6 = ns.internet.Ipv6AddressHelper()
		ipv6.SetBase (ns.network.Ipv6Address ("2001:1::"), ns.network.Ipv6Prefix (64))
		iic1 = ipv6.Assign (ndc1)
		iic1.SetForwarding (2, True)
		iic1.SetForwarding (1, True)
		iic1.SetDefaultRouteInAllNodes (1)

		ipv6.SetBase (ns.network.Ipv6Address ("2001:2::"), ns.network.Ipv6Prefix (64))
		iic2 = ipv6.Assign (ndc2)
		iic2.SetForwarding (0, True)
		iic2.SetDefaultRouteInAllNodes (0)

		routingHelper = ns.internet.Ipv6StaticRoutingHelper()

		# manually inject a static route to the second router.
		routing = routingHelper.GetStaticRouting (r1.GetObject(ns.internet.Ipv6.GetTypeId()))
		routing.AddHostRouteTo (iic2.GetAddress (1, 1), iic1.GetAddress (2, 0), iic1.GetInterfaceIndex (1))

		routingStream = ns.network.OutputStreamWrapper ("icmpv6-redirect.routes", ns.network.STD_IOS_OUT)
		routingHelper.PrintRoutingTableAt (ns.core.Seconds (0.0), r1, routingStream)
		routingHelper.PrintRoutingTableAt (ns.core.Seconds (3.0), sta1, routingStream)

		print ("Create Applications.")
		packetSize = 1024
		maxPacketCount = 5
		interPacketInterval = ns.core.Seconds (1.)
		ping6 = ns.internet_apps.Ping6Helper()

		ping6.SetLocal (iic1.GetAddress (0, 1))
		ping6.SetRemote (iic2.GetAddress (1, 1))
		ping6.SetAttribute ("MaxPackets", ns.core.UintegerValue (maxPacketCount))
		ping6.SetAttribute ("Interval", ns.core.TimeValue (interPacketInterval))
		ping6.SetAttribute ("PacketSize", ns.core.UintegerValue (packetSize))
		apps = ping6.Install(ns.network.NodeContainer(sta1))
		apps.Start (ns.core.Seconds (2.0))
		apps.Stop (ns.core.Seconds (10.0))

		ascii = ns.network.AsciiTraceHelper()
		csma.EnableAsciiAll (ascii.CreateFileStream ("icmpv6-redirect.tr"))
		csma.EnablePcapAll ("icmpv6-redirect", True)

		# Now, do the actual simulation.
		print ("Run Simulation.")
		ns.core.Simulator.Run ()
		ns.core.Simulator.Destroy ()
		print ("Done.")


if __name__ == '__main__':
    import sys
    main (sys.argv)



