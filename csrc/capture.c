#include <stdio.h>
#include <pcap.h>

#define selectFilter(x)	filter[x-1]

static const char *filter[4] = {"ether proto 0x88B8", "ether proto 0x900 and tcp port 102", \
"ether proto 0x88BA", "udp port 123 or udp port 319 or udp port 320 or ether proto 0x88F7"};
//filter[0] = "ether proto 0x88B8"; // GOOSE
//filter[2] = "ether proto 0x88BA"; // SV
//filter[1] = "ether proto 0x800 and tcp port 102";  // MMS
//filter[3] = "udp port 123 or udp port 319 or udp port 320 or ether proto 0x88F7"; // TS (NTP, PTP)

struct sniff_ethernet {
	u_char ether_dhost[6];
	u_char ether_shost[6];
	u_short ether_type;
};

int main(int argc, char *argv[])
{
	int i;
	pcap_t *capture;
	char *dev  = "eth0";
	char *errbuf;
//	char *filter = "tcp port 80";
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
	if (pcap_compile(capture, &filt, selectFilter(1), 0, 0) == -1)
	{
		fprintf(stderr, "Unable to compile filter", filter, errbuf);
		return (-1);
	}

	if (pcap_setfilter(capture, &filt) == -1)
	{
		fprintf(stderr, "Unable to set filter", filt, errbuf);
		return (-2);
	}

	for(i = 0; i < 10000; i ++)
	{
		packet = pcap_next(capture, &header);

		printf("Header length [%u]\n", header.len);

		eth = (struct sniff_ethernet *)(packet);

		printf("Header length: [%u], Ethernet src [%s] and dst [%s]\n", header.len, eth->ether_shost, eth->ether_dhost);
	}
	pcap_close(capture);

	return 0;
}
