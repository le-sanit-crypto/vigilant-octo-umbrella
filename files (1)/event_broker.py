import redis
import threading
import json

class EventBroker:
    def __init__(self, host='localhost'):
        self.r = redis.Redis(host=host)
        self.pubsub = self.r.pubsub()

    def publish(self, channel, data):
        self.r.publish(channel, json.dumps(data))

    def subscribe(self, channel, handler):
        def listen():
            self.pubsub.subscribe(channel)
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    handler(json.loads(message['data']))
        t = threading.Thread(target=listen)
        t.daemon = True
        t.start()