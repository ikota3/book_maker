import os
import subprocess
from watchdog.events import PatternMatchingEventHandler


class Handler(PatternMatchingEventHandler):
    def __init__(self, patterns=['*.pdf']):
        super(Handler, self).__init__(patterns=patterns,
                                      ignore_directories=True,
                                      case_sensitive=False)

    def on_created(self, event):
        print('!Create Event!')
        file_path = os.path.join(os.path.dirname(__file__), '../../getISBN.sh')
        cmd = f'{file_path} {event.src_path}'
        result = subprocess.call(cmd, shell=True)
        print(f'Result is {result}')

    def on_deleted(self, event):
        print('!Delete Event!')

    def on_moved(self, event):
        print('!Move Event!')

    def on_modified(self, event):
        print('!Modify Event!')
