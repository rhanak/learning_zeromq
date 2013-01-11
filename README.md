learning_zeromq
===============

../c -ll /usr/local/lib -l -q server.c

./c -li ../include -ll /usr/local/lib -l -q wuserver.c

../c -li ../include -ll /usr/local/lib -l -q tasksink.c

**CH. 1

Request-reply, which connects a set of clients to a set of services. This is a remote procedure call and task distribution pattern.
Publish-subscribe, which connects a set of publishers to a set of subscribers. This is a data distribution pattern.
Pipeline, which connects nodes in a fan-out / fan-in pattern that can have multiple steps, and loops. This is a parallel task distribution and collection pattern.

Pipeline
In the Parallel Pipeline the workers connect upstream to the ventilator, and downstream to the sink. This means you can add workers arbitrarily. If the workers bound to their endpoints, you would need (a) more endpoints and (b) to modify the ventilator and/or the sink each time you added a worker. We say that the ventilator and sink are 'stable' parts of our architecture and the workers are 'dynamic' parts of it.

The pipeline pattern also exhibits the "slow joiner" syndrome, leading to accusations that PUSH sockets don't load balance properly. If you are using PUSH and PULL, and one of your workers gets way more messages than the others, it's because that PULL socket has joined faster than the others, and grabs a lot of messages before the others manage to connect.

Contexts in 0MQ
You should create and use exactly one context in your process. Technically, the context is the container for all sockets in a single process, and acts as the transport for inproc sockets, which are the fastest way to connect threads in one process.

When Exiting
Always close a message the moment you are done with it, using zmq_msg_close().
If you are opening and closing a lot of sockets, that's probably a sign you need to redesign your application.
When you exit the program, close your sockets and then call zmq_ctx_destroy(). This destroys the context.


Upgrading from 2.2 to 3.2
Finally, we added context monitoring via the zmq_ctx_set_monitor() call, which lets you track connections and disconnections, and other events on sockets.

**CH. 2 Sockets and Patterns

To create a connection between two nodes you use zmq_bind() in one node, and zmq_connect() in the other. As a general rule of thumb, the node which does zmq_bind() is a "server", sitting on a well-known network address, and the node which does zmq_connect() is a "client", with unknown or arbitrary network addresses. Thus we say that we "bind a socket to an endpoint" and "connect a socket to an endpoint", the endpoint being that well-known network address.

The network connection itself happens in the background, and ØMQ will automatically re-connect if the network connection is broken (e.g. if the peer disappears and then comes back).

A server node can bind to many endpoints (that is, a combination of protocol and address) and it can do this using a single socket. This means it will accept connections across different transports

The upshot is that you should usually think in terms of "servers" as static parts of your topology, that bind to more-or-less fixed endpoints, and "clients" as dynamic parts that come and go and connect to these endpoints.

Sockets have types. The socket type defines the semantics of the socket, its policies for routing messages inwards and outwards, queuing, etc.

ØMQ sockets carry messages, like UDP, rather than a stream of bytes as TCP does. A ØMQ message is length-specified binary data. We'll come to messages shortly, their design is optimized for performance and so a little tricky

ØMQ sockets do their I/O in a background thread. This means that messages arrive in local input queues, and are sent from local output queues, no matter what your application is busy doing.

ØMQ is not a neutral carrier, it imposes a framing on the transport protocols it uses. This framing is not compatible with existing protocols, which tend to use their own framing. For example, compare an HTTP request, and a ØMQ request, both over TCP/IP.

We said that ØMQ does I/O in a background thread. One I/O thread (for all sockets) is sufficient for all but the most extreme applications. When you create a new context it starts with one I/O thread. The general rule of thumb is to allow one I/O thread per gigabyte of data in or out per second.

Exclusive pair, which connects two sockets exclusively. This is a pattern you should use only to connect two threads in a process.

These are the socket combinations that are valid for a connect-bind pair (either side can bind):
PUB and SUB
REQ and REP
REQ and ROUTER
DEALER and REP
DEALER and ROUTER
DEALER and DEALER
ROUTER and ROUTER
PUSH and PULL
PAIR and PAIR

You may send zero-length messages, e.g. for sending a signal from one thread to another.
ØMQ guarantees to deliver all the parts (one or more) for a message, or none of them.
ØMQ does not send the message (single, or multi-part) right away but at some indeterminate later time. A multi-part message must therefore fit in memory.
A message (single, or multi-part) must fit in memory. If you want to send files of arbitrary sizes, you should break them into pieces and send each piece as separate single-part messages.
You must call zmq_msg_close() when finished with a message, in languages that don't automatically destroy objects when a scope closes.

ØMQ aims for decentralized intelligence but that doesn't mean your network is empty space in the middle. It's filled with message-aware infrastructure and quite often, we build that infrastructure with ØMQ. The ØMQ plumbing can range from tiny pipes to full-blown service-oriented brokers. The messaging industry calls this "intermediation", meaning that the stuff in the middle deals with either side. In ØMQ we call these proxies, queues, forwarders, device, or brokers, depending on the context.

The Dynamic Discovery Problem

There are quite a few answers to this but the very simplest answer is to add an intermediary, that is, a static point in the network to which all other nodes connect. In classic messaging, this is the job of the "message broker". ØMQ doesn't come with a message broker as such, but it lets us build intermediaries quite easily.
















Typical Problems 0MQ solves

How do we handle I/O? Does our application block, or do we handle I/O in the background? This is a key design decision. Blocking I/O creates architectures that do not scale well. But background I/O can be very hard to do right.
How do we handle dynamic components, i.e. pieces that go away temporarily? Do we formally split components into "clients" and "servers" and mandate that servers cannot disappear? What then if we want to connect servers to servers? Do we try to reconnect every few seconds?
How do we represent a message on the wire? How do we frame data so it's easy to write and read, safe from buffer overflows, efficient for small messages, yet adequate for the very largest videos of dancing cats wearing party hats?
How do we handle messages that we can't deliver immediately? Particularly, if we're waiting for a component to come back on-line? Do we discard messages, put them into a database, or into a memory queue?
Where do we store message queues? What happens if the component reading from a queue is very slow, and causes our queues to build up? What's our strategy then?
How do we handle lost messages? Do we wait for fresh data, request a resend, or do we build some kind of reliability layer that ensures messages cannot be lost? What if that layer itself crashes?
What if we need to use a different network transport. Say, multicast instead of TCP unicast? Or IPv6? Do we need to rewrite the applications, or is the transport abstracted in some layer?
How do we route messages? Can we send the same message to multiple peers? Can we send replies back to an original requester?
How do we write an API for another language? Do we re-implement a wire-level protocol or do we repackage a library? If the former, how can we guarantee efficient and stable stacks? If the latter, how can we guarantee interoperability?
How do we represent data so that it can be read between different architectures? Do we enforce a particular encoding for data types? How far is this the job of the messaging system rather than a higher layer?
How do we handle network errors? Do we wait and retry, ignore them silently, or abort?

Solutions 0MQ Provides

It handles I/O asynchronously, in background threads. These communicate with application threads using lock-free data structures, so concurrent ØMQ applications need no locks, semaphores, or other wait states.
Components can come and go dynamically and ØMQ will automatically reconnect. This means you can start components in any order. You can create "service-oriented architectures" (SOAs) where services can join and leave the network at any time.
It queues messages automatically when needed. It does this intelligently, pushing messages as close as possible to the receiver before queuing them.
It has ways of dealing with over-full queues (called "high water mark"). When a queue is full, ØMQ automatically blocks senders, or throws away messages, depending on the kind of messaging you are doing (the so-called "pattern").
It lets your applications talk to each other over arbitrary transports: TCP, multicast, in-process, inter-process. You don't need to change your code to use a different transport.
It handles slow/blocked readers safely, using different strategies that depend on the messaging pattern.
It lets you route messages using a variety of patterns such as request-reply and publish-subscribe. These patterns are how you create the topology, the structure of your network.
It lets you create proxies to queue, forward, or capture messages with a single call. Proxies can reduce the interconnection complexity of a network.
It delivers whole messages exactly as they were sent, using a simple framing on the wire. If you write a 10k message, you will receive a 10k message.
It does not impose any format on messages. They are blobs of zero to gigabytes large. When you want to represent data you choose some other product on top, such as Google's protocol buffers, XDR, and others.
It handles network errors intelligently. Sometimes it retries, sometimes it tells you an operation failed.
It reduces your carbon footprint. Doing more with less CPU means your boxes use less power, and you can keep your old boxes in use for longer. Al Gore would love ØMQ.

This examples shows that the subscription filter rejects or accepts the entire multi-part message (key plus data). You won't get part of a multi-part message, ever.`

** Chapter 3 - Advanced Request-Reply Patterns


