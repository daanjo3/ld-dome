import asyncio
import time
# Add redland to the python path
import sys, os
sys.path.append(os.path.abspath(os.path.join('lib', 'redland', 'bindings', 'python')))
import RDF

from dome.db.graph import Graph

from dome.websocket.HALoader import load
from dome.websocket.HAUpdater import HAUpdater
# from dome.websocket.WebUpdater import WebUpdater
from dome.parser.ParserService import *
from dome.automations.AutomationService import AutomationService

# from dome.dummy.webpropertyDummy import loadWebProperty
# from dome.dummy.automationDummy import loadAutomation
# from dome.dummy.wpautomationDummy import loadWPAutomation

class DomeMain():
    def __init__(self):
        self.manager = Manager()
        # Create global event
        self.graph_readable_event = self.manager.Event()
        self.graph_readable_event.set()

        # Create global queues
        self.parser_queue = self.manager.Queue()
        self.automation_queue = self.manager.Queue()

        # Create global database access
        # self.graph = self.manager.Graph()
    
    def log(self, message):
        timestamp = time.strftime('%H:%M:%S', time.localtime())
        print('{} {}'.format(timestamp, message))
        

# Load the general manager
dome = DomeMain()

# Start ParserService
pm = ParserService(dome)
pm.register(dome.log)
pm.start()

# Loading dummies for testing
# loadWebProperty()
# loadAutomation()
# loadWPAutomation()

# Start HALoader
loop = asyncio.get_event_loop()
loop.run_until_complete(load(dome.parser_queue))

# Start WebUpdater
# web_updater = WebUpdater(dome)
# web_updater.start()

# Start Automation Manager
am = AutomationService(dome)
am.register(dome.log)
am.start()

# Start HAUpdater
ha_updater = HAUpdater(dome.parser_queue)
ha_updater.start()

# Keep this thread alive while any child is alive
while(ha_updater.is_alive()):
    time.sleep(2)

del dome