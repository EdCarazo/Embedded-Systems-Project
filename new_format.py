import time
import os
import binascii
import socket
import getopt, sys
import dpkt, pcap
import posix_ipc

PROTO_GOOSE = 0x88B8 ##ethernet proto value for GOOSE packets
PROTO_SV = 0x88BA ##Ethernet proto value for the Sampled Values packets
PROTO_IP4 = 0x800 ##Ethernet proto value for IPv4 Packages
PROTO_TIMESYNC = 0x88F7 ## Ethernet proto value for PTP based timesync over ethernet

readPipe = "/tmp/pipe" ##containing pipe for sending parameters
messageQue = "/msg_que" ##containing the messageQueue

def usage():
	print >>sys.stderr, 'usage: %s [-i device] [pattern]' % sys.argv[0] ##prints the usage message with necessary arguments listed
	sys.exit(1)

def main():
	opts, args = getopt.getopt(sys.argv[1:], 'i:h') ##fetches command line arguments
	name = None ##contains the name of the interface that is used for capture
	countPackets = 0 ##Variable containing the number of packets we want to capture

	for o, a in opts:
		if o == '-i': name = a 
		else: usage()

	mq = posix_ipc.MessageQueue(messageQue, posix_ipc.O_CREAT) ##Creates the messaque

	try:
		os.mkfifo(readPipe) ##reads the pipe
		pass
	except OSError:
		print "mkfifo readpipe"
		pass

	log_name = "./.log/log_%s.txt" % (time.strftime("%Y%m%d_%H%M%S")) ##contains the log file name and format
	try:
		logf = open(log_name, 'w')	##Opens logfile for writing	
	except OSError:
		print "couldn't open logfile" ##error message if opening logfile fails
		sys.exit(1)
		
	pc = pcap.pcap(name) ##Prepare pcap for specified interface
	f = 0

	print ("Wait parameters")

	p = open(readPipe, 'r') ##Opens the pipe for reading to receive parameters from GUI
	while 1:
		while f == 0:
			## DEBUG print
			try:	
				params = p.read().split(',') ##read parameters sent by GUI
				f = int(params[0]) ##Contains the Protocol number value for selecting protocol to capture
				s = params[1] ## contains the source IP address for the packages we want to capture
				d = params[2] ##contains the destination IP address for the packages we want to capture
				sf = 0
				df = 0
				sdf = int(params[3]) ##contains the count of packets the software will capture before quiting capture

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
		mq = posix_ipc.MessageQueue(messageQue) ##creates messageQueue for sending data to the GUI
		while f != 0:
			try:
				for ts, pkt in pc or (countPackets < sdf and sdf != 0):
						eth = dpkt.ethernet.Ethernet(pkt)
					
						if f == 1 and eth.type == PROTO_GOOSE:
							goose = eth.data ##Variable containing all the data contained in a packet captured by the interface
							countPackets +=1
							pipe_message = "%d,%s,%d,%s" % (countPackets,"{0:.6f}".format(ts), goose.len, goose.data) ##Formats the message for GUI and logs
							mq.send(pipe_message) ##Sends the data to the GUI through messageQueue
							logf.write(pipe_message) ##Writes the data into Logfile
							logf.write('\n')
				
							print "GOOSE %d\n" % (goose.len) ##prints goose packet length in the terminal


						elif f == 2 and eth.type == PROTO_IP4:
							ip = eth.data
							if ip.p == dpkt.ip.IP_PROTO_TCP:
								tcp = ip.data
								if tcp.sport == 102 or tcp.dport == 102:
									if (len(s) == 0 and len(d) == 0) or (len(s) != 0 and sf == ip.src) or (len(d) != 0 and df == ip.dst): 
										## Build string to pipe										
										countPackets +=1 ##increment packet counter
										pipe_message = "%d,%s,%s,%s,%d,%d,%d" % (countPackets,"{0:.6f}".format(ts), socket.inet_ntoa(ip.src), socket.inet_ntoa(ip.dst), ip.ttl, tcp.sport, tcp.dport) ##format string for sending through pipe						
										mq.send(pipe_message) ##Send message through messageQueue
										logf.write(pipe_message) ##write message into log file
										logf.write('\n') ##add new line to log
																
										print pipe_message ##print out the message in terminal screen

	
						elif f == 3 and eth.type == PROTO_SV:
							sv = eth.data
							countPackets +=1
							pipe_message = "%d,%s,%d,%s" % (countPackets, "{0:.6f}".format(ts), sv.len, sv.data)
							mq.send(pipe_message)
							logf.write(pipe_message)
							logf.write('\n')
							print "SV %d\n" % (sv.len)


						elif f == 4 and (eth.type == PROTO_IP4 or eth.type == PROTO_TIMESYNC):
							ip = eth.data
							if ip.p == dpkt.ip.IP_PROTO_UDP:
								udp = ip.data
								if udp.sport == 123 or udp.dport == 123 or udp.sport == 319 or udp.dport == 319 or udp.sport == 320 or udp.dport == 320:
									if (len(s) == 0 and len(d) == 0) or (len(s) != 0 and sf == ip.src) or (len(d) != 0 and df == ip.dst): 
										## Build string to pipe										
										countPackets +=1
										pipe_message = "%d,%s,%s,%s,%d,%d,%d" % (countPackets, "{0:.6f}".format(ts), socket.inet_ntoa(ip.src), socket.inet_ntoa(ip.dst), ip.ttl, udp.sport, udp.dport)							
										mq.send(pipe_message)
										logf.write(pipe_message)
										logf.write('\n')
																
										print pipe_message


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
		mq.close() ##Close the messageQueue
	mq.unlink
if __name__ == '__main__':
	main()
