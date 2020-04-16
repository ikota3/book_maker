import sys
import time
from watchdog.observers import Observer
from src.handler.handler import Handler


def watch(path, extensions):
    print([f'*.{extension}' for extension in extensions])
    event_handler = Handler([f'*.{extension}' for extension in extensions])
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print('--Start Observer--')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.unschedule_all()
        observer.stop()
        print('--End Observer--', flush=True)
    observer.join()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: ', f'{sys.argv[0]} dir_to_watch [extensions]')
    elif len(sys.argv) == 2:
        watch(sys.argv[1], ['pdf'])
    else:
        watch(sys.argv[1], sys.argv[2:])
