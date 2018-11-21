#!/usr/bin/env python
from __future__ import print_function # TODO is this needed

import sys
import rospy
import object_detection_lib
from object_detection.msg import detection_results
from std_msgs.msg import Empty
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class ObjectDetectionNode:
    def __init__(self):
        self.__bridge = CvBridge()
        # Publisher to publish update image
        self.__image_pub = rospy.Publisher("object_detection_node/adjusted_image", Image, queue_size=1)
        # Publisher to publish the result
        self.__result_pub = rospy.Publisher("object_detection_node/result", detection_results, queue_size=1)
        # Subscribe to topic which will kick off object detection in the next image
        self.__command_sub = rospy.Subscriber("object_detection_node/start", Empty, self.StartCallback)
        # Subscribe to the topic which will supply the image fom the camera
        self.__image_sub = rospy.Subscriber("camera/image/raw",Image, self.Imagecallback)

        # Flag to indicate that we have been requested to use the next image
        self.__scan_next = False

        # Read the path for models/research/object_detection directory from the parameter server or use this default
        object_detecton_path = rospy.get_param('/object_detection/path', '/home/ubuntu/models/research/object_detection')

        # Read the confidence level, any object with a level below this will not be used
        confidence_level = rospy.get_param('/object_detection/confidence_level', 0.50)

        # Create the object_detection_lib class instance
        self.__odc = object_detection_lib.ObjectDetection(object_detection_path, confidence_level)


    # Callback for start command message
    def StartCallback(self, data):
        # Indicate to use the next image for the scan
        self.__scan_next = True

    # Callback for new image received
    def Imagecallback(self, data):
        if self.__scan_next == True:
            self.__scan_next = False
            # Convert the ROS image to an OpenCV image
            image = self.__bridge.imgmsg_to_cv2(data, "bgr8")

            # The supplied image will be modified if known objects are detected
            object_names_detected = self.__odc.scan_for_objects(image)

            # publish the image, it may have been modified
            try:
                self.__image_pub.publish(self.__bridge.cv2_to_imgmsg(image, "bgr8"))
            except CvBridgeError as e:
                print(e)

            # Publish names of objects detected
            result = detection_results()
            result.names_detected = object_names_detected
            self.__result+pub.publish(result)

def main(args):
    rospy.init_node('object_detection_node', anonymous=False)
    odn = ObjectDetectionNode()
    rospy.loginfo("Object detection node started")
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main(sys.argv)
