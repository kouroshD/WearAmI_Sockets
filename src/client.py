#!/usr/bin/env python

#No yet, change to be used as ROS command, to select the file.

import socket   #for sockets
import sys  #for exit
import time
 
try:
    #create an AF_INET, STREAM socket (TCP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
    print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
    sys.exit();
 
print 'Socket Created'
 
host = socket.gethostname()
port = 8080
 
try:
    #Same computer
    remote_ip = socket.gethostbyname( host )
    #In a network
    remote_ip = "192.168.2.1"
 
except socket.gaierror:
    #could not resolve
    print 'Hostname could not be resolved. Exiting'
    sys.exit()
     
print 'Ip address of ' + host + ' is ' + remote_ip
 
#Connect to remote server
s.connect((remote_ip , port))
 
print 'Socket Connected to ' + host + ' on ip ' + remote_ip


f = open("prova.txt");
i = 0
while(i<300):
    try:
        line = f.readline()
        print i
        s.sendall(line)
        time.sleep(.005);
        i = i +1
    except socket.error:
        #Send failed
        print 'Send failed'
        sys.exit()

print 'Message send successfully'

