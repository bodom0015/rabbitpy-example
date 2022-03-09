import os
import logging
import sys
import time
from agent.rabbitpy_wrapper import rabbitpy_emitter as emitter

DEBUG = os.getenv('DEBUG', 'true').lower() in ('true', '1', 't')

# configure logging
if DEBUG:
    logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.INFO)

if __name__ == '__main__':
    try:
        while True:
            routing_key = 'ExampleTask'
            body = {'hello': 'world', 'it': 'works'}
            logging.info('Sending test message: %s' % body)
            emitter.publish(body=body, routing_key=routing_key)
            time.sleep(10)
    except KeyboardInterrupt:
        sys.exit(1)
    finally:
        emitter.close()
