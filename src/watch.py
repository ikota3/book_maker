import sys
import time
import subprocess
from watchdog.observers import Observer
from handler.handler import Handler


def watch(path, extensions):
    print(['*.%s' % extension for extension in extensions])
    event_handler = Handler(['*.%s' % extension for extension in extensions])
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
        print('Usage: ', '%s dir_to_watch [extensions]' % sys.argv[0])
    elif len(sys.argv) == 2:
        watch(sys.argv[1], ['pdf'])
    else:
        watch(sys.argv[1], sys.argv[2:])
