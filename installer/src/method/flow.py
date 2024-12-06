# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, time, asyncio, json
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# 自作モジュール
from .base.utils import Logger
from .base.spreadsheetWrite import SpreadsheetWrite
from .base.get_gm_df import GetGMPlaceDf
from .base.AiOrder import ChatGPTOrder
# from .base.popup import Popup

from .const_str import GssInfo, EndPopup, EndPoint

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
        self.chatGPT = ChatGPTOrder(debugMode=debugMode)
        self.fullCurrentDate = datetime.now().strftime('%y%m%d_%H%M%S')
        # self.popup = Popup(debugMode=debugMode)


####################################################################################
# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    async def process(self, query: str):
        df = await self.gm_df.process(query=query)
        for index, row in df.iterrows():
            values = [row['name'], row['formatted_phone_number'], row['formatted_address'], row['user_ratings_total']]
            self.logger.info(f"{index} 行目のデータ:\n{values}")

        # 行ごとのアプローチ
            self.gss_write._gss_none_cell_update(spreadsheetId=self.spreadsheetId, worksheet=self.worksheet_1, input_values=values)

        # 完成コメント
        # self.popup.popupCommentOnly(popupTitle=EndPopup.TITLE.value, comment=EndPopup.COMMENT.value)


        # # 厳選データをリストとして収集
        # filtered_data = []
        # for _, row in df.iterrows():
        #     if row['user_ratings_total'] > 10:  # レビュー数が10件以上
        #         filtered_data.append({
        #             '店舗名': row['name'],
        #             '電話番号': row['formatted_phone_number'],
        #             '住所': row['formatted_address'],
        #             'レビュー数': row['user_ratings_total']
        #         })

        # # JSON に変換
        # filtered_json = json.dumps(filtered_data, ensure_ascii=False, indent=2)
        # self.logger.debug(f'filtered_json: {filtered_json}')

        # prompt = ChatGptInfo.PROMPT.value

        # prompt_in_data = prompt + filtered_json

        # self.logger.debug(f'prompt_in_data: {prompt_in_data}')

        # stores_info = await self.chatGPT.resultOutput(
        #     prompt=prompt_in_data,
        #     fixedPrompt=None,
        #     model=ChatGptInfo.MODEL.value,
        #     endpointUrl=EndPoint.CHAT_GPT.value.format(ChatGptInfo.MODEL.value),
        #     apiKey=os.getenv('CHATGPT_APIKEY'),
        #     maxlen=1000,
        #     maxTokens=ChatGptInfo.MAX_TOKEN.value
        # )

        # self.logger.info(f'stores_info: {stores_info}')



        # if '該当なし' in stores_info:
        #     none_data = [f'{query} を調べましたが該当店舗はありませんでした。{self.fullCurrentDate}']
        #     self.logger.debug(f'none_data: {none_data}')
        #     self.gss_write._gss_none_cell_update(spreadsheetId=self.spreadsheetId, worksheet=self.worksheet_2, input_values=none_data)

        # else:
        #     for store_info in stores_info:
        #         input_values = [store_info.get['店舗名', ''], store_info.get['住所', ''], store_info.get['電話番号', ''], store_info.get['出店日', ''], store_info.get['Googleマップリンク', ''], ]
        #         self.gss_write._gss_none_cell_update(spreadsheetId=self.spreadsheetId, worksheet=self.worksheet_2, input_values=input_values)


# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    query = '千歳烏山 すし'
    test_flow = Flow()
    asyncio.run(test_flow.process(query=query))
