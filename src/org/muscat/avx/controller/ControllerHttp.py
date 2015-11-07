from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import logging


httpAccessibleKey = "isHTTPAccessible"


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
            if self.path.count('/') is 3:
                _, deviceID, method, args = self.path.split('/')
                if self.controller.hasDevice(deviceID):
                    device = self.controller.getDevice(deviceID)
                    if device.httpAccessible:
                        function = getattr(device, method)
                        if function:
                            result = function(*args.split(','))
                            self.respond(200, "OK " + str(result))
                        else:
                            self.respond(400, "No such function: " + method)
                    else:
                        self.respond(403, "Not permitted to access device " + deviceID + " over HTTP.")
                else:
                    self.respond(404, "No such device: " + deviceID)
            else:
                self.respond(400, "Incorrectly formatted URL: " + self.path)

        def respond(self, responseCode, text):
            self.send_response(responseCode)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(text)

    def run(self):
        self.server = HTTPServer(("", self.port), self.ControllerHttpRequestHandler)
        logging.info("Started HTTP server on port " + str(self.port))
        self.server.serve_forever()


def httpAccessible(originalFunction):
    '''
    Decorator function that marks the given function as accessible over HTTP.

    The ControllerHTTPRequestHandler will refuse to call any function on the
    controller that does NOT have this decorator.
    '''
    originalFunction.func_dict[httpAccessibleKey] = True
    return originalFunction
