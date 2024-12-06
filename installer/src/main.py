#  coding: utf-8
# ----------------------------------------------------------------------------------
# 2024/6/17 更新

# ----------------------------------------------------------------------------------


import sys
import asyncio
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from method.base.utils import Logger
from method.flow import Flow



# ------------------------------------------------------------------------------
# **********************************************************************************


class Main:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        self.flow = Flow(debugMode=debugMode)


# ----------------------------------------------------------------------------------


    async def run_flow(self, query):
        start_time = time.time()

        await self.flow.process(query=query)

        end_time = time.time()
        return end_time - start_time


# ----------------------------------------------------------------------------------
# **********************************************************************************


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.main_instance = Main()
        self.initUI()

    def initUI(self):
        # ウィジェットのレイアウト
        self.setWindowTitle('Google Map API Tool')
        self.setGeometry(100, 100, 250, 200)
        layout = QVBoxLayout()

        # 入力ラベルと入力フィールド
        self.label = QLabel('検索ワードを入力してください:')
        layout.addWidget(self.label)

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        # 実行ボタン
        self.run_button = QPushButton('実行')
        self.run_button.clicked.connect(self.on_run_clicked)
        layout.addWidget(self.run_button)

        # 終了ボタン
        self.close_button = QPushButton('閉じる')
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

        # レイアウトの設定
        self.setLayout(layout)

    def on_run_clicked(self):
        # ユーザー入力取得
        user_input = self.input_field.text()
        if not user_input.strip():
            QMessageBox.warning(self, '警告', '検索ワードを入力してください')
            return

        # 非同期処理を実行
        asyncio.run(self.run_main_flow(user_input))

    async def run_main_flow(self, user_input):
        try:
            # Mainクラスの非同期メソッドを呼び出す
            elapsed_time = await self.main_instance.run_flow(user_input)
            QMessageBox.information(self, '完了', f'処理が完了しました！\n処理時間: {elapsed_time:.2f}秒')
        except Exception as e:
            QMessageBox.critical(self, 'エラー', f'エラーが発生しました: {e}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = App()
    main_window.show()
    sys.exit(app.exec_())

