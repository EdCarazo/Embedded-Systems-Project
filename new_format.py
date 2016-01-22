import os
import binascii
import socket
import getopt, sys
import dpkt, pcap

PROTO_GOOSE = 0x88B8
PROTO_SV = 0x88BA
PROTO_IP4 = 0x800

writePipe = "/tmp/pipe1"
readPipe = "/tmp/pipe2"

# 1 = GOOSE, 2 = MMS, 3 = SV
def apply_filter(x):
    filterer = {
        1: 'ether proto 0x88B8',
        2: 'tcp port 102',
        3: 'ether proto 0x88BA'
    }
    return filterer.get(x, '')

def usage():
	print >>sys.stderr, 'usage: %s [-i device] [pattern]' % sys.argv[0]
	sys.exit(1)

def main():
	opts, args = getopt.getopt(sys.argv[1:], 'i:h')
	name = None
	for o, a in opts:
		if o == '-i': name = a
		else: usage()
	x = 2 #Test for capping MMS
	z = apply_filter(x) #contains the filter string

	try:
        	os.mkfifo(writePipe)
		os.mkfifo(readPipe)
	except OSError:
		pass
		
	pc = pcap.pcap(name)
	#pc.setfilter(' '.join(args))
	pc.setfilter(z)
	decode = { pcap.DLT_LOOP:dpkt.loopback.Loopback,
			   pcap.DLT_NULL:dpkt.loopback.Loopback,
			   pcap.DLT_EN10MB:dpkt.ethernet.Ethernet }[pc.datalink()]
	f = 0
	while 1:
		while f == 0:
			try:
				p = open(readPipe, 'r')
				params = p.read().split(',')
				f = int(params[0])
				s = params[1]
				d = params[2]
				
#				if f == 2:
#					if s.len() != 0:
#						s_filter = socket.inet_aton(s)
#					if d.len() != 0:
#						d_filter = socket.inet_aton(d)
#					
#					if s.len() != 0 or d.len != 0:
#						ip_filter = 1
#					else: ip_filter = 0
			except IOError:
				f = 0
		
		pc = pcap.pcap(name)
		filter = "%s" % apply_filter(f)
		if s.len() != 0:
			filter += " and src host %s" % s
		elif d.len() != 0:
			filter += " and dst host %s" % d
		pc.setfilter(filter)
	
		while f != 0:
			try:
				for ts, pkt in capt:
					eth = dpkt.ethernet.Ethernet(pkt)
					pipe_message = ""
					addr_filter = 0

					if f == 1:
##					if f == 1 and eth.type == PROTO_GOOSE:
						goose = eth.data
					elif f == 2:
##					elif f == 2 and eth.type == PROTO_IP4:
						ip = eth.data
						tcp = ip.data
						if ip_filter == 0 or (ip_filter == 1 and ((s_filter == ip.src) or (d_filter == ip.dst))):
							# Build string to pipe										
							pipe_message = "%s;%s;%s;%d;%d;%d" % (ts, socket.inet_ntoa(ip.src), socket.inet_ntoa(ip.dst), ip.ttl, tcp.sport, tcp.dport)							

					elif f == 3:
##					elif f == 3 and eth.type == PROTO_SV:
						sv = eth.data
			except:			
		
if __name__ == '__main__':
	main()
