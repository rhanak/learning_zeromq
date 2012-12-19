import zmq
context = zmq.Context.instance()

sock = context.socket(zmq.REQ)
sock.bind('tcp://*:8080')

message = raw_input('Enter a message: ')

sock.send(message)

response = sock.recv()

print response
