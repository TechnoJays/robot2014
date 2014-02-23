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

    def __init__(self, port=1180):
        """Initialize the image processing thread."""
        self.port = port
        self._sock = None;
        threading.Thread.__init__(self);

    def run(self):
        """Background thread that gets images and sends them to the server."""
        while True:
            try:
                if self._sock == None:
                    # Create a socket (SOCK_STREAM means a TCP socket)
                    self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Connect to server and send data
                address = ("localhost", self.port)
                self._sock.connect(address)
            except Exception:
                self._sock = None
                time.sleep(5)
                continue
            while True:
                try:
                    data = None
                    targets = targeting.get_targets()
                    for current_target in targets:
                        data = json_helper.to_json(current_target)
                        if data:
                            self._sock.send(bytes(data + '\n', "utf-8"))
                except Exception:
                    self._sock.close()
                    self._sock = None
                    break
                time.sleep(0.5)
            time.sleep(1)

if __name__ == '__main__':
    proc = ImageProcessor();
    proc.start();
    #proc.setDaemon(True)

