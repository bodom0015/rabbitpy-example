# rabbitpy-example
A sample RabbitMQ emitter and listener usage pattern implemented using [rabbitpy](https://rabbitpy.readthedocs.io/en/latest/)


# Prerequisites
* A running RabbitMQ instance
* Either Docker or Python installed

To run RabbitMQ using Docker, you can use the following command:
```bash
docker run -d --name rabbit \
           -e RABBITMQ_DEFAULT_USER='guest' \
           -e RABBITMQ_DEFAULT_PASS='guest' \
           -p 5672:5672 \
           -p 15672:15672 \
           rabbitmq:management
```

You can then connect to AMQP using `localhost:5672`, or log into the management console 
in your browser at http://localhost:15672 using the credentials above.

## Cleanup
Don't forget to clean up this container afterward with `docker rm -f rabbit`


# Usage
This example has two components that share configuration between them:
* `main.py` - uses a RabbitMqEmitter to publish messages to any queue
* `agent/main.py` - standalone executable that uses a RabbitMqListener to process messages


## Configuration
Both components use the following environment variables:

| Name | Description | Default Value |
| ---- | ------------| ------------- |
| `RABBITMQ_URI` | URI to use to access RabbitMQ | `amqp://guest:guest@localhost:5672/%2f` |
| `RABBITMQ_EXCHANGE` | RabbitMQ exchange to use | `''` |

Additionally, the Listener takes additional configuration to tell it which queue to watch:

| Name | Description | Default Value |
| ---- | ------------| ------------- |
| `RABBITMQ_QUEUENAME` | Queue to watch for messages | `ExampleTask` |


## Running with Docker (recommended)
To build the associated Docker images, you can run the following:
```bash
docker build -t rabbitpy-emitter .
docker build -t rabbitpy-listener -f agent/Dockerfile agent
```

To run the `rabbitpy-emitter` (main application / publisher):
```bash
docker run -d --rm \
           -e RABBITMQ_URI='amqp://guest:guest@localhost:5672/%2f' \
           -e RABBITMQ_EXCHANGE='' \
           rabbitpy-emitter
```

To run the `rabbitpy-listener` (scalable agents / runners):
```bash
docker run -d --rm \
           -e RABBITMQ_URI='amqp://guest:guest@localhost:5672/%2f' \
           -e RABBITMQ_EXCHANGE='' \
           -e RABBITMQ_QUEUENAME='ExampleTask' \
           rabbitpy-listener
```

NOTE: You can run as many containers for the emitter / listeners as you want.


## Running with Python
To run the main application (emitter / publisher), run the following:
```bash
python ./main.py
```

To run the listener / agent / runner application:
```bash
python ./agent/main.py
```


# Additional Notes

## Emitter
The emitter is a singleton that can publish messages to any queue. From anywhere in the main application,
we can use the following import to access the existing instance of the emitter:
```python
from agent.rabbitpy_wrapper import rabbitpy_emitter as emitter
```

We can use this emitter to publish messages to a particular queue using the `routing_key`:
```python
body = {'hello': 'world', 'it': 'works'}
emitter.publish(body=body, routing_key='ExampleTask')
```

## Listener
Each listener runs as a separate Docker container, which allows us to scale them up and down 
independently of one another. 

# TODOs

* binding queues to non-default exchange

