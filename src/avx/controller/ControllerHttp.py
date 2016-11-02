from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import logging


def handleRequest(path, controller, respond):
    if path.count('/') is 3:
        _, deviceID, method, args = path.split('/')
        if controller.hasDevice(deviceID):
            device = controller.getDevice(deviceID)
            if device.httpAccessible:
                function = getattr(device, method)
                if function:
                    result = function(*args.split(','))
                    respond(200, "OK " + str(result))
                else:
                    respond(400, "No such function: " + method)
            else:
                respond(403, "Not permitted to access device " + deviceID + " over HTTP.")
        else:
            respond(404, "No such device: " + deviceID)
    else:
        respond(400, "Incorrectly formatted URL: " + path)


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
            handleRequest(self.path, self.controller, self.respond)

        def respond(self, responseCode, text):
            self.send_response(responseCode)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(text)

    def run(self):
        self.server = HTTPServer(("", self.port), self.ControllerHttpRequestHandler)
        logging.info("Started HTTP server on port " + str(self.port))
        self.server.serve_forever()
