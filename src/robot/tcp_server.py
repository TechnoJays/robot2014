import json
import queue
import socketserver
import threading
import target
import time


class ServerWithQueue(socketserver.TCPServer):

    def __init__(self, server_address, RequestHandlerClass, data_queue):
        socketserver.TCPServer.__init__(self, server_address,
                                        RequestHandlerClass)
        self.data_queue = data_queue


class TargetHandler(socketserver.StreamRequestHandler):

    def handle(self):
        while True:
            json_dict = None
            new_target = None
            data = str(self.rfile.readline(), "utf-8")
            if not data:
                break
            try:
                json_dict = json.loads(data.strip())
            except ValueError:
                pass
            except TypeError:
                pass
            if json_dict:
                try:
                    new_target = target.Target(**json_dict)
                except TypeError:
                    pass
            if new_target:
                if self.server.data_queue.full():
                    self.server.data_queue.get()
                self.server.data_queue.put(new_target)
            time.sleep(0.1)


class ImageServer(threading.Thread):

    def __init__(self, data_queue, port=1180):
        self.port = port
        self._server = None;
        threading.Thread.__init__(self);
        self._data_queue = data_queue

    def run(self):
        if self._server == None:
            address = ('localhost', self.port);
            self._server = ServerWithQueue(address, TargetHandler,
                                           self._data_queue);
        self._server.serve_forever()

#if __name__ == '__main__':
#    data_queue = queue.Queue(2)
#    serv = ImageServer(data_queue);
#    serv.start();
    #serv.setDaemon(True)

