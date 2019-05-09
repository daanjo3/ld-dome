import unittest
import os
import time

import dome.websocket.ha_websocket as websocket
import dome.config as config

# TODO add a method to let the webosocket run and start the tests afterwards

class TestWebsocket(unittest.TestCase):       

    def test_receivedconfig(self):
        self.assertTrue(os.path.isfile(config.WEBSOCKET_OUT_CONFIG))
    
    def test_receivedservices(self):
        self.assertTrue(os.path.isfile(config.WEBSOCKET_OUT_SERVICE))
    
    def test_receiveddevices(self):
        files = os.listdir(config.WEBSOCKET_OUT_DEVICE)
        self.assertGreater(len(files), 0)

if __name__ == '__main__':
    unittest.main()