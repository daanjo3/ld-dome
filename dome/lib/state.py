class BaseState:
        IDLE = (0, 'IDLE')
        FINISHED = (0, 'FINISHED')
    
        def __init__(self):
            self.state = self.IDLE
        
        def get(self):
            return self.state[0]
        
        def update(self, state):
            self.state = state
        
        def __str__(self):
            return self.state[1]
