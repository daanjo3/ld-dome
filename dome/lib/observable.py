class Observable(object):
    def __init__(self):
        self.callbacks = []
    
    def register(self, callback):
        print('New callback registered')
        self.callbacks.append(callback)
    
    def unregister(self, callback):
        print('Callback unregistered')
        self.callbacks.remove(callback)
    
    def notify(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(*args, **kwargs)