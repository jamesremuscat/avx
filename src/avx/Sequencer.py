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
    scheduled Events - there is no need to add a SleepEvent(1) between them.

    Once started, the Sequencer runs in a daemonized thread and will keep running until your program otherwise
    terminates.

    Events can call any Python function, but in this context are probably calls to methods on a Controller, or the
    special 'wait' SleepEvent, which does as it says on the tin.

    Note that Pyro doesn't pickle functions, so if you're sequencing something client-side you'll need to use the
    ControllerEvent or DeviceEvent classes, and you'll only have access to the functions on the Controller and devices
    you'd call normally with Pyro.

    There should probably only be one Sequencer in a system, and it should probably reside on the controller side
    and not the user interface side. Breaching either of these conditions should be preceded by some Deep Thought
    about possible side effects.
    '''

    def __init__(self, controller):
        '''Initialise, but do not start(), the Sequencer.'''
        Thread.__init__(self)
        self.controller = controller
        self.queue = Queue()
        self.setDaemon(True)
        self.lock = RLock()

    def run(self):
        logging.info("Starting sequencer loop")
        while 1:
            time.sleep(1)
            event = self.queue.get()
            event.execute(self.controller)

    def sequence(self, *events):
        '''Add one or more Events to the sequencer queue. Events added in one call are guaranteed to be executed in order
        and without interleaving with other event sequences.'''
        with self.lock:
            for event in events:
                self.queue.put(event)


class Event(object):
    '''An Event is essentially a preserved method call, to be executed at an unspecified point in the future. This will NOT work over
    Pyro RPC: use a ControllerEvent with a named method argument instead.'''

    def __init__(self, method, *args):
        '''Create an Event that, when executed, will call the given method and provide the given arguments.
        Keyword arguments are not (currently) supported.'''
        self.method = method
        self.args = args

    def execute(self, controller):
        '''Execute the Event, by calling the relevant method with the given arguments.'''
        self.method(*self.args)


class ControllerEvent(Event):
    '''A ControllerEvent invokes a method on the Controller. The method is supplied by name.'''

    def __init__(self, method, *args):
        Event.__init__(self, method, *args)

    def execute(self, controller):
        getattr(controller, self.method)(*self.args)


class DeviceEvent(Event):
    '''A DeviceEvent invokes a method on a device on the Controller. The device ID and method are supplied by name.'''

    def __init__(self, deviceID, method, *args):
        Event.__init__(self, method, *args)
        self.deviceID = deviceID

    def execute(self, controller):
        getattr(controller.getDevice(self.deviceID), self.method)(*self.args)


class SleepEvent(Event):
    '''Sleep for a certain number of seconds.'''

    def __init__(self, seconds):
        Event.__init__(self, None)
        self.seconds = seconds

    def execute(self, controller):
        logging.debug("Sleeping sequencer for " + str(self.seconds) + " seconds")
        time.sleep(self.seconds)


class CompositeEvent(object):
    '''An Event that immediately triggers any of its child events.'''

    def __init__(self, *events):
        self.events = events

    def addEvent(self, event):
        self.events.append(event)

    def execute(self, controller):
        for event in self.events:
            event.execute(controller)


class LogEvent(object):
    '''An Event that writes to the controller's log.'''

    def __init__(self, level, msg):
        self.level = level
        self.msg = msg

    def execute(self, controller):
        logging.log(self.level, self.msg)


class BroadcastEvent(object):
    def __init__(self, msgType, source, data):
        self.msgType = msgType
        self.source = source
        self.data = data

    def execute(self, controller):
        controller.broadcast(self.msgType, self.source, self.data)
