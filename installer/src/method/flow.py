# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, asyncio
from dotenv import load_dotenv
from datetime import datetime

# 自作モジュール
from .base.utils import Logger
from .base.spreadsheetWrite import SpreadsheetWrite
from .base.get_gm_df import GetGMPlaceDf
from .base.AiOrder import ChatGPTOrder
from .base.spreadsheetRead import GetDataGSSAPI

from .const_str import GssInfo

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
        self.jsonKeyName = GssInfo.JSON_KEY_NAME.value
        self.spreadsheetId = GssInfo.SHEET_ID.value
        self.worksheet_1 = GssInfo.WORKSHEET_1.value
        self.worksheet_2 = GssInfo.WORKSHEET_2.value


        # インスタンス
        self.gss_write = SpreadsheetWrite(debugMode=debugMode)
        self.gm_df = GetGMPlaceDf(api_key=self.api_key, debugMode=debugMode)
        self.chatGPT = ChatGPTOrder(debugMode=debugMode)
        self.fullCurrentDate = datetime.now().strftime('%y%m%d_%H%M%S')
        self.gss_read = GetDataGSSAPI(debugMode=debugMode)


####################################################################################
# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    async def process(self):
        # スプシから検索キーワードを取得
        read_df = self.gss_read.getDataFrameFromGss(jsonKeyName=self.jsonKeyName, spreadsheetId=self.spreadsheetId, workSheetName=self.worksheet_2)
        for i, read_row in read_df.iterrows():
            query = read_row['地名'] + ' ' + read_row['ジャンル']
            self.logger.debug(f"{i + 1}つ目の検索キーワード: {query}")

            df = await self.gm_df.process(query=query)
            for index, row in df.iterrows():
                address = row['formatted_address'].split('日本、')
                values = [row['name'], row['formatted_phone_number'], address[1], row['user_ratings_total']]
                self.logger.info(f"{index} 行目のデータ:\n{values}")

            # 行ごとのアプローチ
                self.gss_write._gss_none_cell_update(spreadsheetId=self.spreadsheetId, worksheet=self.worksheet_1, input_values=values)



# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    test_flow = Flow()
    asyncio.run(test_flow.process())
