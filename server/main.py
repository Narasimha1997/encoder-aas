#!/bin/python3

import argparse
from frontend import ZMQSource, initialize_environment, ZMQSink

parser = argparse.ArgumentParser()
parser.add_argument('--workers', help = "Number of tensorflow serving instances", default = 2, required = False, type = int)
parser.add_argument('--batch', help = 'Maximum requests in the queue to batch for', default = 1, required = False, type = int)
parser.add_argument('--port', help = 'Port for frontend', default = '8000', required = False, type = str)
parser.add_argument('--portpub', help = 'Port for frontend', default = '8001', required = False, type = str)



if __name__ == "__main__":

    args = parser.parse_args()
    inStream, outStream, master = initialize_environment(args)
    master.startWorkers()

    zmqSource = ZMQSource(args.port)
    zmqSink = ZMQSink(outStream, 0, args.portpub)
    zmqSink.start()

    for data in zmqSource.connector() :
        inStream.addRequest(data)




