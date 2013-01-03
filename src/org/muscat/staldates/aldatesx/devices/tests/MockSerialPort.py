'''
Created on 3 Jan 2013

@author: james
'''

class MockSerialPort(object):
    '''
    It quacks like a serial port, but just stores what's sent to it and lets you check it later.
    (Actually, it just has a write() method, but that's all we use.)
    '''


    def __init__(self, *params):
        self.portstr = "Test"
        self.clear()
        
    def write(self, bytesToWrite):
        self.bytes.extend(bytesToWrite)
        return len(bytesToWrite)
    
    def clear(self):
        self.bytes = []