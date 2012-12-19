import zmq
import re

context = zmq.Context.instance()

sock = context.socket(zmq.SUB)
sock.connect('tcp://localhost:5556')

zipcode = '10001'

sock.setsockopt(zmq.SUBSCRIBE,zipcode)

avg = 0.0 
for i in range(10):
  response = sock.recv()
  r = re.compile('[ \t\n\r]+')
  fields = r.split(response)
  if len(fields) > 2:
    avg += float(fields[1])

print "Average temperature for zipcode %s was %f" % (zipcode, avg/10)
