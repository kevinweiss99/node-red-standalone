import logging
import traceback

from ..pepper.connection import memory, session

logger = logging.getLogger(__name__)

class Publisher:
    """
    Initializes object and registers this class as a module in qi
    """
    subscribers = {}

    def subscribe(self, subscriber):
        if not subscriber.event in self.subscribers:
            self.subscribers[subscriber.event] = []

        if len(self.subscribers[subscriber.event]) == 0:
            memory.subscribeToEvent(subscriber.event, self.__class__.__name__, "publish", _async=True)

        logger.debug("Added subscription for event: " + subscriber.event)
        self.subscribers[subscriber.event].append(getattr(subscriber, subscriber.func_name))

    def unsubscribe(self, subscriber):
        if subscriber.event in self.subscribers:
            try:
                self.subscribers[subscriber.event].remove(getattr(subscriber, subscriber.func_name))
     
                logger.debug("Removed subscription for event: " + subscriber.event)
        
                if len(self.subscribers[subscriber.event]) == 0:
                    memory.unsubscribeToEvent(subscriber.event, self.__class__.__name__, _async=True)
                    logger.debug("No active subscriptions for event {} remaining. Removing memory subscription.".format(subscriber.event))
            except ValueError:
                logger.warning("Attempted to remove a non-existent subscription to an event:" + subscriber.event)
 
    def publish(self, event, data):
        logger.debug(f"Publishing event {event} with data: {data}")
        try:
            if event in self.subscribers:
                for callback in self.subscribers[event]:
                    
                        callback(event, data)
        except Exception as e:
            logger.error(e)
            logger.critical(traceback.format_exc())
