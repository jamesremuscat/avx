from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import logging


class ControllerHttp(Thread):
    '''
    An HTTP interface to a Controller's methods.
    '''

    def __init__(self, controller, port=8080):
        super(ControllerHttp, self).__init__()
        self.controller = controller
        self.port = port
        self.setDaemon(True)
        self.ControllerHttpRequestHandler.controller = controller

    class ControllerHttpRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parts = self.path.split('/')
            if hasattr(self.controller, parts[1]):
                attr = getattr(self.controller, parts[1])
                args = parts[2].split(',')
                if (self.controller.hasDevice(args[0])):
                    result = attr(*args)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write("OK " + str(result))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write("No such device: " + args[0])
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write("No such method: " + parts[1])

    def run(self):
        self.server = HTTPServer(("", self.port), self.ControllerHttpRequestHandler)
        logging.info("Started HTTP server on port " + str(self.port))
        self.server.serve_forever()
