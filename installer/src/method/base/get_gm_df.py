# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/6/4更新

# ----------------------------------------------------------------------------------

import time

# 自作モジュール
from .B_googleMap import GoogleMapBase
from .utils import Logger

###############################################################


class GetGMPlaceDf:
    def __init__(self, api_key, debugMode=True):
        self.api_key = api_key

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        self.gm = GoogleMapBase(api_key=self.api_key, debugMode=debugMode)


###############################################################
# ----------------------------------------------------------------------------------
# GMのPlace APIへのリクエストしてdetail_dataを取得

    def process(self, query):
        try:
            self.logger.info(f"******** get_gm_df_list 開始 ********")

            # gmAPIリクエスト
            json_data = self.gm._google_map_api_request(query=query)
            time.sleep(2)

            # plase_id_listを取得
            plase_id_list = self.gm._get_place_id(json_data=json_data)
            time.sleep(2)

            # 詳細データを取得
            details_data_list = self.gm._place_id_requests_in_list(place_id_list=plase_id_list)
            time.sleep(2)

            # 詳細データリストからresult部分を抽出してリストを作成
            results_data_list= self.gm._get_results_list(place_details_results_list=details_data_list)
            time.sleep(2)

            # 詳細データをDataFrameに変換
            key_df = self.gm._get_json_to_dataframe(json_data=results_data_list)
            time.sleep(2)

            self.logger.info(f"******** get_gm_df_list 終了 ********")

            return key_df

        except Exception as e:
            self.logger.error(f"get_gm_df_list 処理中にエラーが発生: {e}")
            raise


# ----------------------------------------------------------------------------------
