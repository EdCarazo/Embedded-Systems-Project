#include <stdio.h>
#include <pcap.h>

int main(int argc, char *argv[])
{
	pcap_t *capture;
	char *dev  = "eth0";
	char *errbuf;

	capture = pcap_open_live(dev, BUFSIZ, 1, 1000, errbuf);

	if(!capture)
	{
		fprintf(stderr, "Couldn't open device", dev, errbuf);
		return(2);
	}

	
