#!/usr/bin/env python

import sys
import rospy
from geometry_msgs.msg import Point, Pose, Quaternion, Twist, Vector3
import signal
import socket               # Import socket module
import select
import Queue
import time
import os

def signal_handler(signal, frame):
	"""Signal handler of the data """
        print('Signal Handler, you pressed Ctrl+C!')
        print('Server will be closed')
        sys.exit(0)
        #conn.close()


def decode(line):
        """Acceleration decodification"""
        """Return values: success, option, value1, value2, value3"""
        """option = 0 for aceleration data, then value1 = acceleration x, value2 = acceleration y, value3 = acceleration z"""
        """option = 1 for gyroscope data, then value1 = rotation x, value2 = rotationy, value3 = rotation z"""
        line_list = line.split(";")
        if(line_list[0] == 'a'):
                if(len(line_list)==5 and line_list[4] != ''):
                        x = line_list[2]
                        y = line_list[3]
                        z = line_list[4]
                        return True,0,x,y,z
        if(line_list[0] == 'y'):
                if(len(line_list)==5 and line_list[4] != ''):
                        x = line_list[2]
                        y = line_list[3]
                        z = line_list[4]
                        return True,1,x,y,z
        return False,0,0,0,0

def main():

	counterROS=0
        innerLoopCounter=0

	counterPack=0
	counterPackOld=0
	listDataCounter=0
	outputCounter=0;

        completeName = os.path.join('/home/nasa/Datalog/ICRA_TESTS',"67_Acc_data"+".txt")
        file = open(completeName, "a")

        pub = rospy.Publisher('wearami_acc', Pose, queue_size=10)
        pub2 = rospy.Publisher('wearami_gyro', Pose, queue_size=10)
        
	rospy.init_node('wearami_socket', anonymous=True)
	r = rospy.Rate(40) # period
	signal.signal(signal.SIGINT, signal_handler)
	
        print('Press Ctrl+C to exit of this server')
        #A server must perform the sequence socket(), bind(), listen(), accept()
        HOST = socket.gethostname()   # Get local machine name
        PORT = 8080                # Reserve a port for your service.


	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setblocking(0)

        #Running an example several times with too small delay between executions, could lead to this error:
        #socket.error: [Errno 98] Address already in use
        # There is a socket flag to set, in order to prevent this, socket.SO_REUSEADDR:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('', PORT))

        # Listen for incoming connections
        server.listen(5)

        # Sockets from which we expect to read
        inputs = [ server ]

        # Sockets to which we expect to write
        outputs = [ ]

        # Outgoing message queues (socket:Queue)
        message_queues = {}
        #i = 0

        while not rospy.is_shutdown():

		# Wait for at least one of the sockets to be ready for processing
		readable, writable, exceptional = select.select(inputs, outputs, inputs)
		counterROS=counterROS+1 # for checking how the loops working.
		#print "ROS Counter is: ", counterROS
		# Handle inputs
		#if readable is server
		#	print "S is server"

		for s in readable:
		        #print "S is readable:"
		        if s is server:
		            # A "readable" server socket is ready to accept a connection
		            connection, client_address = s.accept()
		            print >>sys.stderr, 'new connection from', client_address
		            connection.setblocking(0)
		            inputs.append(connection)

		            # Give the connection a queue for data we want to send
		            message_queues[connection] = Queue.Queue()

		        else:
				data = s.recv(1024)
				if data:
					# A readable client socket has data
					list_data = data.split("\n")
					innerLoopCounter=0
					listDataCounter=listDataCounter+1
					#print ">>>>>>>>>>>>>>>>>>>>>>>        List_data counter: ",listDataCounter
					#print ">>>>>>>>>>>>>>>>>>>>>>>       List Data ",list_data

					for line in list_data:
						condition, option, x,y,z = decode(line)
#in This If condition, we check the data we recieve, if the first line of the data we recieve is correct, we increase the number of pack, and copy data to list_data_publish which we use these list for data publishing.

						if(condition == True and option == 0 and innerLoopCounter==0 ):
							counterPack=counterPack+1
							innerLoopCounter=innerLoopCounter+1
							list_data_publish=list_data

#						if(condition == True and option == 0 and innerLoopCounter==110):
#
#						        try:
#						            accel = Pose()
#						            accel.position.x=  float(x)
#						            accel.position.y=  float(y)
#						            accel.position.z=  float(z)
#						            pub.publish(accel)
#						            rospy.loginfo("Pub Acc...")
#
#							except ValueError,e:
#						        	#i = i
#								pass

# if we want to publish gyro data we should add them after acc publishment, at the end of ros loop.
#
#						if(condition == True and option == 1):
#						        try:
#						            gyro = Pose()
#						            gyro.position.x=  float(x)
#						            gyro.position.y=  float(y)
#						            gyro.position.z=  float(z)
#						            pub2.publish(gyro)
#						            #i = i+1
#						            print >>sys.stderr, "sending..."
#						        except ValueError,e:
#						        	#i = i
#								pass
						message_queues[s].put(data)
						# Add output channel for response
						if s not in outputs:
						    outputs.append(s)
				else:
				        # Interpret empty result as closed connection
				        print >>sys.stderr, 'closing', client_address, 'after reading no data'
				        # Stop listening for input on the connection
				        if s in outputs:
				            outputs.remove(s)
				        inputs.remove(s)
				        s.close()

				        # Remove message queue
				        del message_queues[s]

#############################################
# Publisher of the data outside of the socket loop, inside the ros loop. because of the problems we had in managing looping and datas we recieve.


		#print "=============================>>>>>>>>>>>>>>>>>>>>Number of Pack", counterPack
		if counterPack>0:

			#print "1st Line of the Line List is: ",list_data [0]
			if counterPack>counterPackOld:
				#print list_data_publish
				length_list_data=len(list_data_publish)# length of acceptable data
				#print "List Data Length ",length_list_data
				#print "Old Pack Number: ",counterPackOld
				lineNo=0 # when recieve new acceptable data --> we start to read data from first line
				counterPackOld=counterPack # a flag for checking recieving new data.
			if lineNo<length_list_data:
				condition, option, x,y,z = decode(list_data_publish[lineNo])
				#print "publish Line Number is: ", lineNo
				if(condition == True and option == 0 ):
					try:
						outputCounter = outputCounter+1
						accel = Pose()
						accel.position.x=  float(x)
						accel.position.y=  float(y)
						accel.position.z=  float(z)
						pub.publish(accel)
						#rospy.loginfo("Pub Acc...")
						#print "Data Publish: ",list_data_publish [lineNo]
						#print "Counter:", outputCounter
						micro_sec = int(round(time.time() * 1e6))
						#print micro_sec
						file.write('{} {} {} {}'.format(str(micro_sec),str(x),str(y),str(z)))
						file.write("\n")

						#if lineNo!=(length_list_data-1):
						r.sleep()
					except ValueError,e:
						pass
				lineNo=lineNo+1

###############################################

if __name__ == '__main__':
	try:
		main()
	except rospy.ROSInterruptException:
		pass






