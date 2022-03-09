# A simple wrapper to create a singleton emitter for the entire application
# Use the following import to access this same emitter from anywhere:
#
#     from agent.rabbitpy_wrapper import rabbitpy_emitter as emitter
#
#

from agent.emitter import RabbitMqEmitter

rabbitpy_emitter = RabbitMqEmitter()
