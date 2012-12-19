import zmq
context = zmq.Context.instance()

sock = context.socket(zmq.REQ)
sock.connect('tcp://localhost:5555')

message = raw_input('Enter a message: ')

sock.send(message)

response = sock.recv()

print response
