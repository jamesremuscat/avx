import subprocess
import logging
import Pyro4


def setHostname():
        ip = getHostname()
        logging.info("Using " + ip + " as hostname")
        Pyro4.config.HOST = ip

def getHostname():
    return subprocess.check_output(["hostname", "-I"]).split()[0].rstrip()
