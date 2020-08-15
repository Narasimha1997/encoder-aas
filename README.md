# encoder-aas
An architecture providing Universal Sentence Encoder as a service by exploiting job-level parallelism of multi-core architectures and can be used as a transformer model for downstream NLP and NLU tasks like Language modelling, Sentiment Classification, Question Answering, Semantic Search and more. Inspired from Bert-as-a-service.

## Architecture:
*encoder-aas* uses highly asynchronous programming model to exploit Job level parallelism of multi-core processor machines, 
since it exploits job-level parallelism it can spin up highly concurrent and independant tensorflow session, each scheduled on a core.
The model we are using is Universal Sentence Encoder lite - more information can be found [here](https://www.tensorflow.org/hub/tutorials/semantic_similarity_with_tf_hub_universal_encoder_lite).
The model is very light weight and can run on a single processor, we expolited this opportunity to schedule multiple models on the same machine. The architecture is very simple and a developer can easily understand this.

![architecture](https://github.com/Narasimha1997/encoder-aas/blob/master/images/use_encoder.jpg "Architecture")

### Build the service:
You can use the dockerfile provided in `server/Dockerfile` to build the server. Follow the instructions below:
1. Build the docker container:
    ```
    docker build . -t use_encoder
    ```
2. Run the docker container:
    ```
    docker run --rm -ti --net=host use_encoder --workers=4 --batch=1 --port=8000 --portpub=8001
    ```
    Parameters:
      1. `workers` : Number of worker instances to run, use workers=number of cpus for max performance.
      2. `batch` : Workers will consume from the queue only when entries=batch, `batch=1` is the default.
      3. `port` : `ZMQSource` port
      4. `portpub` : Service will publish results at this port.

### Running the client:
We have provided a small client library that makes concurrent requests and and waits for responses. See `client` for its implementation.
Usage example is shown here:
```python
from use_client import EncoderClient
import time
results = []

def callback(result) :

    #print(result)
    results.append(result)

#create an encoder client
encoder = EncoderClient(host = '127.0.0.1', port = 8000, port_pub = 8001, callback=callback)

#start the receiver channel to receive results
encoder.createChannel()

sentences = ['Hello!', 'If you think you are bad, I am your dad!!', 'Just kiddnig', 'I am good']

for idx, sentence in enumerate(sentences)  :
    encoder.generateEmbeddings(idx, sentence)

while len(results) != len(sentences) :
    time.sleep(0.01)

print(len(results))

encoder.close()
```

In case of any problems or feature requests, please feel free to raise an issue.

### Acknowledgements:

[Bert-as-a-Service](https://github.com/hanxiao/bert-as-service)
