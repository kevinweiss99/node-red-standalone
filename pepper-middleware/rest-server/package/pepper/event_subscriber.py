class Subscriber:
    def __init__(self, event, callback):
        self.event = event
        self.func_name = callback.__name__
        setattr(self, self.func_name, callback)