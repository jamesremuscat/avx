import subprocess
import logging
import Pyro4


def setHostname():
        ip = subprocess.check_output(["hostname", "-I"]).rstrip()
        logging.info("Using " + ip + " as hostname")
        Pyro4.config.HOST = ip
