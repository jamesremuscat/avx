'''
Created on 21 Mar 2013

@author: jrem
'''


class VISCACommand(object):
    '''
    Encapsulates a VISCA command.
    '''

    def getBytes(self, cameraID=1):
        return [0x80 + cameraID] + self.getInnerBytes() + [0xFF]


# CAM_Zoom
class ZoomStop(VISCACommand):

    def getInnerBytes(self):
        return [0x01, 0x04, 0x07, 0x00]


class ZoomIn(VISCACommand):

    def __init__(self, speed=2):
        if 1 < speed < 8:
            self.speed = speed
        else:
            self.speed = 2

    def getInnerBytes(self):
        return [0x01, 0x04, 0x07, 0x20 + self.speed]


class ZoomOut(VISCACommand):

    def __init__(self, speed=2):
        if 1 < speed < 8:
            self.speed = speed
        else:
            self.speed = 2

    def getInnerBytes(self):
        return [0x01, 0x04, 0x07, 0x30 + self.speed]


class ZoomDirect(VISCACommand):

    def __init__(self, zoom):
        if 0 <= zoom < 0x3FF:
            self.zoom = zoom
        else:
            self.zoom = 0

    def getInnerBytes(self):
        return [
            0x01,
            0x04,
            0x47,
            (self.zoom & 0xF000) >> 12,
            (self.zoom & 0x0F00) >> 8,
            (self.zoom & 0x00F0) >> 4,
            (self.zoom & 0x000F),
            ]


# CAM_Focus
class FocusStop(VISCACommand):

    def getInnerBytes(self):
        return [0x01, 0x04, 0x08, 0x00]


class FocusFar(VISCACommand):

    def getInnerBytes(self):
        return [0x01, 0x04, 0x08, 0x02]


class FocusNear(VISCACommand):

    def getInnerBytes(self):
        return [0x01, 0x04, 0x08, 0x03]


class FocusAuto(VISCACommand):

    def getInnerBytes(self):
        return [0x01, 0x04, 0x38, 0x02]


class FocusManual(VISCACommand):

    def getInnerBytes(self):
        return [0x01, 0x04, 0x38, 0x03]


# CAM_Memory
class MemorySet(VISCACommand):

    def __init__(self, preset):
        self.preset = preset

    def getInnerBytes(self):
        return [0x01, 0x04, 0x3F, 0x01, self.preset]


class MemoryRecall(VISCACommand):

    def __init__(self, preset):
        self.preset = preset

    def getInnerBytes(self):
        return [0x01, 0x04, 0x3F, 0x02, self.preset]


# Pan-tiltDrive
class MoveUp(VISCACommand):

    def __init__(self, speed):
        self.speed = speed

    def getInnerBytes(self):
        return [0x01, 0x06, 0x01, self.speed, self.speed, 0x03, 0x01]


class MoveDown(VISCACommand):

    def __init__(self, speed):
        self.speed = speed

    def getInnerBytes(self):
        return [0x01, 0x06, 0x01, self.speed, self.speed, 0x03, 0x02]


class MoveLeft(VISCACommand):

    def __init__(self, speed):
        self.speed = speed

    def getInnerBytes(self):
        return [0x01, 0x06, 0x01, self.speed, self.speed, 0x03, 0x03]


class MoveRight(VISCACommand):

    def __init__(self, speed):
        self.speed = speed

    def getInnerBytes(self):
        return [0x01, 0x06, 0x01, self.speed, self.speed, 0x02, 0x03]


class MoveStop(VISCACommand):

    def getInnerBytes(self):
        return [0x01, 0x06, 0x01, 0, 0, 0x03, 0x03]


class MoveTo(VISCACommand):

    def __init__(self, speed, position):
        self.speed = speed
        self.position = position

    def getInnerBytes(self):
        p = self.position.pan
        t = self.position.tilt
        return [0x01,
                0x06,
                0x02,
                self.speed,
                self.speed,
                # Pan x 4 bytes
                (p & 0xF000) >> 12,
                (p & 0x0F00) >> 8,
                (p & 0x00F0) >> 4,
                (p & 0x000F),
                # Tilt x 4 bytes
                (t & 0xF000) >> 12,
                (t & 0x0F00) >> 8,
                (t & 0x00F0) >> 4,
                (t & 0x000F),
                ]
