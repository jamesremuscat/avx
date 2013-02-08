'''
Contains all you need to queue up a sequence of actions to be carried out in the future.
'''
from threading import Thread, RLock
from Queue import Queue
import time
import logging

class Sequencer(Thread):
    '''
    A threaded sequencer that queues Events and executes them periodically. You should call start() once you've 
    created your Sequencer: this isn't done for you. The queue is checked, and events executed, at an interval
    of around one second. This means that there will be a delay of around one second between two consecutive
    scheduled Events - there is no need to add a wait(1) between them.
    
    Once started, the Sequencer runs in a daemonized thread and will keep running until your program otherwise
    terminates.
    
    Events can be any Python function, but in this context are probably calls to methods on a Controller, or the
    special 'wait' event returned by a call to Sequencer.wait(secs), which does as it says on the tin.
    
    There should probably only be one Sequencer in a system, and it should probably reside on the controller side
    and not the user interface side. Breaching either of these conditions should be preceded by some Deep Thought
    about possible side effects.
    '''

    def __init__(self):
        '''Initialise, but do not start(), the Sequencer.'''
        Thread.__init__(self)
        self.queue = Queue()
        self.setDaemon(True)
        self.lock = RLock()
        
    def run(self):
        logging.info("Starting sequencer loop")
        while 1:
            time.sleep(1)
            event = self.queue.get()
            event.execute()
            
    def sequence(self, *events):
        '''Add one or more Events to the sequencer queue. Events added in one call are guaranteed to be executed in order
        and without interleaving with other event sequences.'''
        with self.lock:
            for event in events:
                self.queue.put(event)
            
    @staticmethod
    def wait(secs):
        '''
        Convenience method for scheduling a wait of a given number of seconds. Returns an Event you can then sequence.
        '''
        def annotatedSleep(secs):
            logging.info("Sleeping sequencer for " + str(secs) + " seconds")
            time.sleep(secs)
        return Event(annotatedSleep, secs)
            

class Event(object):
    '''An Event is essentially a preserved method call, to be executed at an unspecified point in the future.'''
    
    def __init__(self, method, *args):
        '''Create an Event that, when executed, will call the given method and provide the given arguments.
        Keyword arguments are not (currently) supported.'''
        self.method = method
        self.args = args
        
    def execute(self):
        '''Execute the Event, by calling the relevant method with the given arguments.'''
        self.method(*self.args)

        
class CompositeEvent(object):
    '''An Event that immediately triggers any of its child events.'''
    
    def __init__(self, *events):
        self.events = events
        
    def addEvent(self, event):
        self.events.append(event)
        
    def execute(self):
        for event in self.events:
            event.execute()