import asyncio
import time
# Add redland to the python path
import sys, os
sys.path.append(os.path.abspath(os.path.join('lib', 'redland', 'bindings', 'python')))
import RDF

from dome.db.graph import Graph

from dome.websocket.HALoader import load
from dome.websocket.HAUpdater import HAUpdater
from dome.websocket.WebUpdater import WebUpdater
from dome.parser.ParserService import *
from dome.automations.AutomationService import AutomationService

from dome.lib.benchmark import BenchMark

from dome.dummy.webpropertyDummy import loadWebProperty
# from dome.dummy.automationDummy import loadAutomation
# from dome.dummy.wpautomationDummy import loadWPAutomation

class DomeMain():
    def __init__(self):
        self.manager = Manager()
        # Create global events
        self.graph_readable_event = self.manager.Event()
        self.graph_readable_event.set()
        self.loader_finished = self.manager.Event()

        # Create global queues
        self.parser_queue = self.manager.Queue()
        self.automation_queue = self.manager.Queue()
        self.bm_queue = self.manager.Queue()

        # Create global database access
        # self.graph = self.manager.Graph()
    
    def log(self, message):
        timestamp = time.strftime('%H:%M:%S', time.localtime())
        print('{} {}'.format(timestamp, message))
        

# Load the general manager
dome = DomeMain()
bm = BenchMark(dome, time.time())
bm.start()

# loadWebProperty()

# Create services
web_updater = WebUpdater(dome)
am = AutomationService(dome)
ha_updater = HAUpdater(dome.parser_queue)

# Start ParserService
pm = ParserService(dome)
pm.register(dome.log)
pm.start()

# Loading dummies for testing
# loadAutomation()
# loadWPAutomation()

# Start HALoader
dome.bm_queue.put(('loader', 'start', time.time()))
loop = asyncio.get_event_loop()
loop.run_until_complete(load(dome.parser_queue))

dome.loader_finished.wait()
dome.bm_queue.put(('loader', 'stop', time.time()))

# Start Automation Manager
am.register(dome.log)
am.start()

# Start HAUpdate
ha_updater.start()

time.sleep(3)

# Start WebUpdater
web_updater.start()

# Keep this thread alive while any child is alive
while(ha_updater.is_alive()):
    time.sleep(2)

del dome