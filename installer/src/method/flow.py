# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, time, asyncio
import pandas as pd
from dotenv import load_dotenv

# 自作モジュール
from base.utils import Logger
from base.spreadsheetWrite import SpreadsheetWrite
from base.get_gm_df import GetGMPlaceDf

from const_str import GssInfo

load_dotenv()


# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ

class Flow:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # const, env
        self.api_key = os.getenv('GM_API_KEY')
        self.spreadsheetId = GssInfo.SHEET_ID.value
        self.worksheet_1 = GssInfo.WORKSHEET_1.value
        self.worksheet_2 = GssInfo.WORKSHEET_2.value



        # インスタンス
        self.gss_write = SpreadsheetWrite(debugMode=debugMode)
        self.gm_df = GetGMPlaceDf(api_key=self.api_key, debugMode=debugMode)


####################################################################################
# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    def process(self, query: str):
        df = self.gm_df.process(query=query)
        for index, row in df.iterrows():
            values = [row['name'], row['formatted_phone_number'], row['formatted_address'], row['user_ratings_total']]
            self.logger.info(f"{index} 行目のデータ:\n{values}")

        # 行ごとのアプローチ
            self.gss_write._gss_none_cell_update(spreadsheetId=self.spreadsheetId, worksheet=self.worksheet_1, input_values=values)








# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    query = '千歳烏山 ラーメン'
    test_flow = Flow()
    test_flow.process(query=query)