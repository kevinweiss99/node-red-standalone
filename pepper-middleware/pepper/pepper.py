import qi
import requests
import traceback

UPDATE_EVENT = "update_event_list"

DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50

endpoint_base_path = None


class Wraps(object):
    def __init__(self, service_name, event):
        self.service_name = service_name
        self.event = event

    def callback(self, *args):
        print(args, self.service_name, self.event)

        global endpoint_base_path
        try:
            if self.event == UPDATE_EVENT:
                endpoint_base_path = args[0]
                print("Received server IP")
                refresh_events()
                return

            if not endpoint_base_path:
                print("endpoint_base_path not set")
                return

            data = {"service_name": self.service_name,
                    "event": self.event,
                    "data": args}

            requests.post(endpoint_base_path + "/event", json=data)
        except Exception as e:
            print(traceback.format_exc())
            log(ERROR, e, "callback")


def get_config(init=False):
    global endpoint_base_path
    if not endpoint_base_path:
        if not init:
            print("endpoint_base_path not set")
        return []

    try:
        return requests.get(endpoint_base_path + "/config").json()
    except Exception as e:
        print(traceback.format_exc())
        log(ERROR, e, "get_config")
        return []


def log(level, message, service_name):
    global endpoint_base_path
    if not endpoint_base_path:
        print("endpoint_base_path not set")
        return

    try:
        data = {"level": level, "message": str(message),
                "serviceName": service_name}

        requests.post(endpoint_base_path + "/log", json=data)
    except Exception:
        print(traceback.format_exc())


def refresh_events(init=False):
    global subscriber_list
    global session

    for signal, link_id in subscriber_list:
        signal.signal.disconnect(link_id)

    del subscriber_list[:]

    config = get_config(init)
    config.append({"service_name": "ALMemory", "event": UPDATE_EVENT})

    for config_item in config:
        try:
            wrap = Wraps(config_item["service_name"], config_item["event"])

            subscriber = session.service(
                wrap.service_name).subscriber(wrap.event)
            callback = getattr(wrap, "callback")
            link_id = subscriber.signal.connect(callback)

            subscriber_list.append((subscriber, link_id))
        except Exception as e:
            print(traceback.format_exc())
            log(ERROR, e, "refresh_events")


pepper = qi.Application()
pepper.start()
session = pepper.session

subscriber_list = []
refresh_events(True)
print("Waiting for IP information")

pepper.run()
