#!/usr/bin/env python

import sys
import rospy
from beginner_tutorials.srv import robot_command
import random
import time 

__author__ = 'kongaloosh'

def robot_command_client(x, y):
    rospy.wait_for_service('robot_controller')
    try:
        command_service = rospy.ServiceProxy('robot_controller', robot_command)
        resp1 = command_service(x, y)
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e

if __name__ == "__main__":
    x = 512
    y = 512

    while True:
        command = random.randint(0,3)
	print command
        if command == 0:
            x += 70
        elif command == 1:
            x -= 70
        elif command == 2:
            y += 70
        elif command == 3:
            y -= 70

        robot_command_client(x, y)
	time.sleep(0.2)
    sys.exit(1)
