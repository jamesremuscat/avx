import Pyro4
from org.muscat.staldates.aldatesx.Controller import *

if __name__ == '__main__':
    c = Pyro4.Proxy("PYRONAME:" + Controller.pyroName)
    print "Controller c available."
