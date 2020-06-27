import os
import asyncio
import threading
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
            row=2, column=0, columnspan=3, sticky=NSEW, pady=(10, 20)
        )

        log_label.grid(
            row=3, column=0, sticky=W, pady=(7, 0)
        )
        log_export_button.grid(
            row=3, column=1, columnspan=2, sticky=E, pady=(0, 7)
        )
        log_box.grid(
            row=4, column=0, columnspan=3, sticky=NSEW
        )
        scrollbar.grid(
            row=4, column=1, columnspan=2, sticky=(N, S, E), padx=(1, 1), pady=(1, 1)
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

        # Check input
        if not self.dir_to_watch_path.get():
            messagebox.showerror('入力エラー', '監視対象のディレクトリを選択してください')
            return

        if not os.path.isdir(self.dir_to_watch_path.get()):
            messagebox.showerror('入力エラー', 'ディレクトリではありません')
            return

        if not self.file_type_value.get() or not self.file_type_value.get() in FILE_TYPES:
            messagebox.showerror(
                '入力エラー',
                'ファイルの種類が選択されていません\n' + ', '.join(FILE_TYPES) + 'の中から選択してください'
            )
            return
        print('from components.py')
        print(hex(id(self.log_box)))

        # TODO Fix to call the process in the background
        # from src.watch import watch
        # self.after(
        #     100,
        #     watch(self.dir_to_watch_path.get(), self.dir_to_watch_path.get(), [self.file_type_value.get()])
        # )
        # async_loop = asyncio.get_event_loop()
        # def _asyncio_thread(async_loop):
        #     async_loop.run_until_complete(
        #         watch(self.dir_to_watch_path.get(), self.dir_to_watch_path.get(), [self.file_type_value.get()])
        #     )
        # threading.Thread(target=_asyncio_thread, args=(async_loop,)).start()

    def _export_log(self):
        """
        When user clicked "ログを出力"
        Pop up the filedialog for asking which directory to save the log file
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

        log_text = self.log_box.get(1.0, 'end-1c')
        with open(file=f'{dir_name}/{filename}', mode='w', encoding='utf-8') as f:
            f.write(log_text)

    def insert_to_log_box(self, text):
        """
        Insert text content to log box.
        :param text: string
        """
        if not text:
            return
        print(text)
        self.log_box.insert(float(self.log_box_line_count), f'{text}\n')
        self.log_box_line_count += 1

    @classmethod
    def get_instance(cls, master=ROOT):
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
