from .AbstractTask import AbstractTask


class QueueAwaker(AbstractTask):
    @staticmethod
    def get_name():
        return "QueueAwaker"

    def run_task(self, body):
        # Insert task logic here

        self.logger.info('Sending a new message to trigger ExampleTask...')
        # TODO: can we create DAGs like this?

        return
