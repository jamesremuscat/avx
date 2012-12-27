from threading import Thread
from Queue import Queue
import time

class Sequencer(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.queue = Queue()
        self.setDaemon(True)
        
    def run(self):
        print "Starting sequencer loop"
        while 1:
            time.sleep(1)
            event = self.queue.get(1)
            event.execute()
            
    def sequence(self, *events):
        for event in events:
            self.queue.put(event)
            
    @staticmethod
    def wait(secs):
        '''
        Convenience method for scheduling a wait. Returns an Event you can use.
        '''
        def annotatedSleep(secs):
            print "Sleeping sequencer for " + str(secs) + " seconds"
            time.sleep(secs)
        return Event(annotatedSleep, secs)
            

class Event(object):
    
    def __init__(self, method, *args):
        self.method = method
        self.args = args
        
    def execute(self):
        self.method(*self.args)