"""This module is the tcp client that gets targets and sends them to a robot.

NOTE: THIS RUNS ON THE DRIVER STATION, NOT ON THE ROBOT.

DO NOT UPLOAD TO THE ROBOT!!

"""

import json_helper
import socket
import targeting
import time


class ImageProcessor(object):
    """Gets targets and sends them to a tcp server."""

    _targeting = None

    def __init__(self, port=1180):
        """Initialize the image processor."""
        self.port = port
        self._sock = None
        self._targeting = targeting.Targeting()

    def process(self):
        """Gets images and sends them to the server."""
        robot_connected = False
        camera_connected = False
        # Loop continuously
        while True:
            # Try to connect to the robot
            if not robot_connected:
                try:
                    print "Attempting to connect to robot..."
                    if self._sock == None:
                        # Create a socket (SOCK_STREAM means a TCP socket)
                        self._sock = socket.socket(socket.AF_INET,
                                                   socket.SOCK_STREAM)
                    # Connect to server and send data
                    address = ("10.0.94.2", self.port)
                    self._sock.connect(address)
                    robot_connected = True
                except KeyboardInterrupt:
                    raise
                except Exception as excep:
                    print "Robot connection failed." + str(excep)
                    self._sock = None
                    robot_connected = False
            # Try to connect to the camera
            if not camera_connected:
                print "Attempting to connect to the camera..."
                if not self._targeting.open():
                    print "Camera connection failed."
                    camera_connected = False
                else:
                    camera_connected = True
            # If one of the two isn't connected, we can't continue yet
            if not camera_connected or not robot_connected:
                print "Retrying in 5 seconds."
                time.sleep(5)
                continue
            # Both connections are active; time to get to work
            print "Connected to both! Processing targets..."
            # Loop as long as we're connected
            while True:
                try:
                    data = None
                    # Get an image from the webcam and process it into a List of
                    # Targets
                    targets = self._targeting.get_targets()
                    # Convert each Target to JSON and send it to the robot
                    for current_target in targets:
                        data = json_helper.to_json(current_target)
                        print "Sending: " + str(data)
                        if data:
                            # Python3
                            #self._sock.send(bytes(data + '\n', "utf-8"))
                            # Python2
                            self._sock.send(bytes(data + '\n'))
                # If anything fails, bail out and try to reconnect
                except KeyboardInterrupt:
                    raise
                except Exception as excep:
                    print "Connection error, disconnected: " + str(excep)
                    self._sock.close()
                    #self._targeting.close()
                    self._sock = None
                    break
                # Wait before getting new targets
                # TODO: what should this really be?
                time.sleep(0.2)
            # Wait before trying to reconnect
            time.sleep(1)

# This lets us run this as a script
if __name__ == '__main__':
    # Create the Image Processor and start it
    iproc = ImageProcessor()
    iproc.process()

