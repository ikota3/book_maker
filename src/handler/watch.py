import time
import threading
from watchdog.observers import Observer
from src.handler.handler import Handler
from src.constants.log_constants import Message, LogStatus


class Watcher(threading.Thread):
    def __init__(self, queue, input_path, output_path, extensions):
        self.input_path = input_path
        self.output_path = output_path
        self.extensions = extensions
        super().__init__()
        self.queue = queue
        self.observer = Observer()
        self.setDaemon(True)
        self.event = threading.Event()

    def run(self, *args, **kwargs):
        """
        Run the observer for watching the directory.
        """
        while self.event.wait():
            self.queue.put(
                Message(
                    LogStatus.INFO, 'Watching %s files in %s' % (', '.join(self.extensions), self.input_path)
                )
            )
            event_handler = Handler(
                queue=self.queue,
                input_path=self.input_path,
                output_path=self.output_path,
                patterns=[f'*.{extension}' for extension in self.extensions],
            )

            self.observer.schedule(event_handler, self.input_path, recursive=False)
            self.observer.start()
            self.queue.put(Message(LogStatus.INFO, 'Start Observer'))
            try:
                while True:
                    time.sleep(1)
            except Exception as e:
                self.observer.unschedule_all()
                self.observer.stop()
                self.queue.put(Message(LogStatus.COMPLETED, 'End Observer'))
            self.observer.join()

    def set_event(self):
        """
        Set the event flag to true, for running the event
        """
        self.event.set()

    def stop_event(self):
        """
        Set the event flag to false, and stop the observer
        """
        self.event.clear()
        self.observer.unschedule_all()
        self.observer.stop()
        self.queue.put(Message(LogStatus.COMPLETED, 'End Observer'))
        self.observer.join()
