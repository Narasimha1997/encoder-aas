from multiprocessing import Queue, Process

from sparse_encoder_impl import SparseEncoder
from tf_inference_impl import EmbeddingGenerationEngine
# a simple round robin load balancer
class QueueScheduler :

    def __init__(self, number_of_workers) :
        self.n_workers = number_of_workers
        self.current_idx = 0 

    def decideSchedule(self) :
        queue_idx = (self.current_idx % self.n_workers)
        self.current_idx +=1
        return queue_idx

class BatchingBuffer :

    def __init__(self, size = 1) :
        self.buffer = []
        self.max_size = 1
    
    def add(self, request) :

        self.buffer.append(request)
    
    def getLength(self) :

        return len(self.buffer)
    
    def isFull(self) :
        return len(self.buffer) >= self.max_size
    
    def clear(self) :
        return self.buffer.clear()
    
    def getElements(self) :
        return self.buffer.copy()

class InputQueueManager :

    def __init__(self, nb_worker, max_batch = 1) :

        self.n_workers = nb_worker 
        self.buffers = [BatchingBuffer(max_batch) for i in range(nb_worker)]

        self.queues = [Queue() for i in range(nb_worker)]

        self.loadBalancer = QueueScheduler(nb_worker)
    
    def addRequest(self, request) :

        idx = self.loadBalancer.decideSchedule()
        print('Sending load to ', idx)
        
        buffer = self.buffers[idx]
        buffer.add(request)

        print(buffer.buffer, buffer.isFull())

        if buffer.isFull() :

            #get elements
            buffered_requests = buffer.getElements()
            buffer.clear()

            #push it to the queue :
            queue = self.queues[idx]
            queue.put(buffered_requests)
    
    def getQueues(self) :
        return self.queues


class UniversalSentenceEncoder(Process) :

    def __init__(self, inputConnector, outputConnector, idx, **kwargs) :
        super(UniversalSentenceEncoder, self).__init__()
        self.sentence_encoder = SparseEncoder()

        self.inputStream = inputConnector
        self.idx = idx

        self.outputConnector = outputConnector
    
    def __preprocess_requests(self, request) :

        request_ids = [req['id'] for req in request]
        sentences = [req['text'] for req in request]

        clients = [req['client'] for req in request]

        return request_ids, clients, sentences
    

    def __postprocess_results(self, outputs, request_ids, clients) :

        return [
            {"id" : idx, "result" : result, "client" : client} for idx, result, client in zip(request_ids, outputs, clients)
        ]

    
    def run(self) :

        embeddings = EmbeddingGenerationEngine()
        
        while True :
            request = self.inputStream.get(block = True)

            #print('Consumed ' ,  request)

            # process requests here
            request_ids, clients, sentences = self.__preprocess_requests(request)
            values, indices, dense_shape = self.sentence_encoder.getSparseEncodings(
                sentences
            )

            try :
                outputs = embeddings.infer(
                    values, indices, dense_shape
                )

                outputs = self.__postprocess_results(outputs, request_ids, clients)
                for output in outputs :
                    self.outputConnector.put(output)
            except Exception as e :
                print("error")
                print(e)

class OutputQueueManager :
    
    def __init__(self) :
        self.queue = Queue()
    
    def putResult(self, result) :
        self.queue.put(result)
    
    def getQueue(self) :
        return self.queue

class MasterProcessor :

    def __init__(self, n_workers, queues, output_queues) :

        self.n_workers = n_workers
        self.processPool = [
            UniversalSentenceEncoder(
                queues[idx],
                output_queues,
                idx,
            ) for idx in range(n_workers)
        ]
    
    
    def startWorkers(self) :
        [process.start() for process in self.processPool]
    
    def terminateWorkers(self) :
        for process in self.processPool :
            process.terminate()
        
        
#test
def test() :

    N_Worker = 4
    queueManager = InputQueueManager(N_Worker)
    queues = queueManager.getQueues()
    ps = []
    import time

    for idx in range(N_Worker) :
        q = queues[idx]
        process = UniversalSentenceEncoder(q, idx)
        process.start()
        ps.append(process)
    
    #start sending requests one by one 
    request = {"id" : 0, "text" : "Hello,world"}
    idx = 0
    while True :
        request['id'] = idx 
        queueManager.addRequest(request)

        time.sleep(1)
        idx +=1
#test()


    