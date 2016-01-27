import cPickle
import os, sys

readPipe = "/tmp/pipe2"
#os.mkfifo(readPipe)
print "Listening...\n"
try:
#   while True:
        rp = open(readPipe, 'r')
        response = rp.read()
#       ts = response.split(';')[0]
#       print "Timestamp: %s\n" %ts
        print "Received: \n%s" %response
        rp.close()
except KeyboardInterrupt:
    print "\nTerminated by user"
