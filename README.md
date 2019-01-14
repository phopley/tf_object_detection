# tf_object_detection
ROS node for object detection using TensorFlow
## Running the Node
Once you have the node built you can run it with "rosrun tf_object_detection tf_object_detection_node.py".
## Node Information
Topics:

* `raspicam_node/image/compressed`:  
  Subscribes `sensor_msgs/CompressedImage` Image which may be used to run object detection on

* `tf_object_detection_node/image/compressed`:  
  Publishes `sensor_msgs/CompressedImage` Adjusted image which may contain bounded boxes and labels of detected objects
  
* `tf_object_detection_node/result`:  
  Publishes `tf_object_detection/detection_results` Contains an array of strings of the detected object names  
  
Action:

* `tf_object_detection/scan_for_objects`:  
  Server used to control the process of scanning for objects in the current image.  
  
Parameters:

* `/object_detection/path`: the path for models/research/object_detection directory. Default value = /home/ubuntu/git/models/research/object_detection
* `/object_detection/confidence_level`: confidence level, any object with a level below this will not be used. Default value = 0.5 (50%)
