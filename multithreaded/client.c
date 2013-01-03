//
//  Multithreaded Hello World server
//
#include "zhelpers.h"
#include <pthread.h>

int main (void)
{
    int message_count = 0;
	
    void *context = zmq_ctx_new ();

    //  Socket to talk to clients
    void *request = zmq_socket (context, ZMQ_REQ);
    zmq_connect (request, "tcp://localhost:5555");

    while (message_count++ < 7500) {
        s_send (request, "Hello");

        //   reply back to client
        char *reply = s_recv (request);
        //printf ("Message %d Received reply: [%s]\n", ++message_count, reply);
        free (reply);
    }

    //  We never get here but clean up anyhow
    zmq_close (request);
    zmq_ctx_destroy (context);
    return 0;
}
