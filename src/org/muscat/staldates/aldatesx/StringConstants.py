'''
Created on 15 Nov 2012

@author: jrem
'''


class StringConstants():
    '''
    Storage for string constants.
    '''

    '''Text displayed when we can't contact the Pyro nameserver on the network.'''
    nameErrorText = "Can't talk to Pyro network. Please check network connectivity and restart the controller if necessary."

    '''Text displayed when we can talk to the nameserver, but can't find the controller object or something else goes wrong.'''
    protocolErrorText = "Can't talk to control server. Please check network connectivity and restart the controller if necessary."

    noDevice = "No controllable device"

    poweringOn = "System powering on. Please wait..."
    poweringOff = "System powering off. Please wait..."
