import unittest
from mock import MagicMock, patch
from avx import PyroUtils


class TestPyroUtils(unittest.TestCase):

    @patch("avx.PyroUtils.subprocess")
    @patch("avx.PyroUtils.os")
    @patch("avx.PyroUtils.Pyro4")
    def testSetHostnameFromShell(self, Pyro4, os, subprocess):
        os.environ.get = MagicMock(return_value=False)
        subprocess.check_output = MagicMock(return_value='myfakehostname')
        PyroUtils.setHostname()
        subprocess.check_output.assert_called_once_with(['hostname', '-I'])
        self.assertEqual("myfakehostname", Pyro4.config.HOST)

    @patch("avx.PyroUtils.os")
    @patch("avx.PyroUtils.Pyro4")
    def testSetHostnameFromEnvironment(self, Pyro4, os):
        os.environ.get = MagicMock(return_value='myfakehostname')
        PyroUtils.setHostname()
        os.environ.get.assert_called_once_with('PYRO_IP', False)
        self.assertEqual("myfakehostname", Pyro4.config.HOST)
