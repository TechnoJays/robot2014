import json_helper
import socket
import targeting
import threading
import time


class ImageProcessor(threading.Thread):

    def __init__(self, port=1180):
        self.port = port
        self._sock = None;
        threading.Thread.__init__(self);

    def run(self):
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
                    #current_target = targeting.get_target()
                    args = {'distance': 5.0, 'angle':-10, 'is_hot':True, 'confidence':100}
                    current_target = targeting.Target(**args)
                    if current_target:
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

