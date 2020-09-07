"""定数

定数を格納する

"""


# 監視するファイルタイプ
FILE_TYPES = [
    'pdf'
]

# メッセージ
INPUT_ERROR = '入力エラー'
SELECT_DIR_MESSAGE = '{0}ディレクトリを選択してください'
IS_NOT_DIR_MESSAGE = '{0}ディレクトリに入力された値はディレクトリではありません'
FILE_TYPE_IS_NOT_CHOSEN_MESSAGE = f'ファイルの種類が選択されていません\n{", ".join(FILE_TYPES)}の中から選択してください'
FILE_TYPE_IS_NOT_IN_THE_LIST_MESSAGE = f'ファイルの種類が特定できません\n{", ".join(FILE_TYPES)}の中から選択してください'
