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
            parts = self.path.split('/')
            if hasattr(self.controller, parts[1]):
                function = getattr(self.controller, parts[1])
                if (function.func_dict.get(httpAccessibleKey)):
                    args = parts[2].split(',')
                    if (self.controller.hasDevice(args[0])):
                        result = function(*args)
                        self.respond(200, "OK " + str(result))
                    else:
                        self.respond(404, "No such device: " + args[0])
                else:
                    self.respond(403, "Not permitted to call " + parts[1] + " over HTTP (missing @httpAccessible decorator?)")
            else:
                self.respond(400, "No such function: " + parts[1])

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
