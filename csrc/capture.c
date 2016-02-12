#include <stdio.h>
#include <pcap.h>

struct sniff_ethernet {
	u_char ether_dhost[6];
	u_char ether_shost[6];
	u_short ether_type;
};

char *selectfilter(int f)
{
	static const char f1[] = "0x88B8";
	static const char f2[] = "0x88BA";
	static const char f3[] = "0x800";
	static const char f4[] = "0x88F7";

	switch (f)
	{
		case 1:
			return &f1;
		case 2:
			return &f2;
		case 3:
			return &f3;
		case 4:
			return &f4;

		default:
			return 0;
	}

}

int main(int argc, char *argv[])
{
	pcap_t *capture;
	char *dev  = "eth0";
	char *errbuf;
	char *filter = "tcp port 80";
	struct bpf_program filt;

	struct pcap_pkthdr header;
	const struct sniff_ethernet *eth;
	const u_char *packet;

	capture = pcap_open_live(dev, BUFSIZ, 1, 1000, errbuf);

	if(!capture)
	{
		fprintf(stderr, "Couldn't open device", dev, errbuf);
		return(2);
	}

//	filter = selectfilter(2);
	if (pcap_compile(capture, &filt, filter, 0, 0) == -1)
	{
		fprintf(stderr, "Unable to compile filter", filter, errbuf);
		return (-1);
	}

	if (pcap_setfilter(capture, &filt) == -1)
	{
		fprintf(stderr, "Unable to set filter", filt, errbuf);
		return (-2);
	}

	packet = pcap_next(capture, &header);

	eth = (struct sniff_ethernet *)(packet);

	printf("Header length: [%u], Ethernet src [%s] and dst [%s]\n", header.len, eth->ether_shost, eth->ether_dhost);

	pcap_close(capture);

	return 0;
}
