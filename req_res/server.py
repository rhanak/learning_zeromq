import zmq
context = zmq.Context.instance()

sock = context.socket(zmq.REP)
sock.connect('tcp://localhost:8080')

while True:
    message = sock.recv()
    print message

    response = raw_input('Enter a response: ')
    sock.send(response)

