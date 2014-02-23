"""This module is the tcp client that gets targets and sends them to a robot.

NOTE: THIS RUNS ON THE DRIVER STATION, NOT ON THE ROBOT.

DO NOT UPLOAD TO THE ROBOT!!

"""

import json_helper
import socket
import targeting
import threading
import time


class ImageProcessor(threading.Thread):
    """Thread that gets targets and sends them to a tcp server."""

    _targeting = None

    def __init__(self, port=1180):
        """Initialize the image processing thread."""
        self.port = port
        self._sock = None;
        self._targeting = targeting.Targeting()
        threading.Thread.__init__(self);

    def run(self):
        """Background thread that gets images and sends them to the server."""
        robot_connected = False
        camera_connected = False
        while True:
            if not robot_connected:
                try:
                    print "Attempting to connect to robot..."
                    if self._sock == None:
                        # Create a socket (SOCK_STREAM means a TCP socket)
                        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # Connect to server and send data
                    address = ("10.0.94.2", self.port)
                    self._sock.connect(address)
                    robot_connected = True
                except Exception:
                    print "Robot connection failed."
                    self._sock = None
                    robot_connected = False
            if not camera_connected:
                print "Attempting to connect to the camera..."
                if not self._targeting.open():
                    print "Camera connection failed."
                    camera_connected = False
                else:
                    camera_connected = True
            if not camera_connected or not robot_connected:
                print "Retrying in 5 seconds."
                time.sleep(5)
                continue
            print "Connected to both! Processing targets..."
            while True:
                try:
                    data = None
                    targets = self._targeting.get_targets()
                    for current_target in targets:
                        data = json_helper.to_json(current_target)
                        print "Sending: " + str(data)
                        if data:
                            #self._sock.send(bytes(data + '\n', "utf-8")) #python3
                            self._sock.send(bytes(data + '\n'))
                except Exception as excep:
                    print "Connection error, disconnected: " + str(excep)
                    self._sock.close()
                    self._targeting.close()
                    self._sock = None
                    break
                time.sleep(0.5)
            time.sleep(1)

if __name__ == '__main__':
    proc = ImageProcessor();
    proc.start();
    #proc.setDaemon(True)

