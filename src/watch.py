import time
from watchdog.observers import Observer
from src.handler.handler import Handler
from src.gui.log_handler import LogHandler


def watch(input_path, output_path, extensions):
    LogHandler.info('Watching %s files' % ', '.join(extensions))
    event_handler = Handler(input_path=input_path,
                            output_path=output_path,
                            patterns=[f'*.{extension}' for extension in extensions])
    observer = Observer()
    observer.schedule(event_handler, input_path, recursive=False)
    observer.start()
    LogHandler.info('Start Observer')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.unschedule_all()
        observer.stop()
        LogHandler.info('--End Observer--')
    observer.join()
