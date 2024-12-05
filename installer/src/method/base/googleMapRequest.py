# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/6/2更新

# ----------------------------------------------------------------------------------

from .base.B_googleMap import GoogleMapBase
from .base.utils import Logger


###############################################################
# Override

class GoogleMapRequest(GoogleMapBase):
    def __init__(self, debug_mode=False):

        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

    # リクエスト
    def _google_map_api_request(self, api_key, query):
        return super()._google_map_api_request(api_key, query)

    # レスポンスのjsonファイルの中身全てを確認
    def _response_result_checker(self, json_data):
        return super()._response_result_checker(json_data)

    # jsonファイルのcolumnごとの値を取得
    def _get_json_column_only_data(self, json_data, column):
        return super()._get_json_column_only_data(json_data, column)

    # jsonファイルの階層があるcolumnの値を取得
    def _get_json_column_hierarchy_data(self, json_data, column, column2, column3):
        return super()._get_json_column_hierarchy_data(json_data, column, column2, column3)


###############################################################
# 今回確認するcolumnデータ

    # 店名のデータ
    def shop_name_column_in_json(self, api_key, query):
        json_data =self. _google_map_api_request(api_key, query)
        column = 'name'
        return self._get_json_column_only_data(json_data, column)


    # 店の写真データ
    def shop_photo_column_in_json(self, json_data):
        column = 'photos'
        return self._get_json_column_only_data(json_data, column)


    # 市区町村のデータ
    def shop_name_column_in_json(self, json_data):
        column = 'name'
        return self._json_column(json_data, column)



    # 住所データ



    # 電話番号データ



    # 営業時間データ



    # 定休日データ



    # 公式サイトデータ



    # 口コミデータ



    # ジャンルデータ



    # 料金ランクデータ





###############################################################
