import binascii
import socket
import getopt, sys
import dpkt, pcap

def usage():
	print >>sys.stderr, 'usage: %s [-i device] [pattern]' % sys.argv[0]
	sys.exit(1)

def main():
	opts, args = getopt.getopt(sys.argv[1:], 'i:h')
	name = None
	for o, a in opts:
		if o == '-i': name = a
		else: usage()
	
	f = open('pcaplog.txt' , 'w')
		
	pc = pcap.pcap(name)
	pc.setfilter(' '.join(args))
	decode = { pcap.DLT_LOOP:dpkt.loopback.Loopback,
			   pcap.DLT_NULL:dpkt.loopback.Loopback,
			   pcap.DLT_EN10MB:dpkt.ethernet.Ethernet }[pc.datalink()]
	try:
		print 'listening on %s: %s' % (pc.name, pc.filter)
		for ts, pkt in pc:
			print ts, `decode(pkt)`
			eth = dpkt.ethernet.Ethernet(pkt)
			ip = eth.data
			ip_filter = 0
			
			if ip_filter != 0:
				_ip_filter = socket.inet_aton(ip_filter)
			
			if ip.p == dpkt.ip.IP_PROTO_ICMP:
				print "PING!!"
			elif (ip.p == dpkt.ip.IP_PROTO_TCP) and (ip_filter == 0 or (_ip_filter == ip.dst or _ip_filter == ip.src )):
				tcp = ip.data
				pipe_message = socket.inet_ntoa(ip.src),';', socket.inet_ntoa(ip.dst),';',ip.ttl,';',tcp.sport,';',tcp.dport,';',tcp.data.id,'\n'
				
			print socket.inet_ntoa(ip.src), '\t', socket.inet_ntoa(ip.dst), '\t', tcp.data.id

			#packet = decode(pkt)
			#s = str(packet)
			#f.write(str(ts))
			#f.write('\t')
			#f.write(s)
			#f.write('\n')
	except KeyboardInterrupt:
		nrecv, ndrop, nifdrop = pc.stats()
		print '\n%d packets received by filter' % nrecv
		print '%d packets dropped by kernel' % ndrop

if __name__ == '__main__':
	main()
