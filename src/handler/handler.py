import os
import shutil
import datetime
import subprocess
from src.isbn_from_pdf import get_isbn_from_pdf, NoSuchISBNException, NoSuchOCRToolException
from watchdog.events import PatternMatchingEventHandler
from src.bookinfo_from_isbn import book_info_from_google, book_info_from_openbd, NoSuchBookInfoException
from src.gui.log_handler import Message, LogStatus


class Handler(PatternMatchingEventHandler):
    def __init__(self, queue, input_path, output_path, patterns=None):
        if patterns is None:
            patterns = ['*.pdf']
        super(Handler, self).__init__(patterns=patterns,
                                      ignore_directories=True,
                                      case_sensitive=False)
        self.queue = queue
        self.input_path = input_path
        # If the output_path is equal to input_path, then make a directory named with current time
        if input_path == output_path:
            self.output_path = os.path.join(self.input_path, datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        else:
            self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)

        # Create tmp directory inside of output directory
        self.tmp_path = os.path.join(self.output_path, 'tmp')
        os.makedirs(self.tmp_path, exist_ok=True)

    def __del__(self):
        # Delete the tmp directory, when the directory is empty
        tmp_files_len = len(os.listdir(self.tmp_path))
        if tmp_files_len == 0:
            os.rmdir(self.tmp_path)

        # Delete the output directory, when the directory is empty
        output_files_len = len(os.listdir(self.output_path))
        if output_files_len == 0:
            os.rmdir(self.output_path)

    def _book_info_from_each_api(self, isbn, event_src_path):
        google_book_info = None
        try:
            google_book_info = book_info_from_google(isbn)
        except NoSuchBookInfoException as e:
            self.queue.put(Message(LogStatus.WARNING, e.args[0]))

        if google_book_info:
            self.queue.put(
                Message(
                    LogStatus.INFO,
                    f'<Google> title: {google_book_info.title}, author: {google_book_info.author}'
                )
            )
            self._rename_and_move_pdf(google_book_info, event_src_path)
            return

        openbd_book_info = None
        try:
            openbd_book_info = book_info_from_openbd(isbn)
        except NoSuchBookInfoException as e:
            self.queue.put(Message(LogStatus.WARNING, e.args[0]))

        if openbd_book_info:
            self.queue.put(
                Message(
                    LogStatus.INFO,
                    f'<openBD> title: {openbd_book_info.title}, author: {openbd_book_info.author}'
                )
            )
            self._rename_and_move_pdf(openbd_book_info, event_src_path)

    def _rename_and_move_pdf(self, book_info, event_src_path):
        # Rename pdf file to formatted name
        pdf_rename_path = os.path.join(os.path.dirname(event_src_path), f'[{book_info.author}]{book_info.title}.pdf')
        os.rename(event_src_path, pdf_rename_path)

        # If pdf file already exists, move file to tmp directory
        output_path_with_basename = os.path.join(self.output_path, os.path.basename(pdf_rename_path))
        if os.path.isfile(output_path_with_basename):
            shutil.move(pdf_rename_path, self.tmp_path)
            self.queue.put(
                Message(
                    LogStatus.WARNING,
                    f'PDF file already exists! Move {os.path.basename(pdf_rename_path)} to {self.tmp_path}'
                )
            )
        else:
            shutil.move(pdf_rename_path, self.output_path)
            self.queue.put(
                Message(
                    LogStatus.INFO,
                    f'Move {os.path.basename(pdf_rename_path)} to {self.output_path}'
                )
            )

    def on_created(self, event):
        shell_path = os.path.join(os.path.dirname(__file__), '../../getISBN.sh')
        event_src_path = event.src_path
        cmd = f'{shell_path} {event_src_path}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        try:
            if result.returncode == 0:
                # Retrieve ISBN from shell
                isbn = result.stdout.strip()
                self.queue.put(
                    Message(
                        LogStatus.INFO,
                        f'ISBN from Shell -> {isbn}'
                    )
                )
                self._book_info_from_each_api(isbn, event_src_path)

            else:
                # Get ISBN from pdf barcode or text
                isbn = get_isbn_from_pdf(event_src_path)
                self.queue.put(
                    Message(
                        LogStatus.INFO,
                        f'ISBN from Python -> {isbn}'
                    )
                )
                self._book_info_from_each_api(isbn, event_src_path)

        except (NoSuchISBNException, NoSuchOCRToolException) as e:
            # NoSuchISBNException will be thrown when the shell command has failure and cannot find isbn using python.
            if isinstance(e, NoSuchISBNException):
                self.queue.put(Message(LogStatus.WARNING, e.args[0]))

            # raise the error. because without OCR tool, cannot extract ISBN from image
            if isinstance(e, NoSuchOCRToolException):
                self.queue.put(Message(LogStatus.ERROR, e.args[0]))
                raise

            shutil.move(event_src_path, self.tmp_path)
            self.queue.put(
                Message(
                    LogStatus.WARNING,
                    f'Move {os.path.basename(event_src_path)} to {self.tmp_path}'
                )
            )
