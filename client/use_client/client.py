import zmq
import uuid
import random
from threading import Thread
from pubsub_zmq import subscriber

import json

class EncoderReceiver(Thread) :

    def __init__(self, host, port_pub, client_id, callback) :
        Thread.__init__(self)
        self.client_id = client_id
        self.callback = callback

        self.receiver = subscriber.Subscriber(
            topics = [self.client_id],
            url = "tcp://{}:{}".format(host, port_pub),
            identity = 'USE receiver'
        )

    def run(self) :

        while True :
            client_id, response = self.receiver.receive()
            response = json.loads(response)
            self.callback(response)

class EncoderClient :

    def __init__(self, host, port, port_pub, callback) :

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.bind("tcp://{}:{}".format(host, port))

        self.client_id = self.generate_uuid()
        self.receiver  = EncoderReceiver(host, port_pub, self.client_id, callback)

    def createChannel(self) :
        self.receiver.start()
    
    def generate_uuid(self) :
        return str(random.randint(a = 100, b = 100000))
    
    def generateEmbeddings(self, idx, text) :

        payload = {"id" : idx, "client" : self.client_id, "text" : text}
        self.socket.send_json(payload)
        #print('Pushed payload')
    
    def close(self) :

        #self.receiver.receiver.clean()
        try:
            self.socket.close()
            self.receiver.receiver.socket.close()
        except Exception as e:
            print(e)            




#test
