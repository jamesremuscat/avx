ALIX - St Aldates In-House AMX Replacement
==========================================

Configuration and Miscellaneous Notes
-------------------------------------

### INSTALLATION & CONFIGURATION ###

You will need a Python (2.7 is what I've used) with python-serial, PySide, and
Pyro4 . Ubuntu packages all but Pyro4: you'll need to `easy_install` it to get
the right version.

You'll also need the Tango icon theme installed - it needs to be under
`/usr/share/icons/Tango`. This is where the tango-icon-theme package gets
installed to.

Mapping of physical hardware devices through serial ports to virtual devices is
done in the `runController.py` script. Be sure to map devices based on their USB
device path - `/dev/ttyUSBx`'es might get swapped round after a reboot, which
would be sad. Everything GUI-side refers to the name string you assign to each
device, so balance these between descriptive and concise.


### RUNNING ###

You will need a Pyro4 nameserver running somewhere on your network. The 
`runNameserver.sh` script will take care of this for you, or use the
`contrib/pyro-nsd` init script for Debian (maybe others?)

The machine with all the serial ports on it will need to run the 
`runController.py` script. The machine with the GUI should run the `AldatesX.py`
script. They don't have to be different machines. The GUI should automatically
discover the controller via the Pyro nameserver, no need to manually configure
IP addresses and whatnot.

The controller machine can also use the `contrib/AldatesXController` init script
to run the controller as a daemon.
