import zmq
from pubsub_zmq import publisher
import logging
logging.basicConfig(level = logging.INFO)


from runtime_impl import InputQueueManager, OutputQueueManager, MasterProcessor
import time 
from multiprocessing import Process
import json

class ZMQSource :
    
    def __init__(self , port) :
        self.port = port 
        self.context = zmq.Context()
    
    def connector(self) :
        receiver = self.context.socket(zmq.PULL)
        receiver.connect("tcp://0.0.0.0:{}".format(self.port))
        while True :
            data = receiver.recv_json()
            #validate request data for these terms :
            print('Got data')
            if 'id' not in data or 'client' not in data or 'text' not in data :
                logging.error("Invalid payload {}  ignored".format(data))
                continue

            logging.info("frontend got payload {}".format(data))
            yield data 



class ZMQSink(Process) :
    
    def __init__(self, queue, idx, port, **kwargs) :

        super(ZMQSink, self).__init__()

        self.queue = queue
        self.idx = idx

        self.port = port


    def run(self) :

        sender = publisher.Publisher(
            'tcp://0.0.0.0:{}'.format(self.port),
            identity = 'USE encoder'
        )

        #print(port)
        output_queue = self.queue.getQueue()

        while True :    
            response = output_queue.get(block = True)
            logging.info("Publishing result client={} id={}".format(
                response['client'], response['id']
            ))

            response['result'] = response['result'].tolist()

            response_str = json.dumps(response)
            
            #publish
            
            sender.run(response['client'], response_str)
            print('Done')

def initialize_environment(args) :
    
    n_workers = args.workers 
    n_batch = args.batch

    input_queues = InputQueueManager(n_workers, n_batch)
    output_queue = OutputQueueManager()

    workController = MasterProcessor(n_workers, input_queues.getQueues(), output_queue.getQueue())

    return (input_queues, output_queue, workController)



"""im, om, wc =initialize_environment(Args())
wc.startWorkers()

#start sink
sink = ZMQSink(om, 0)
sink.start()

idx = 0

while True :

    request = {"id" : idx , "text" : "Hello world"}
    im.addRequest(request)
    idx +=1
    time.sleep(1)"""