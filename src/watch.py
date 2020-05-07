import sys
import time
from watchdog.observers import Observer
from src.handler.handler import Handler


def watch(input_path, output_path, extensions):
    print([f'*.{extension}' for extension in extensions], flush=True)
    event_handler = Handler(input_path=input_path,
                            output_path=output_path,
                            patterns=[f'*.{extension}' for extension in extensions])
    observer = Observer()
    observer.schedule(event_handler, input_path, recursive=False)
    observer.start()
    print('--Start Observer--', flush=True)
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
        print('Usage: ', f'{sys.argv[0]} input_path [output_path] [extensions]', flush=True)
        sys.exit()
    elif len(sys.argv) == 2:
        watch(sys.argv[1], sys.argv[1], ['pdf'])
    elif len(sys.argv) == 3:
        watch(sys.argv[1], sys.argv[2], ['pdf'])
    else:
        watch(sys.argv[1], sys.argv[2], sys.argv[3:])
