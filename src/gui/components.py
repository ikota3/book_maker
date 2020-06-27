import os
from datetime import datetime
from tkinter import (
    E,
    W,
    EW,
    NSEW,
    Tk,
    Frame,
    Button,
    Entry,
    Text,
    Label,
    StringVar,
    filedialog,
    messagebox
)
from tkinter.ttk import Combobox


FILE_TYPES = 'pdf'


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
        self.log_box = {}

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
        log_box.grid(
            row=4, column=0, columnspan=3, sticky=NSEW
        )

        log_export_button.grid(
            row=3, column=1, columnspan=2, sticky=E, pady=(0, 7)
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

        if not self.file_type_value.get():
            messagebox.showerror(
                '入力エラー',
                'ファイルの種類が選択されていません\n' + ', '.join(FILE_TYPES) + 'の中から選択してください'
            )
            return

        # TODO insert all print content to log box
        # TODO colorize

    def _export_log(self):
        """
        When user clicked "ログを出力"
        Pop up the filedialog for asking which directory to save the log file
        """

        dir_name = filedialog.Directory().show()
        if not dir_name:
            return

        filename = datetime.now().strftime('%Y%m%d_%H%M%S_LOG.txt')
        willSave = messagebox.askyesnocancel(
            '保存',
            f'{filename}で保存します\n続行しますか?'
        )
        if not willSave:
            return

        log_text = self.log_box.get(1.0, 'end-1c')
        with open(file=f'{dir_name}/{filename}', mode='w', encoding='utf-8') as f:
            f.write(log_text)


def main():
    root = Tk()
    app = BookMakerApp(root)
    app.mainloop()


if __name__ == '__main__':
    main()
