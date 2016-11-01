import logging
import os
import subprocess
import Pyro4


def setHostname():
        ip = getHostname()
        logging.info("Using " + ip + " as hostname")
        Pyro4.config.HOST = ip


def getHostname():
    fromEnv = os.environ.get("PYRO_IP", False)
    if fromEnv:
        return fromEnv
    return subprocess.check_output(["hostname", "-I"]).split()[0].rstrip()
