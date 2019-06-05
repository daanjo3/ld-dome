class Observable(object):
    def __init__(self):
        self.callbacks = []
    
    def register(self, callback):
        self.callbacks.append(callback)
    
    def unregister(self, callback):
        self.callbacks.remove(callback)
    
    def notify(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(*args, **kwargs)