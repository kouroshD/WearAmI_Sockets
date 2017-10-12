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
from numpy import double

def signal_handler(signal, frame):
	"""Signal handler of the data """
	print('Signal Handler, you pressed Ctrl+C!')
	print('Server will be closed')
	sys.exit(0)

        
def main():
	rospy.init_node('wearami_socket_offline', anonymous=True)
	r = rospy.Rate(40) # period
	signal.signal(signal.SIGINT, signal_handler)
	
	filePath = os.path.join('/home/nasa/Datalog/ICRA_TESTS/',"20_Acc_data"+".txt")
	inputFile = open(filePath, "r")
	pub = rospy.Publisher('wearami_acc', Pose, queue_size=10)

	counterROS=0
	completeName = os.path.join('/home/nasa/Datalog/AIIA/14/',"20_AccData"+".txt")
	file = open(completeName, "a")

# 	while not rospy.is_shutdown() and
	secondsInit = rospy.get_time()
	for line in inputFile:
		counterROS=counterROS+1 
		cleanLine = line.rstrip(' \n')
		Acc_list = [float(x) for x in cleanLine.split(' ')][0:4]
		assert len(Acc_list)> 0
#   		print counterROS,': ',Acc_list[0],' ', Acc_list[1],' ', Acc_list[2],' ', Acc_list[2]
		accel = Pose()
		accel.position.x=Acc_list[1]
		accel.position.y=Acc_list[2]
		accel.position.z=Acc_list[3]
		pub.publish(accel)
		
		micro_sec = int(round(time.time() * 1e6))
		#print micro_sec
		file.write('{} {} {} {}'.format(str(micro_sec),float(Acc_list[1]),float(Acc_list[1]),float(Acc_list[1])))
		file.write("\n")
		if counterROS>1:
			time_now=Acc_list[0]
			elapsed_time=(time_now-time_prev)/1000000
			rospy.sleep(elapsed_time)
		time_prev=Acc_list[0]
	secondsEnd = rospy.get_time()
	total_time=secondsEnd-secondsInit
	print 'total_time: ',total_time
###############################################

if __name__ == '__main__':
	try:
		main()
	except rospy.ROSInterruptException:
		pass






