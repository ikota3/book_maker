import os
import subprocess
from src.isbn_from_pdf import get_isbn_from_pdf, NoSuchISBNException
from watchdog.events import PatternMatchingEventHandler


class Handler(PatternMatchingEventHandler):
    def __init__(self, patterns=None):
        if patterns is None:
            patterns = ['*.pdf']
        super(Handler, self).__init__(patterns=patterns,
                                      ignore_directories=True,
                                      case_sensitive=False)

    def on_created(self, event):
        print('!Create Event!')
        shell_path = os.path.join(os.path.dirname(__file__), '../../getISBN.sh')
        pdf_path = event.src_path
        cmd = f'{shell_path} {pdf_path}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            # Retrieve ISBN
            isbn = result.stdout.strip()
            print(f'isbn from shell -> {isbn}')
            # TODO rename file to isbn.pdf

        else:
            try:
                # Get isbn from pdf barcode or text
                isbn = get_isbn_from_pdf(pdf_path)
                print(f'isbn from python -> {isbn}')
                # TODO rename file to isbn.pdf

            except NoSuchISBNException as e:
                print(e.args[0])
                print(f'Move {os.path.basename(pdf_path)} to temporary folder.')
                # TODO move file to tmp dir
