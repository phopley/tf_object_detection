#!/usr/bin/env python

import sys
import rospy
import object_detection_lib
import actionlib
from tf_object_detection.msg import scan_for_objectsAction, scan_for_objectsGoal, scan_for_objectsResult
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge, CvBridgeError

class ObjectDetectionNode:
    def __init__(self):
        self.__bridge = CvBridge()
        # Publisher to publish update image
        self.__image_pub = rospy.Publisher('tf_object_detection_node/image/compressed', CompressedImage, queue_size=1)
        # Subscribe to the topic which will supply the image fom the camera
        self.__image_sub = rospy.Subscriber('raspicam_node/image/compressed', CompressedImage, self.Imagecallback)

        # Read the path for models/research/object_detection directory from the parameter server or use this default
        object_detection_path = rospy.get_param('/object_detection/path', '/home/ubuntu/git/models/research/object_detection')

        # Read the confidence level, any object with a level below this will not be used
        confidence_level = rospy.get_param('/object_detection/confidence_level', 0.50)

        # Create the object_detection_lib class instance
        self.__odc = object_detection_lib.ObjectDetection(object_detection_path, confidence_level)

        # Create the Action server
        self.__as = actionlib.SimpleActionServer('object_detection', scan_for_objectsAction, self.do_action, False)
        self.__as.start()

    # Callback for new image received
    def Imagecallback(self, data):
        # Each time we receive an image we store it in case we are asked to scan it
        self.__current_image = data

    def do_action(self, goal):
        # Scan the current image for objects
        # Convert the ROS compressed image to an OpenCV image
        image = self.__bridge.compressed_imgmsg_to_cv2(self.__current_image)

        # The supplied image will be modified if known objects are detected
        object_names_detected = self.__odc.scan_for_objects(image)

        # publish the image, it may have been modified
        try:
            self.__image_pub.publish(self.__bridge.cv2_to_compressed_imgmsg(image))
        except CvBridgeError as e:
            print(e)

        # Set result for the action
        result = scan_for_objectsResult()
        result.names_detected = object_names_detected
        self.__as.set_succeeded(result) 


def main(args):
    rospy.init_node('tf_object_detection_node', anonymous=False)
    odn = ObjectDetectionNode()
    rospy.loginfo("Object detection node started")
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main(sys.argv)
