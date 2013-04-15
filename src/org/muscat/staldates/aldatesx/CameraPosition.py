class CameraPosition(object):
    tilt = 0
    pan = 0
    zoom = 0

    def __init__(self, pan, tilt, zoom):
        object.__init__(self)
        self.tilt = tilt
        self.pan = pan
        self.zoom = zoom
