from org.muscat.staldates.aldatesx.devices.SerialDevice import SerialDevice
from org.muscat.staldates.aldatesx.devices.Device import Device

class SerialRelayCard(SerialDevice):
    '''
    A serial relay card is a single serial device which may control multiple relays.
    For convenience, each relay on a card may have its own device which can be created by calling
    createDevice on the relay card.
    '''

    def __init__(self, deviceID, serialDevice):
        super(SerialRelayCard, self).__init__(deviceID, serialDevice)
        
    
    def on(self, channel):
        return self.sendCommand(SerialDevice.byteArrayToString([0xFF, channel, 0x01]))
        
    def off(self, channel):
        return self.sendCommand(SerialDevice.byteArrayToString([0xFF, channel, 0x00]))
        
    def createDevice(self, deviceID, channel):
        return RelayDevice(deviceID, self, channel)
    
    
class RelayDevice(Device):
    
    def __init__(self, deviceID, relayCard, channel):
        super(RelayDevice, self).__init__(deviceID)
        self.relayCard = relayCard
        self.channel = channel
        
    def on(self):
        return self.relayCard.on(self.channel)
    
    def off(self):
        return self.relayCard.off(self.channel)