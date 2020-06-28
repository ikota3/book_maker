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
        self.stop_event = threading.Event()
        self.setDaemon(True)

    def run(self, *args, **kwargs):
        while not self.stop_event.is_set():
            self.queue.put(Message(LogStatus.INFO, 'Watching %s files' % ', '.join(self.extensions)))
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

    def stop(self):
        self.observer.unschedule_all()
        self.observer.stop()
        self.queue.put(Message(LogStatus.COMPLETED, 'End Observer'))
        self.observer.join()
        self.stop_event.set()
