
# Network topology
#
#      n0              n1
#      |               |
#      =================
#             LAN
#
# UDP flows from n0 to n1

import ns3
import ns.core
import ns.csma
import ns.internet
import ns.network


def ReceivePacket (socket):

	print ("Received one packet!")
	packet = socket.Recv()
	tosTag = ns3.SocketIpTosTag()

	if packet.RemovePacketTag(tosTag):
		print (" TOS = ", tosTag.GetTos ())
	
	ttlTag = ns3.SocketIpTtlTag()
	
	if packet.RemovePacketTag(ttlTag):
		print (" TTL = ", ttlTag.GetTtl ())


def SendPacket (args, socket, pktSize, pktCount, pktInterval):
  	
	if pktCount > 0 :
		socket.Send(ns.network.Packet(pktSize))
		ns.core.Simulator.Schedule(pktInterval, SendPacket, args, socket, pktSize, pktCount -1 , pktInterval)
				
	else :
		socket.Close ()		



def main(argv):
	
#
# Allow the user to override any of the defaults and the above Bind() at
# run-time, via command-line arguments
#
	cmd = ns.core.CommandLine()

	cmd.packetSize = 1024 
	cmd.packetCount = 10
	cmd.packetInterval = 1.0

# Socket options for IPv4, currently TOS, TTL, RECVTOS, and RECVTTL
	cmd.ipTos = 0
	cmd.ipRecvTos = True 
	cmd.ipTtl = 0
	cmd.ipRecvTtl = True 

	cmd.AddValue ("PacketSize", "Packet size in bytes")
	cmd.AddValue ("PacketCount", "Number of packets to send")
	cmd.AddValue ("Interval", "Interval between packets")
	cmd.AddValue ("IP_TOS", "IP_TOS")
	cmd.AddValue ("IP_RECVTOS", "IP_RECVTOS")
	cmd.AddValue ("IP_TTL", "IP_TTL")
	cmd.AddValue ("IP_RECVTTL", "IP_RECVTTL")
	cmd.Parse(argv)

	packetSize = int(cmd.packetSize) 
	packetCount = int(cmd.packetCount)
	packetInterval = float(cmd.packetInterval)
	ipTos = int(cmd.ipTos)
	ipRecvTos = bool(cmd.ipRecvTos) 
	ipTtl = int(cmd.ipTtl)
	ipRecvTtl = bool(cmd.ipRecvTtl) 

	print ("Create nodes.")
	n = ns.network.NodeContainer()
	n.Create(2)

	internet = ns.internet.InternetStackHelper()
	internet.Install (n)

	print ("Create channels.")
	csma = ns.csma.CsmaHelper()
	csma.SetChannelAttribute("DataRate", ns.network.DataRateValue(ns.network.DataRate(5000000)))
	csma.SetChannelAttribute("Delay", ns.core.TimeValue(ns.core.MilliSeconds(2)))
	csma.SetDeviceAttribute("Mtu", ns.core.UintegerValue(1400))
	d = csma.Install(n)  

	print ("Assign IP addresses.")
	ipv4 = ns.internet.Ipv4AddressHelper()
	ipv4.SetBase(ns.network.Ipv4Address("10.1.1.0"), ns.network.Ipv4Mask("255.255.255.0"))
	i = ipv4.Assign(d)
	serverAddress = ns.network.Address (i.GetAddress(1))

	print ("Create sockets.")
	# Receiver socket on n1
	tid = ns3.TypeId.LookupByName("ns3::UdpSocketFactory")
	recvSink = ns3.Socket.CreateSocket(n.Get(1), tid)
	local= ns3.InetSocketAddress(ns3.Ipv4Address.GetAny(), 4477)
	recvSink.SetIpRecvTos(ipRecvTos)
	recvSink.SetIpRecvTtl(ipRecvTtl)
	recvSink.Bind(local)
	recvSink.SetRecvCallback (ReceivePacket)
	
	# Sender socket on n0
	source = ns3.Socket.CreateSocket(n.Get(0), tid)
	remote = ns.network.InetSocketAddress(i.GetAddress(1), 4477)

	# Set socket options, it is also possible to set the options after the socket has been created/connected.
	if ipTos > 0:
		source.SetIpTos (ipTos)

	if ipTtl > 0:
		source.SetIpTtl (ipTtl)
	source.Connect (remote)

	ascii = ns.network.AsciiTraceHelper ()
	csma.EnableAsciiAll(ascii.CreateFileStream("socket-options-ipv4.tr"))
	csma.EnablePcapAll ("socket-options-ipv4", False)
	
	# Schedule SendPacket
	interPacketInterval = ns.core.Seconds(packetInterval)
	ns.core.Simulator.ScheduleWithContext (source.GetNode ().GetId (), ns.core.Seconds (1.0), SendPacket, source, packetSize, packetCount, interPacketInterval)

	print ("Run Simulation.")
	ns.core.Simulator.Run()
	ns.core.Simulator.Destroy()
	print ("Done.")


if __name__ == '__main__':
    import sys
    main (sys.argv)
