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