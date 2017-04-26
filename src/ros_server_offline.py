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
	
	filePath = os.path.join('/home/nasa/Datalog/ICRA_TESTS',"01_Acc_data"+".txt")
	inputFile = open(filePath, "r")
	pub = rospy.Publisher('wearami_acc', Pose, queue_size=10)

	counterROS=0

# 	while not rospy.is_shutdown() and
	for line in inputFile:
		counterROS=counterROS+1 
		cleanLine = line.rstrip(' \n')
		Acc_list = [float(x) for x in cleanLine.split(' ')][0:4]
		assert len(Acc_list)> 0
# 		print counterROS,': ',Acc_list[1],' ', Acc_list[2],' ', Acc_list[3]
		accel = Pose()
		accel.position.x=Acc_list[1]
		accel.position.y=Acc_list[2]
		accel.position.z=Acc_list[3]
		pub.publish(accel)
		r.sleep()
		

###############################################

if __name__ == '__main__':
	try:
		main()
	except rospy.ROSInterruptException:
		pass






