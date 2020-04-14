from watchdog.events import PatternMatchingEventHandler


class Handler(PatternMatchingEventHandler):
    def __init__(self, patterns=['*.pdf']):
        super(Handler, self).__init__(patterns=patterns,
                                      ignore_directories=True,
                                      case_sensitive=False)

    def on_created(self, event):
        print('created')

    def on_deleted(self, event):
        print('deleted')

    def on_moved(self, event):
        print('moved')

    def on_modified(self, event):
        print('modified')
