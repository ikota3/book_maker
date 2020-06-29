import os
from queue import Queue
from datetime import datetime
from tkinter import (
    N,
    S,
    E,
    W,
    EW,
    NSEW,
    VERTICAL,
    Tk,
    Frame,
    Button,
    Entry,
    Text,
    Label,
    Scrollbar,
    StringVar,
    filedialog,
    messagebox
)
from tkinter.ttk import Combobox
from src.handler.watch import Watcher
from src.constants.log_constants import LogStatus

FILE_TYPES = [
    'pdf'
]

ROOT = Tk()


class BookMakerApp(Frame):
    """
    Book Maker Application
    """

    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.master.geometry('+1000+100')
        self.master.resizable(0, 0)
        self.master.title('Book Maker')

        self.dir_to_watch_path = StringVar()
        self.file_type_value = StringVar()
        self.log_box = None
        self.log_box_line_count = 1
        self.queue = Queue()
        self.watcher_thread = None

        self._create_widgets()

    def _create_widgets(self):
        """
        Create all widgets
        """

        # Main Frame
        main_frame = Frame(self)
        main_frame.grid(row=0, column=0, sticky=NSEW, padx=10, pady=10)

        # Dir to watch
        dir_to_watch_label = Label(main_frame, text='監視対象ディレクトリ')
        dir_to_watch_entry = Entry(
            main_frame,
            relief='solid',
            borderwidth=1,
            textvariable=self.dir_to_watch_path
        )
        dir_to_watch_button = Button(
            main_frame,
            text='参照',
            relief='solid',
            borderwidth=1,
            command=self._ask_folder
        )

        # File type
        file_type_label = Label(main_frame, text='ファイルの種類')
        file_type_combobox = Combobox(
            main_frame,
            state='readonly',
            values=FILE_TYPES,
            textvariable=self.file_type_value
        )
        file_type_combobox.current(0)

        # Execute
        execute_button = Button(
            main_frame,
            text='実行',
            relief='solid',
            borderwidth=1,
            command=self._execute
        )

        # Stop
        stop_button = Button(
            main_frame,
            text='停止',
            relief='solid',
            borderwidth=1,
            command=self._stop
        )

        # Log
        log_label = Label(main_frame, text='ログ')
        log_box = Text(main_frame, relief='solid', borderwidth=1)
        log_box.bind('<Key>', lambda e: "break")
        self.log_box = log_box

        # Log scroll bar
        scrollbar = Scrollbar(
            main_frame,
            orient=VERTICAL,
            command=log_box.yview,
        )
        log_box['yscrollcommand'] = scrollbar.set

        # Export log
        log_export_button = Button(
            main_frame,
            text='ログを出力',
            relief='solid',
            borderwidth=1,
            command=self._export_log
        )

        # Place all widgets
        dir_to_watch_label.grid(
            row=0, column=0, sticky=W, padx=(0, 7), pady=(10, 10)
        )
        dir_to_watch_entry.grid(
            row=0, column=1, sticky=EW, padx=(10, 10), pady=(10, 10)
        )
        dir_to_watch_button.grid(
            row=0, column=2, padx=(7, 0), pady=(10, 10)
        )

        file_type_label.grid(
            row=1, column=0, sticky=W, padx=(0, 7), pady=(10, 10)
        )
        file_type_combobox.grid(
            row=1, column=1, columnspan=2, sticky=EW, padx=(7, 0), pady=(10, 10)
        )

        execute_button.grid(
            row=2, column=0, columnspan=3, pady=(10, 20)
        )

        stop_button.grid(
            row=3, column=0, columnspan=3, pady=(10, 20)
        )

        log_label.grid(
            row=4, column=0, sticky=W, pady=(7, 0)
        )
        log_export_button.grid(
            row=4, column=1, columnspan=2, sticky=E, pady=(0, 7)
        )
        log_box.grid(
            row=5, column=0, columnspan=3, sticky=NSEW
        )
        scrollbar.grid(
            row=5, column=1, columnspan=2, sticky=(N, S, E), padx=(1, 1), pady=(1, 1)
        )

        # Fit the main frame to master
        self.grid_rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def _ask_folder(self):
        """
        When user clicked "参照"
        Pop up the filedialog for asking directory, and fill the path which user selected
        """
        path = filedialog.askdirectory()
        self.dir_to_watch_path.set(path)

    def _execute(self):
        """
        When user clicked "実行"
        Kick to handler
        """

        # Check path is correct
        if not self.dir_to_watch_path.get():
            messagebox.showerror('入力エラー', '監視対象のディレクトリを選択してください')
            return
        if not os.path.isdir(self.dir_to_watch_path.get()):
            messagebox.showerror('入力エラー', 'ディレクトリではありません')
            return

        # Check file type is correct
        if not self.file_type_value.get() or not self.file_type_value.get() in FILE_TYPES:
            messagebox.showerror(
                '入力エラー',
                'ファイルの種類が選択されていません\n' + ', '.join(FILE_TYPES) + 'の中から選択してください'
            )
            return

        # If the watcher thread is running, show the message box
        if self.watcher_thread:
            will_switch = messagebox.askyesnocancel(
                'エラー',
                'すでに実行中です\n監視している対象ディレクトリを切り替えますか?'
            )
            # If the user select no or cancel, return
            if not will_switch:
                return
            # If the user select yes, stop the watcher thread which exists
            self._stop()

        self.watcher_thread = Watcher(
            queue=self.queue,
            input_path=self.dir_to_watch_path.get(),
            output_path=self.dir_to_watch_path.get(),
            extensions=[self.file_type_value.get()],
        )
        self.watcher_thread.start()
        self.watcher_thread.set_event()
        self.after(100, self.insert_to_log_box)

    def insert_to_log_box(self):
        """
        Insert received message from other thread to log box
        """
        # If queue is not empty, insert message to log box
        if not self.queue.empty():
            message = self.queue.get()
            self.log_box.insert(
                float(self.log_box_line_count),
                '[' + datetime.now().strftime('%Y/%m/%d_%H:%M:%S') + '] '
                + f'<{message.status.name}> {message.message}\n'
            )
            self.log_box_line_count += 1

            # If the log status was completed, return
            if message.status is LogStatus.COMPLETED:
                return

        # Recursively call function for always checking the queue is empty or not
        if self.watcher_thread:
            self.after(100, self.insert_to_log_box)

    def _stop(self):
        """
        When user clicked "停止"
        Tell the thread to stop the observer
        """
        # If the watcher thread exists, stop the thread
        if self.watcher_thread:
            self.watcher_thread.stop_event()
            self.after(100, self.insert_to_log_box)
            self.watcher_thread = None
        else:
            # Show a message box, when watcher thread does not exist
            messagebox.showwarning(
                'エラー',
                '実行されていないため停止することができません\n実行を行ったうえで停止することができます'
            )

    def _export_log(self):
        """
        When user clicked "ログを出力"
        Pop up the filedialog for asking which directory to save the log file
        Save the log file when user select yes, otherwise do not save
        """
        dir_name = filedialog.Directory().show()
        if not dir_name:
            return

        filename = datetime.now().strftime('%Y%m%d_%H%M%S_LOG.txt')
        will_save = messagebox.askyesnocancel(
            '保存',
            f'{filename}で保存します\n続行しますか?'
        )
        if not will_save:
            return

        # Get all text in the log box
        log_text = self.log_box.get(1.0, 'end-1c')
        with open(file=f'{dir_name}/{filename}', mode='w', encoding='utf-8') as f:
            f.write(log_text)

    @classmethod
    def get_instance(cls, master=ROOT):
        """
        Returns a singleton instance of BookMakerApp.

        :param master: default parameter is tk.Tk()
        :return: Singleton BookMakerApp instance
        """
        if not hasattr(cls, '_instance'):
            cls._instance = cls(master)
        else:
            cls._instance.master = master
        return cls._instance


def main():
    global ROOT
    app = BookMakerApp(ROOT)
    app.mainloop()


if __name__ == '__main__':
    main()
