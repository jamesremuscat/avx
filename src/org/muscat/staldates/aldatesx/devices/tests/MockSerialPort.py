'''
Created on 3 Jan 2013

@author: james
'''

class MockSerialPort(object):
    '''
    It quacks like a serial port, but just stores what's sent to it and lets you check it later.
    Also allows you to set data to be returned by read() calls.
    '''


    def __init__(self, *params):
        self.portstr = "Test"
        self.clear()
        
    def setDataForRead(self, data):
        self.data = data
        
    def write(self, bytesToWrite):
        self.bytes.extend(bytesToWrite)
        return len(bytesToWrite)
    
    def clear(self):
        self.bytes = []
        
    def read(self, length):
        return self.data
    
    def flushInput(self):
        pass