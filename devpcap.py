
import getopt, sys
import dpkt, pcap

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
    f = open('pcaplog.txt' , 'w')
    z = apply_filter(x) #contains the filter string

    pc = pcap.pcap(name)
#    pc.setfilter(' '.join(args))
    pc.setfilter(z)
    decode = { pcap.DLT_LOOP:dpkt.loopback.Loopback,
               pcap.DLT_NULL:dpkt.loopback.Loopback,
               pcap.DLT_EN10MB:dpkt.ethernet.Ethernet }[pc.datalink()]
    try:
        print 'listening on %s: %s' % (pc.name, pc.filter)
        for ts, pkt in pc:
            print ts, `decode(pkt)`
	    packet = decode(pkt)
	    s = str(packet)
	    f.write(str(ts))
	    f.write('\t')
	    f.write(s)
	    f.write('\n')
    except KeyboardInterrupt:
        nrecv, ndrop, nifdrop = pc.stats()
        print '\n%d packets received by filter' % nrecv
        print '%d packets dropped by kernel' % ndrop

if __name__ == '__main__':
    main()
