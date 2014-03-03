"""This module provides a image targeting server."""

import json
import queue
import socketserver
import threading
import target
import time


class ServerWithQueue(socketserver.TCPServer):
    """Describes a TCP server with a Queue for transfering data."""

    def __init__(self, server_address, RequestHandlerClass, data_queue):
        """Create a TCP server with a Queue.

        Args:
            server_address: the host and port for the server.
            RequestHandlerClass: the request handler.
            data_queue: the Queue for transfering data to another object.

        """
        # Create the base TCP server with address/port and connection handler
        socketserver.TCPServer.__init__(self, server_address,
                                        RequestHandlerClass)
        # Store the Queue used to transfer objects to another thread/object
        self.data_queue = data_queue


class TargetHandler(socketserver.StreamRequestHandler):
    """Describes a connection handler for Target objects."""

    def handle(self):
        """Handle incoming connections.

        This method receives JSON data a line at a time.  The JSON is parsed
        and a Target object is instantated using the resulting JSON dictionary.
        The Target object is then put into a Queue used to transfer data between
        different objects and threads.  If the queue is full, the oldest (since
        it's FIFO) is removed and the new Target is added.

        """
        print("Connection!")
        # Loop continuously as long as the connection is alive
        while True:
            # Read from the TCP connection until a newline is encountered
            # We append a newline in the TCP client whenever a JSON message
            # is sent.
            json_data = None
            new_targets = []
            try:
                data = str(self.rfile.readline(), "utf-8")
            except Exception:
                break
            # If we failed to read data, close the connection
            if not data:
                break
            # Try to convert the JSON string to Python types (List of Dicts)
            try:
                json_data = json.loads(data.strip())
            except ValueError:
                pass
            except TypeError:
                pass
            # If the JSON was parsed, create Target objects from it
            if json_data and isinstance(json_data, list):
                for json_dict in json_data:
                    # Here we use ** to pass a dictionary containing all keyword
                    # arguments. It isn't the best, but I don't know of a better
                    # method for easily populating an object's properties using a
                    # dictionary.
                    try:
                        current_target = target.Target(**json_dict)
                        new_targets.append(current_target)
                    except TypeError:
                        pass
            # If everything went well, we have new Target object(s)
            if new_targets and len(new_targets) > 0:
                # Add Targets to the queue. If the queue is full, remove the
                # oldest element (since it's FIFO, just do a get()).
                if self.server.data_queue.full():
                    try:
                        self.server.data_queue.get()
                    except queue.Empty:
                        pass
                try:
                    self.server.data_queue.put(new_targets)
                except queue.Full:
                    pass
            time.sleep(0.1)


class ImageServer(threading.Thread):
    """A TCP server that runs in a background thread to receive Targets."""

    def __init__(self, data_queue, port=1180):
        """Initialize a background thread for receiving Targets over TCP."""
        self.port = port
        self._server = None
        self._data_queue = data_queue
        threading.Thread.__init__(self)

    def run(self):
        """Starts a TCP server that listens for Targets."""
        # If the server hasn't been created yet, create it
        if self._server == None:
            address = ('10.0.94.2', self.port)
            self._server = ServerWithQueue(address, TargetHandler,
                                           self._data_queue)
        print("Listening for TCP connections..")
        # Serve connections forever (until the robot is turned off)
        self._server.serve_forever()

# This is used for testing on a PC
#if __name__ == '__main__':
#    data_queue = queue.Queue(1)
#    serv = ImageServer(data_queue)
#    serv.start()

