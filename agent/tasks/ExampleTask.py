import time

from .AbstractTask import AbstractTask

# no internal dependencies


class ExampleTask(AbstractTask):
    @staticmethod
    def get_name():
        return "ExampleTask"

    def run_task(self, body):
        # ExampleTask just waits for 12 seconds
        time.sleep(12)

