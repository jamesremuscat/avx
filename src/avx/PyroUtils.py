import subprocess
import logging
import Pyro4


def setHostname():
        ip = subprocess.check_output(["hostname", "-I"]).split()[0].rstrip()
        logging.info("Using " + ip + " as hostname")
        Pyro4.config.HOST = ip
