import time
import os
import binascii
import socket
import getopt, sys
import dpkt, pcap
import posix_ipc

PROTO_GOOSE = 0x88B8
PROTO_SV = 0x88BA
PROTO_IP4 = 0x800

readPipe = "/tmp/pipe"
messageQue = "/msg_que"

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

	mq = posix_ipc.MessageQueue(messageQue, posix_ipc.O_CREAT)

	try:
		os.mkfifo(readPipe)
		pass
	except OSError:
		print "mkfifo readpipe"
		pass

	log_name = "./.log/log_%s.txt" % (time.strftime("%Y%m%d_%H%M%S"))
	try:
		logf = open(log_name, 'w')		
	except OSError:
		print "couldn't open logfile"
		sys.exit(1)
		
	pc = pcap.pcap(name)

	decode = { pcap.DLT_LOOP:dpkt.loopback.Loopback,
			   pcap.DLT_NULL:dpkt.loopback.Loopback,
			   pcap.DLT_EN10MB:dpkt.ethernet.Ethernet }[pc.datalink()]
	f = 0

	print ("Wait parameters")

	p = open(readPipe, 'r')
	while 1:
		while f == 0:
			## DEBUG print
			try:	
				params = p.read().split(',')
				f = int(params[0])
				s = params[1]
				d = params[2]
				sf = 0
				df = 0
				
		## DEBUG PARAMS		
				##f = 2
				##s = ""
				##d = "192.168.69.24"
				
				if len(s) != 0:
					sf = socket.inet_aton(s)
				if len(d) != 0:
					df = socket.inet_aton(d)
			except IOError:
				f = 0
		
		print ('Starting capture')
		mq = posix_ipc.MessageQueue(messageQue)
		while f != 0:
			try:
				for ts, pkt in pc:
						eth = dpkt.ethernet.Ethernet(pkt)
					
						if f == 1 and eth.type == PROTO_GOOSE:
							goose = eth.data
							pipe_message = "%s,%d,%s" % ("{0:.6f}".format(ts), goose.len, goose.data)
							mq.send(pipe_message)
							logf.write(pipe_message)
							logf.write('\n')
				
							print "GOOSE %d\n" % (goose.len)

						elif f == 2 and eth.type == PROTO_IP4:
							ip = eth.data
							if ip.p == dpkt.ip.IP_PROTO_TCP:
								tcp = ip.data
								if tcp.sport == 102 or tcp.dport == 102:
									if (len(s) == 0 and len(d) == 0) or (len(s) != 0 and sf == ip.src) or (len(d) != 0 and df == ip.dst): 
										## Build string to pipe										
										pipe_message = "%s,%s,%s,%d,%d,%d" % ("{0:.6f}".format(ts), socket.inet_ntoa(ip.src), socket.inet_ntoa(ip.dst), ip.ttl, tcp.sport, tcp.dport)							
										mq.send(pipe_message)
										logf.write(pipe_message)
										logf.write('\n')
																
										print pipe_message
	
						elif f == 3 and eth.type == PROTO_SV:
							sv = eth.data
							pipe_message = "%s,%d,%s" % ("{0:.6f}".format(ts), sv.len, sv.data)
							mq.send(pipe_message)
							logf.write(pipe_message)
							logf.write('\n')
							print "SV %d\n" % (sv.len)
						try:
							params = p.read().split(',')
							f = int(params[0])
							if f == 0:
								break
						except:
							pass
						
			except KeyboardInterrupt:
				mq.close()
				mq.unlink()
				logf.close()
				readPipe.close()
				return -1
		mq.close()
	mq.unlink
if __name__ == '__main__':
	main()
