'''
Created on 18 Mar 2013

@author: jrem
'''
from avx.devices.serial.tests.MockSerialPort import MockSerialPort
from avx.devices.serial.VISCACamera import VISCACamera, Aperture
from threading import Thread
from time import sleep

import unittest


class TestVISCACamera(unittest.TestCase):

    def testGetPosition(self):
        port = MockSerialPort()

        cam = VISCACamera("Test Camera", port, 1)

        result = []

        def getPos(result):
            result.append(cam.getPosition())

        t = Thread(target=getPos, args=[result])
        t.start()

        cam.handleMessage([0x10, 0x50, 0x01, 0x02, 0x03, 0x04, 0x0A, 0x0B, 0x0C, 0x0D, 0xFF])
        sleep(0.5)
        cam.handleMessage([0x10, 0x50, 0x05, 0x06, 0x07, 0x08, 0xFF])

        t.join()

        self.assertTrue(len(result) == 1)
        pos = result[0]

        self.assertEqual(pos.pan, 0x1234)
        self.assertEqual(pos.tilt, 0xABCD)
        self.assertEqual(pos.zoom, 0x5678)

    def testSetAperture(self):
        port = MockSerialPort()

        cam = VISCACamera("Test Camera", port, 1)

        def run(func, arg, myBytes):
            Thread(target=func, args=[arg]).start()
            sleep(0.2)
            cam.handleMessage([0, 0x40, 0xFF])
            self.assertBytesEqual(myBytes, port.bytes)
            port.clear()

        run(cam.setAperture, Aperture.F28, [0x81, 0x01, 0x04, 0x4B, 0x00, 0x00, 0x00, 0x01, 0xFF])

        run(cam.setAperture, Aperture.F1_8, [0x81, 0x01, 0x04, 0x4B, 0x00, 0x00, 0x01, 0x01, 0xFF])

    def testMovement(self):
        port = MockSerialPort()
        cam = VISCACamera("Test Camera", port, 1)

        def run(func, myBytes):
            Thread(target=func).start()
            sleep(0.2)
            cam.handleMessage([0, 0x40, 0xFF])
            self.assertBytesEqual(myBytes, port.bytes)
            port.clear()

        run(cam.moveDown, [0x81, 0x01, 0x06, 0x01, 0x06, 0x06, 0x03, 0x02, 0xFF])
        run(cam.moveDownLeft, [0x81, 0x01, 0x06, 0x01, 0x06, 0x06, 0x01, 0x02, 0xFF])
        run(cam.moveLeft, [0x81, 0x01, 0x06, 0x01, 0x06, 0x06, 0x01, 0x03, 0xFF])
        run(cam.moveUpLeft, [0x81, 0x01, 0x06, 0x01, 0x06, 0x06, 0x01, 0x01, 0xFF])
        run(cam.moveUp, [0x81, 0x01, 0x06, 0x01, 0x06, 0x06, 0x03, 0x01, 0xFF])
        run(cam.moveUpRight, [0x81, 0x01, 0x06, 0x01, 0x06, 0x06, 0x02, 0x01, 0xFF])
        run(cam.moveRight, [0x81, 0x01, 0x06, 0x01, 0x06, 0x06, 0x02, 0x03, 0xFF])
        run(cam.moveDownRight, [0x81, 0x01, 0x06, 0x01, 0x06, 0x06, 0x02, 0x02, 0xFF])
        run(cam.stop, [0x81, 0x01, 0x06, 0x01, 0x06, 0x06, 0x03, 0x03, 0xFF])

    def testZoomFocus(self):
        port = MockSerialPort()
        cam = VISCACamera("Test Camera", port, 1)

        def run(func, myBytes):
            Thread(target=func).start()
            sleep(0.2)
            cam.handleMessage([0, 0x40, 0xFF])
            sleep(0.2)
            cam.handleMessage([0, 0x40, 0xFF])
            self.assertBytesEqual(myBytes, port.bytes)
            port.clear()

        focusManual = [0x81, 0x01, 0x04, 0x38, 0x03, 0xFF]

        run(cam.focusFar, focusManual + [0x81, 0x01, 0x04, 0x08, 0x02, 0xFF])
        run(cam.focusNear, focusManual + [0x81, 0x01, 0x04, 0x08, 0x03, 0xFF])
        run(cam.focusStop, [0x81, 0x01, 0x04, 0x08, 0x00, 0xFF])
        run(cam.focusAuto, [0x81, 0x01, 0x04, 0x38, 0x02, 0xFF])
        run(cam.focusManual, focusManual)
        run(cam.zoomIn, [0x81, 0x01, 0x04, 0x07, 0x26, 0xFF])
        run(cam.zoomOut, [0x81, 0x01, 0x04, 0x07, 0x36, 0xFF])
        run(cam.zoomStop, [0x81, 0x01, 0x04, 0x07, 0x00, 0xFF])

    def assertBytesEqual(self, expected, actual):
        self.assertEqual(len(expected), len(actual))
        for i in range(len(expected)):
            self.assertEqual(chr(expected[i]), actual[i], "Byte " + str(i) + ", expected " + str(expected[i]) + " but received " + str(ord(actual[i])))


if __name__ == "__main__":
    unittest.main()
