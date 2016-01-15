Filtering options for pcap_exam.py
	
http://www.tcpdump.org/manpages/pcap-filter.7.html

AND NOT OR can be used for combining filters

for example
	src *ip*
	dst *ip*

GOOSE FILTER
 ether proto 0x88B8 
MMS FILTER
 You cannot directly filter MMS protocols while capturing. 
SV
 Runs over ethernet and uses the ethenet ID 0x88BA
