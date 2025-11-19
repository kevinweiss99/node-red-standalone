import logging

logger = logging.getLogger(__name__)


class Dummy2():
    def __init__(self, service, name):
        self.service = service
        self.name = name

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration
    
    def __add__(self, other):
        return Dummy("Add")

    def dummy_function(self, *args, **kwargs):
        logger.debug("Trying to access {}.{} with parameter: {}, {}".format(self.service, self.name, args, kwargs))
        return Dummy("Inner dummy function")

class Dummy():
    def __init__(self, service):
        self.service = service

    def __getattribute__(self, name):
        if name == "service":
            return object.__getattribute__(self, name)

        dummy2 = Dummy2(self.service, name)
        return dummy2.dummy_function

    def __iter__(self):
        return self
    
    def __next__(self):
        raise StopIteration
    
    def __add__(self, other):
        return Dummy("Add")
