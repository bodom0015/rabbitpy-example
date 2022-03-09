import json
import logging
import os
import pika

from pika import exceptions as pika_exceptions

from agent.tasks.QueueAwaker import QueueAwaker
from agent.tasks.ExampleTask import ExampleTask
from agent.constants import TaskNames, RABBITMQ_EXCHANGE, RABBITMQ_URI

# A classic pika-based emitter and listener, for comparison

RABBITMQ_CALLBACKS = {
    'QueueAwaker': QueueAwaker.pika_callback,
    'ExampleTask': ExampleTask.pika_callback,
}


class RabbitMqEmitter:
    def __init__(self):
        self.logger = logging.getLogger('agent.agent.rabbit.RabbitMqEmitter')
        self.connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URI))
        self.channel = self.connection.channel()

    def publish(self, routing_key, body):
        self.channel.queue_declare(queue=routing_key, durable=True)
        self.channel.basic_publish(exchange=RABBITMQ_EXCHANGE,
                                   routing_key=routing_key,
                                   properties=pika.BasicProperties(
                                       delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                                   ),
                                   body=bytearray(json.dumps(body), 'utf-8'))

    def close(self):
        self.logger.debug(" [x] Shutting down emitter")
        self.connection.close()


class RabbitMqListener(RabbitMqEmitter):

    def __init__(self, queue):
        super().__init__()
        self.queue_name = queue
        self.logger = logging.getLogger('agent.agent.rabbit.RabbitMqListener.%s' % queue)
        self.channel.queue_declare(queue=queue, durable=True)
        self.callback = RABBITMQ_CALLBACKS[queue]

    # TODO: Expand this to multiple Threads? (one listener thread per-task?)
    def start_consuming(self):
        self.logger.debug(" [✓] Started listening on queue: %s" % self.queue_name)
        while True:
            try:
                self.channel.basic_qos(prefetch_count=1)
                self.channel.basic_consume(queue=self.queue_name,
                                           auto_ack=False,
                                           on_message_callback=self.callback)
                self.channel.start_consuming()

            except pika_exceptions.ConnectionClosedByBroker:
                # Uncomment this to make the example not attempt recovery
                # from server-initiated connection closure, including
                # when the node is stopped cleanly
                #
                # break
                continue
            except pika_exceptions.AMQPChannelError as err:
                self.logger.error("Caught a channel error: {}, stopping...".format(err))
                break

            # Recover on all other connection errors
            except pika_exceptions.AMQPConnectionError:
                self.logger.warning("Connection was closed, retrying...")
                continue

    def close(self):
        self.logger.debug(' [⚠] Stopping listener on queue: %s' % self.queue_name)
        self.channel.stop_consuming()
        self.connection.close()
        self.logger.debug(' [×] Stopped listening on queue: %s' % self.queue_name)


class RabbitMqAgent:

    def __init__(self):
        self.logger = logging.getLogger('agent.agent.rabbit.RabbitMqAgent')
        self.emitter = None
        self.executors = []

    # Emitter works as a singleton: we should only need one to send messages to any queue
    def get_emitter(self):
        if self.emitter is None:
            self.emitter = RabbitMqEmitter()
        return self.emitter

    # Close any open channels and clear the RMQ connections from memory
    def close_all(self):
        for e in self.executors:
            e.close()

        self.executors.clear()

    # Creates and starts a new listener for the given queue with the given callback fn
    def add_listener(self, queue, callback):
        self.executors.append(RabbitMqListener(queue=queue, callback=callback))

    # Creates and starts a new listener for each known value in the TaskName enum
    def add_listeners(self):
        for queue in TaskNames:
            callback = RABBITMQ_CALLBACKS.get(queue.value)
            if callback is None:
                self.logger.warning('Canceling listener for %s: no callback found' % queue)
            else:
                self.add_listener(queue=queue.value, callback=callback)

    # Reset internal data and set up emitter + all listeners
    def init_app(self):
        self.close_all()
        self.executors.append(self.get_emitter())
        self.add_listeners()

