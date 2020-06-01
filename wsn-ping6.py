
#  Network topology
#  
#         n0    n1
#         |     |
#         =================
#          WSN (802.15.4)
#  
#   - ICMPv6 echo request flows from n0 to n1 and back with ICMPv6 echo reply
#   - DropTail queues 
#   - Tracing of queues and packet receptions to file "wsn-ping6.tr"
#  
#   This example is based on the "ping6.cc" example.


import ns3
import ns.core
import ns.network
import ns.internet
import ns.internet_apps
import ns.mobility
import ns.lr_wpan

def main(argv):
		print ("Ping6WsnExample")

		cmd = ns.core.CommandLine()
		cmd.AddValue ("verbose", "turn on log components")
		cmd.verbose = False
		cmd.Parse (argv)
		verbose = bool(cmd.verbose)

		if verbose:
			ns.core.LogComponentEnable ("Ping6WsnExample", ns.core.LOG_LEVEL_INFO)
			ns.core.LogComponentEnable ("Ipv6EndPointDemux", ns.core.LOG_LEVEL_ALL)
			ns.core.LogComponentEnable ("Ipv6L3Protocol", ns.core.LOG_LEVEL_ALL)
			ns.core.LogComponentEnable ("Ipv6StaticRouting", ns.core.LOG_LEVEL_ALL)      
			ns.core.LogComponentEnable ("Ipv6ListRouting", ns.core.LOG_LEVEL_ALL)
			ns.core.LogComponentEnable ("Ipv6Interface", ns.core.LOG_LEVEL_ALL)
			ns.core.LogComponentEnable ("Icmpv6L4Protocol", ns.core.LOG_LEVEL_ALL)
			ns.core.LogComponentEnable ("Ping6Application", ns.core.LOG_LEVEL_ALL)
			ns.core.LogComponentEnable ("NdiscCache", ns.core.LOG_LEVEL_ALL)
			ns.core.LogComponentEnable ("SixLowPanNetDevice", ns.core.LOG_LEVEL_ALL)

		print ("Create nodes.")
		nodes = ns.network.NodeContainer()
		nodes.Create(2)

		#Set seed for random numbers
		ns.core.SeedManager.SetSeed (167)

		# Install mobility
		mobility=ns.mobility.MobilityHelper ()
		mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel")

		nodesPositionAlloc = ns.mobility.ListPositionAllocator()
		nodesPositionAlloc.Add( ns.core.Vector3D (0.0, 0.0, 0.0))
		nodesPositionAlloc.Add( ns.core.Vector3D (50.0, 0.0, 0.0))
		mobility.SetPositionAllocator (nodesPositionAlloc)
		mobility.Install (nodes)

		print ("Create channels.")
		lrWpanHelper = ns.lr_wpan.LrWpanHelper()
		# Add and install the LrWpanNetDevice for each node
		# lrWpanHelper.EnableLogComponents();
		devContainer = lrWpanHelper.Install(nodes)
		lrWpanHelper.AssociateToPan (devContainer, 10)

		print (f'Created {devContainer.GetN()} devices\n')
		print (f'There are {nodes.GetN()} nodes\n')

		# Install IPv4/IPv6 stack
		print ("Install Internet Stack.")
		internetv6 = ns.internet.InternetStackHelper()
		internetv6.SetIpv4StackInstall (False)
		internetv6.Install (nodes)

		# Install 6LowPan Layer
		print ("Install 6LowPAN.")
		sixlowpan = ns3.SixLowPanHelper()
		six1 = sixlowpan.Install (devContainer)

		print ("Assign addresses.")
		ipv6=ns.internet.Ipv6AddressHelper()
		ipv6.SetBase (ns.network.Ipv6Address ("2001:1::"), ns.network.Ipv6Prefix (64))
		i = ipv6.Assign(six1)

		print ("Create Applications.")

		# Create a Ping6 application to send ICMPv6 echo request from node zero to
		#   all-nodes (ff02::1).
		#
		packetSize =10
		maxPacketCount = 5
		interPacketInterval = ns.core.TimeValue(ns.core.Seconds (1.))
		ping6 = ns.internet_apps.Ping6Helper ()
		ping6.SetLocal (i.GetAddress (0, 1))
		ping6.SetRemote (i.GetAddress (1, 1))
		#ping6.SetRemote (ns.network.Ipv6Address.GetAllNodesMulticast ());

		ping6.SetAttribute ("MaxPackets", ns.core.UintegerValue (maxPacketCount))
		ping6.SetAttribute ("Interval", ns.core.TimeValue (interPacketInterval))
		ping6.SetAttribute ("PacketSize", ns.core.UintegerValue (packetSize))

		apps = ping6.Install(ns.network.NodeContainer(nodes.Get(0)))

		apps.Start (ns.core.Seconds (2.0))
		apps.Stop (ns.core.Seconds (10.0))

		ascii = ns.network.AsciiTraceHelper() 
		lrWpanHelper.EnableAsciiAll (ascii.CreateFileStream ("ping6wsn.tr"))
		lrWpanHelper.EnablePcapAll ("ping6wsn", True)

		print ("Run Simulation.")
		ns.core.Simulator.Run ()
		ns.core.Simulator.Destroy ()
		print ("Done.")

if __name__ == '__main__':
    import sys
    main (sys.argv)