import logging
from abc import ABC, abstractmethod
import time


class AbstractTask(ABC):

    @staticmethod
    @abstractmethod
    def get_name():
        pass

    def __init__(self):
        self.logger = logging.getLogger(self.get_name())

    def pika_callback(self, ch, method, properties, body):
        self.run_timed_task(body=body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def rabbitpy_callback(self, message):
        self.run_timed_task(body=message.json())
        message.ack()

    @abstractmethod
    def run_task(self, body):
        pass

    def run_timed_task(self, body):
        start_time = time.time_ns() / 1000000
        self.logger.info(" [✓] Running ExampleTask: %s" % str(body))
        self.run_task(body=body)
        self.logger.info(" [✓] Done")
        end_time = time.time_ns() / 1000000
        duration = end_time - start_time
        self.logger.debug(' [✓] %s completed in %d ms' % (self.get_name(), duration))