import logging
import time

# no internal dependencies

class QueueAwaker:
    @staticmethod
    def get_name():
        return "QueueAwaker"

    def __init__(self):
        self.logger = logging.getLogger(QueueAwaker.get_name())

    def rmq_callback(self, ch, method, properties, body):
        self.run_task(body=body)

    def rabbitpy_callback(self, message):
        self.run_task(body=message.json())
        message.ack()

    def run_task(self, body):
        start_time = time.time_ns() / 1000000
        self.logger.info(" [✓] Running %s: %s" % (self.get_name(), str(body)))

        # Insert task logic here

        self.logger.info(" [✓] Done")
        end_time = time.time_ns() / 1000000
        duration = end_time - start_time
        self.logger.debug(' [✓] %s completed in %d ms' % (self.get_name(), duration))
