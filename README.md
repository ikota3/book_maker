# BOOK_MAKER

### Workflow
1. 監視対象のディレクトリを指定し、src/watch.py を起動
2. PDFを監視対象のディレクトリに配置
3. イベントを感知し、ファイルの中身からISBNを取得
4. 各APIから、ISBNを元に書籍情報を取得
5. ファイル名を修正し、ファイルを適切なディレクトリに移動

### Requirements
- Library
    - watchdog

- Install
    - `pip3 install -r requirement.txt`

### How to use
- `python3 src/watch.py dir_to_watch [*extensions]`
