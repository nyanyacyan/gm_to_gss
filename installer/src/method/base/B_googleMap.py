# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/5/8更新

# ----------------------------------------------------------------------------------

import sys
import time
import requests
import json
import math
import pandas as pd
# from tkinter import messagebox
from dotenv import load_dotenv
import asyncio
import aiohttp
from typing import Optional
from datetime import datetime

# 自作モジュール
from ..const_str import EndPoint, SubDir, Extension
from .utils import Logger
from .path import BaseToPath

load_dotenv()

###############################################################
# googleMapApiを使ってrequest

class GoogleMapBase:
    def __init__(self, api_key, debugMode=True):
        self.api_key = api_key

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.path = BaseToPath(debugMode=debugMode)
        self.fullCurrentDate = datetime.now().strftime('%y%m%d_%H%M%S')




###############################################################
# ----------------------------------------------------------------------------------
# Google mapAPIへのrequest(async)

    async def fetch_data(self, endpoint_url, params, timeout):
        try:
            self.logger.info(f"******** fetch_data start ********")

            # sessionを使うことで同じ通り道をそのまま使える
            # sessionをCookie、認証情報をそのまま使える
            # sessionを同じパラメータをそのまま使える
            # sessionを使う場合には使ったあとに閉じる必要がある→withを使うことで閉じてる
            async with aiohttp.ClientSession() as session:

                # sessionにて返ってきたレスポンスをエンドポイントに取りに行ってる
                # withにすることで干渉を受けずに独立して実施される
                # ssl=False SSL/TLS証明書の検証を無効
                async with session.get(endpoint_url, params=params, ssl=False, timeout=timeout) as response:
                    if response.status == 200:
                        json_data = await response.json()  # ここでawaitを使用して非同期操作を実行
                        self.logger.info(f"リクエスト成功: {json_data}")

                        self.logger.info(f"******** fetch_data end ********")

                        return json_data

                    elif response.status == 500:
                        self.logger.error("google_map_api_request サーバーエラー")
                        raise Exception("サーバーエラー")

                    else:
                        error_text = await response.text()  # ここでawaitを使用して非同期操作を実行
                        self.logger.error(f"google_map_api_request リクエストした際にエラーが発生: {response.status} - {error_text}")
                        raise Exception("リクエストした際にエラーが発生")

        except aiohttp.ClientError as e:
            self.logger.error(f"HTTPリクエスト中にクライアントエラーが発生しました: {str(e)}")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {e}")
            sys.exit(1)

        except asyncio.TimeoutError:
            self.logger.error("HTTPリクエストがタイムアウトしました")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# Google mapAPIへのrequest

    async def _google_map_api_request(self, query):
        try:
            self.logger.info(f"******** google_map_api_request 開始 ********")

            self.logger.debug(f"検索ワード: {query}")

            endpoint_url = EndPoint.GOOGLE_MAP.value

            params = {
                'query' : query,  # 検索ワード
                'key' : self.api_key
            }

            # response = requests.get(endpoint_url, params=params, timeout=10)
            response = await self.fetch_data(endpoint_url=endpoint_url, params=params, timeout=10)
            # self.logger.info(f"response: {response[:20]}")
            return response


        except requests.exceptions.Timeout:
            self.logger.error(f"google_map_api_request リクエストでのタイムアウトエラー")
            sys.exit(1)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"google_map_api_request リクエストエラーが発生: {e}")
            sys.exit(1)

        except Exception as e:
            self.logger.error(f"google_map_api_request 処理中にエラーが発生: {e}")
            sys.exit(1)

        finally:
            self.logger.info(f"******** google_map_api_request 終了 ********")

# ----------------------------------------------------------------------------------
# jsonファイルの全ての中身を確認

    def _response_result_checker(self, json_data):
        try:
            self.logger.info(f"******** _response_result_checker 開始 ********")

            self.logger.critical(f'json_data:{json_data}')

            if json_data:
                self.logger.debug(json.dumps(json_data, indent=2, ensure_ascii=False))

            else:
                raise Exception("json_data データがなし")

            self.logger.info(f"******** _response_result_checker 終了 ********")


        except Exception as e:
            self.logger.error(f"_response_result_checker 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# 取得したjsonデータを再リクエストしなくて済むようにデータに置き換える


    def _get_json_to_dataframe(self, json_data):

        self.logger.info(f"******** _get_json_to_dataframe 開始 ********")

        # json_dataの中身を確認
        self._response_result_checker(json_data=json_data)

        # json_dataの「results」部分を抜き出す
        # places = json_data.get('results', [])

        # jsonデータをDataFrameに変換
        df = pd.json_normalize(json_data)

        df = df.fillna('')
        self.logger.debug(df.head())

        # DataFrameをデバッグ用にCSV出力
        debug_csv_path = self.path.getResultSubDirFilePath(subDirName=SubDir.DEBUG_CSV.value, fileName=self.fullCurrentDate, extension=Extension.csv.value)
        df.to_csv(debug_csv_path)

        return df

        # except Exception as e:
        #     self.logger.error(f"_get_json_to_dataframe 処理中にエラーが発生: {e}")
        #     sys.exit(1)


# ----------------------------------------------------------------------------------
# DataFrameから複数のcolumnの値データを取得する
#! columnsで必要なcolumnを順番に指定する
#! →columns = ["name", "geometry.location.lat", "geometry.location.lng", "rating"]

    def get_column_data_in_df(self, df, columns):
        try:
            self.logger.info(f"******** get_column_data_in_df 開始 ********")

            store_data_list = []

            if df:
                # iterrowsは一つずつ取り出す→Indexとデータをタプルで返す
                for index, row in df.iterrows():
                    # rowのデータからcolumnのデータをリストに入れ込んでいく
                    store_data = {column: row[column] for column in columns}

                    self.logger.info(f"store_data: {index} {store_data}")

                    store_data_list.append(store_data)

            else:
                self.logger.error(f"dfがNoneになっている")

            self.logger.debug(f"store_data_list: \n{store_data_list}")

            self.logger.info(f"******** get_column_data_in_df 終了 ********")

            return store_data_list

        except Exception as e:
            self.logger.error(f"get_column_data_in_df 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# jsonファイルの特定のcolumnの内容を確認

    def _get_json_column_only_data(self, json_data, column):
        try:
            self.logger.info(f"******** _json_column 開始 ********")

            self.logger.debug(f"column:{column}")

            # jsonファイルが存在確認
            if not json_data:
                raise ValueError("json_data がNoneです")

            # jsonファイルに指定したcolumnがあるのか確認
            if column in json_data:
                raise KeyError(f"column '{column}' が JSONデータに存在しません")

            # jsonファイルの中にある'results'の中からデータを抜く
            places = json_data.get('results', [])

            for place in places:

                # columnごとの値
                column_value = place.get(column)

            self.logger.debug(f"column_value: {column_value}")

            self.logger.info(f"******** _json_column 終了 ********")

            return column_value


        except KeyError as ke:
            self.logger.error(f"指定されたカラムにエラーがあります: {ke}")
            sys.exit(1)


        except ValueError as ve:
            self.logger.error(f"指定したcolumnのデータが指定したJSONファイルにない: {ve}")
            sys.exit(1)


        except Exception as e:
            self.logger.error(f"response_result_checker 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# jsonファイルの特定の階層がある部分の値を取得

    def _get_json_column_hierarchy_data(self, json_data, column, column2, column3):
        try:
            self.logger.info(f"******** response_result_checker 開始 ********")

            self.logger.debug(f"columns: {column}, {column2}, {column3}")

            if not json_data:
                raise ValueError("json_data がNoneです")


            # jsonファイルの中にある'results'の中からデータを抜く
            places = json_data.get('results', [])

            for place in places:
                if column in place and column2 in place[column] and column3 in place[column][column2]:

                # columnごとの値
                    column_value = place[column][column2][column3]

                else:
                    raise KeyError(f"指定したcolumn '{column}/{column2}/{column3}'が jsonデータに存在しない")

            self.logger.debug(f"column_value: {column_value}")

            self.logger.info(f"******** response_result_checker 終了 ********")

            return column_value


        except KeyError as ke:
            self.logger.error(f"指定されたカラムにエラーがあります: {ke}")
            sys.exit(1)


        except ValueError as ve:
            self.logger.error(f"指定したcolumnのデータが指定したJSONファイルにない: {ve}")
            sys.exit(1)


        except Exception as e:
            self.logger.error(f"response_result_checker 処理中にエラーが発生: {e}")
            sys.exit(1)

# ----------------------------------------------------------------------------------
# place_idを取得

    async def _get_place_id(self, json_data):
        try:
            self.logger.info(f"******** _get_place_id 開始 ********")

            if not json_data:
                raise ValueError("json_data がNoneです")

            # jsonファイルの中にある'results'の中からデータを抜く
            places = json_data.get('results', [])

            self.logger.debug(f"places:\n{places[:100]}")

            place_id_list = []

            for place in places:
                self.logger.debug(f"place:\n{place}")

                # columnごとの値
                plase_id_value = place.get('place_id')
                self.logger.debug(f"column_value: {plase_id_value}")

                place_id_list.append(plase_id_value)

            self.logger.debug(f"place_id_list: {place_id_list}")


            self.logger.info(f"******** _get_place_id 終了 ********")

            return place_id_list


        except KeyError as ke:
            self.logger.error(f"指定されたカラムにエラーがあります: {ke}")
            sys.exit(1)


        except ValueError as ve:
            self.logger.error(f"指定したcolumnのデータが指定したJSONファイルにない: {ve}")
            sys.exit(1)


        except Exception as e:
            self.logger.error(f"response_result_checker 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# place_idのリストそれぞれでリクエストを行い詳細データをリスト化する

    async def _place_id_requests_in_list(self, place_id_list):
        try:
            self.logger.info(f"******** get_results_in_place_id_list 開始 ********")

            self.logger.debug(f"place_id_list: {place_id_list[:20]}")

            place_details_results_list = []

            # 詳細データをリスト化する
            for place_id in place_id_list:
                # place_idでリクエスト
                place_details = self._place_id_request(place_id=place_id)
                self.logger.debug(f"place_details: \n{place_details}")
                place_details_results_list.append(place_details)

            self.logger.debug(f"place_details_results_list: \n{place_details_results_list[:100]}")

            self.logger.info(f"******** get_results_in_place_id_list 終了 ********")

            return place_details_results_list


        except Exception as e:
            self.logger.error(f"get_results_in_place_id_list 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# plase_idを使ってrequestをして詳細情報を取得

    def _place_id_request(self, place_id):
        try:
            self.logger.info(f"******** _plase_id_request 開始 ********")
            endpoint_url = EndPoint.GOOGLE_MAP_PLACE.value

            params = {
                'place_id' : place_id,  # IDによる詳細情報を取得
                'key' : self.api_key,
                'language' : 'ja'
            }

            response = requests.get(endpoint_url, params=params, timeout=10)

            # ステータスコードが成功ならjsonを返す
            if response.status_code == 200:
                json_data = response.json()

                self.logger.info(f"******** _plase_id_request 終了 ********")

                return json_data


            elif response.status_code == 500:
                self.logger.error(f"_plase_id_request サーバーエラー")

            else:
                self.logger.error(f"_plase_id_request リクエストした際にエラーが発生: {response.status_code} - {response.text}")


            self.logger.info(f"******** _plase_id_request 終了 ********")

        except requests.exceptions.Timeout:
            self.logger.error(f"_plase_id_request リクエストでのタイムアウトエラー")
            sys.exit(1)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"_plase_id_request リクエストエラーが発生: {e}")
            sys.exit(1)

        except Exception as e:
            self.logger.error(f"_plase_id_request 処理中にエラーが発生: {e}")
            sys.exit(1)

        finally:
            self.logger.info(f"******** _plase_id_request 終了 ********")

        return None


# ----------------------------------------------------------------------------------
# place_details_dataからresults部分を抽出してリスト化する

    async def _get_results_list(self, place_details_results_list):
        try:
            self.logger.info(f"******** _get_results_list 開始 ********")

            self.logger.debug(f"place_details_results_list: {place_details_results_list[:20]}")

            results_data_list = []

            # results部分を抽出してリストに追加
            for place_details in place_details_results_list:
                if 'result' in place_details:
                    self.logger.debug(place_details['result'])
                    results_data_list.append(place_details['result'])

            self.logger.debug(f"results_data: {results_data_list[:20]}")

            self.logger.info(f"******** _get_results_list 終了 ********")

            return results_data_list


        except Exception as e:
            self.logger.error(f"_get_results_list 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# DataFrameにする

    def _to_df(self, list_data, new_column):
        try:
            self.logger.info(f"******** _to_df 開始 ********")

            self.logger.debug(f"list_data: {list_data}")

            series_df = pd.DataFrame(list_data, columns=[new_column])

            self.logger.debug(series_df.head())

            self.logger.info(f"******** _to_df 終了 ********")

            return series_df

        except Exception as e:
            self.logger.error(f"_to_df 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# 既存のDataFrameに結合させる

    def _df_marge(self, key_df, add_df):
        try:
            self.logger.info(f"******** _df_marge 開始 ********")

            self.logger.debug(f"key_df: \n{key_df.head(3)}")
            self.logger.debug(f"add_df: \n{add_df.head(3)}")

            new_df = pd.merge(key_df, add_df, left_index=True, right_index=True, how='left')

            self.logger.debug(f"new_df: \n{new_df.head(3)}")

            self.logger.info(f"******** _df_marge 終了 ********")

            return new_df

        except Exception as e:
            self.logger.error(f"_df_marge 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# DataFrameからcolumnデータを抽出

    def _get_column_data(self, key_df, column):
        try:
            self.logger.info(f"******** _get_column_data 開始 ********")

            self.logger.debug(f"key_df: \n{key_df.head(3)}")

            series_data = key_df[column]

            # self.logger.debug(f"series_data: \n{series_data[2]}")

            self.logger.info(f"******** _get_column_data 終了 ********")

            return series_data

        except Exception as e:
            self.logger.error(f"_get_column_data 処理中にエラーが発生: {e}")
            sys.exit(1)



# ----------------------------------------------------------------------------------
# 住所を日本語に変換するためにGeocoding APIを通す

    def _address_to_japanese(self, address):
        try:
            self.logger.info(f"******** address_to_japanese 開始 ********")

            self.logger.debug(f"list_data: {address}")

            endpoint_url = const.geocoding_endpoint_url

            self.logger.debug(f"endpoint_url: {endpoint_url}")

            params ={
                'address' : address,
                'key' : self.api_key,
                'language' : 'ja'
            }

            # Geocodingへリクエスト
            response = requests.get(endpoint_url, params=params)

            # 送信のステータスcodeがOKだったら
            if response.status_code == 200:
                response_json = response.json()
                self.logger.info("リクエスト成功")

                self.logger.info(response_json)

                # ステータスがOKだったら
                if response_json['status'] == 'OK':
                    self.logger.info("ステータスOK")

                    # jsonデータのresultsの中のformatted_addressを取得
                    formatted_address = response_json['results'][0]['formatted_address']
                    self.logger.debug(f"formatted_address: {formatted_address}")

                    # 余計な文字を除去
                    clean_address = self._str_Remove(value=formatted_address, str_remove="日本、")

                    self.logger.info(f"******** address_to_japanese 終了 ********")

                    return clean_address

                else:
                    raise Exception(f"ステータスがOKになってない {response_json['status']}")

            else:
                raise Exception(f"リクエスト中にエラーが発生 {response.status_code}")


        except Exception as e:
            self.logger.error(f"address_to_japanese 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# 余計な文字が入るためクリーニング

    def _str_Remove(self, value, str_remove):
        try:
            self.logger.info(f"******** _str_Remove 開始 ********")

            self.logger.debug(f"str_remove: {str_remove}")

            if str_remove in value:
                self.logger.info(f"{value} に {str_remove} を発見")

                # 対象の文字を除去
                remove_value = value.replace(str_remove, "")
                self.logger.debug(f"remove_value: {remove_value}")
                return remove_value

            else:
                self.logger.error(f"{value} には {str_remove} はありません。")

            self.logger.info(f"******** _str_Remove 終了 ********")

            return value

        except Exception as e:
            self.logger.error(f"_str_Remove 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# 各リストに処理を当て込めていく

    def add_process_value_in_list(self, list_data, add_func):
        try:
            self.logger.info(f"******** add_process_value_in_list 開始 ********")

            self.logger.debug(f"list_data: \n{list_data}")

            original_data_list = []

            # 値に処理を加えてリストにまとめる
            for data in list_data:
                # もしデータがない場合には追記する
                if data is None or (isinstance(data, float) and math.isnan(data)):
                    self.logger.info(f"dataがNone")

                    # TODO Googleマップに情報がなかったときにいれる文言
                    original_data_list.append("")

                else:
                    original_data = add_func(data)
                    self.logger.debug(f"original_data: {original_data}")

                    # もしリストのデータだったら結合させてリストに追加
                    if isinstance(original_data, list):
                        original_data_list.append("\n".join(original_data))
                    else:
                        original_data_list.append(original_data)

            self.logger.debug(f"original_data_list: {original_data_list}")

            self.logger.info(f"******** add_process_value_in_list 終了 ********")

            return original_data_list

        except Exception as e:
            self.logger.error(f"add_process_value_in_list 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# # 各リストに処理を当て込めていく

    def review_add_process_value_in_list(self, list_data, add_func):
        try:
            self.logger.info(f"******** review_add_process_value_in_list 開始 ********")

            self.logger.debug(f"list_data: \n{list_data}")

            original_data_list = []

            # 値に処理を加えてリストにまとめる
            for data in list_data:
                # もしデータがない場合には追記する
                if data is None or (isinstance(data, float) and math.isnan(data)):
                    self.logger.info(f"dataがNone")

                else:
                    original_data = add_func(data)
                    self.logger.debug(f"original_data: {original_data}")

                    # もしリストのデータだったら結合させてリストに追加
                    if isinstance(original_data, list):
                        original_data_list.append("\n".join(original_data))
                    else:
                        original_data_list.append(original_data)

            self.logger.debug(f"original_data_list: {original_data_list}")

            self.logger.info(f"******** review_add_process_value_in_list 終了 ********")

            return original_data_list

        except Exception as e:
            self.logger.error(f"review_add_process_value_in_list 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# # 営業時間を抽出

    def get_business_hour(self, list_data):
        try:
            self.logger.info(f"******** get_business_hour 開始 ********")
            self.logger.info(f"list_data: {list_data}")

            # APIデータに基づいて曜日を定義
            days_of_week = ["日曜日", "月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日"]

            business_hours_lst = []

            for day_data in list_data:
                self.logger.debug(f"day_data:\n{day_data}")

                if not isinstance(day_data, dict):
                    self.logger.error(f"無効なデータ型: {type(day_data)}")
                    continue


                # 曜日データを用意してそのデータに取得したデータを割り当てる
                day = days_of_week[day_data['open']['day']]

                # 数値データを取得
                # open_time = day_data['open']['time']
                # close_time: Optional[str] = day_data['close']['time']
                open_time = day_data.get('open', None)
                close_time = day_data.get('close', None)


                self.logger.debug(f"open_time: {open_time}, close_time: {close_time}")
                self.logger.debug(f"open_time: {open_time}, close_time: {close_time}")

                # 時間をサイトに表記する文字列に変換
                format_open_time = self._format_time(open_time[time])
                format_close_time = self._format_time(close_time[time])


                # 曜日ごとの時間を示す
                format_business_hour = f"{day} : {format_open_time} 〜 {format_close_time}<br>"

                self.logger.info(f"format_business_hour: {format_business_hour}")

                business_hours_lst.append(format_business_hour)

            self.logger.info(f"******** get_business_hour 終了 ********")

            return business_hours_lst

        except Exception as e:
            self.logger.error(f"get_business_hour 処理中にエラーが発生: {e}")
            sys.exit(1)



# ----------------------------------------------------------------------------------
# 営業時間データを修正する

    def get_business_hours(self, list_data):
        try:
            self.logger.info(f"******** get_business_hours start ********")
            self.logger.debug(f"list_data_type: {type(list_data)}")
            self.logger.debug(f"list_data: {list_data}")

            if list_data:

                # リストの中の値が「定休日」になってるものを除去
                close_day_remove_list = [day for day in list_data if '定休日' not in day]

                # 改行で結合して表記したいデータに変換
                business_hours = '<br>'.join(close_day_remove_list)

                self.logger.debug(f"business_hours: {business_hours}")

                self.logger.info(f"******** get_business_hours end ********")

                return business_hours


        except Exception as e:
            self.logger.error(f"get_business_hour 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# 0から始まる時間から頭の０を消去する

    def _format_time(self, time_str):
        try:
            self.logger.info(f"******** _format_time 開始 ********")

            self.logger.info(f"time_str: {time_str}")

            if time_str:
                formatted_time = f"{time_str[:2]}時{time_str[2:]}分"

                # もし頭の文字が「0」だったら
                if formatted_time.startswith('0'):
                    # ２つ目の文字からにすることで「０」を除去
                    formatted_time = formatted_time[1:]

            else:
                raise ValueError("time_strが空です。")

            self.logger.info(f"******** _format_time 終了 ********")

            return formatted_time

        except ValueError as ve:
            self.logger.error(f"time_strが None です{ve}")
            messagebox.showerror("エラー", f"time_strが None です: {e}")
            sys.exit(1)

        except Exception as e:
            self.logger.error(f"_format_time 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# 定休日を抽出

    def get_close_days(self, list_data):
        try:
            self.logger.info(f"******** get_close_day 開始 ********")

            if list_data:
                self.logger.debug(f"list_data: {list_data}")

                # APIデータに基づいて曜日を定義
                days_of_week = ["日曜日", "月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日"]

            for day_data in list_data:
                self.logger.debug(f"day_data:\n{day_data}")

                if not isinstance(day_data, dict):
                    self.logger.error(f"無効なデータ型: {type(day_data)}")
                    continue

                # setにてやっている曜日の数値を取得
                open_day = {day_data['open']['day'] for day_data in list_data}

                # [{'open': {'day': 0, 'time': '0000'}}]だった場合には定休日はなし
                if any(day_data['open']['time'] == '0000' and 'close' not in day_data for day_data in list_data):
                    return 'なし'

                # set 関数にて７個までの長さを集合を作成（0, 1, 2, 3, 4, 5, 6）
                all_days = set(range(7))
                self.logger.debug(f"all_days:\n{all_days}")

                # すべての集合から被ってるオープンしてる曜日の数値を除去する
                close_days_list = all_days - open_day
                self.logger.debug(f"close_days_list:{close_days_list}")

                if not close_days_list:
                    return "なし"

                # 曜日を文字列に置き換える
                # セットのため、一つ一つの数値を当て込んでその曜日を取得してリストにする
                close_days = [days_of_week[day] for day in close_days_list]
                self.logger.debug(f"close_day_str: {close_days}")


                # もし２つ以上の定休日があった場合、結合する
                if len(close_days) > 1:
                    close_days = ', '.join(close_days)
                    self.logger.debug(f"close_days: {close_days}")

                self.logger.info(f"******** get_close_day 開始 ********")

                return close_days

            else:
                raise ValueError("list_data が None")


        except ValueError as ve:
            self.logger.error(f"list_data が None: {ve}")
            sys.exit(1)

        except Exception as e:
            self.logger.error(f"get_close_day 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# 定休日を抽出

    def get_close_day(self, list_data):
        try:
            self.logger.info(f"******** get_close_day start ********")

            self.logger.debug(f"list_data: {list_data}")

            if list_data:
                close_days = [day for day in list_data if '定休日' in day]

                self.logger.warning(f"close_days: {close_days}")

                if not close_days:
                    self.logger.debug("定休日なし")
                    return 'なし'

                # keyと値になってるものを':'の部分で分割して1つ目のデータを抽出してリストにする
                close_days_keys = [day.split(':')[0].strip() for day in close_days]

                # リストを結合
                close_days_str = ', '.join(close_days_keys)

                self.logger.info(f"close_days_str: {close_days_str}")

                self.logger.info(f"******** get_close_day end ********")
                return close_days_str

            else:
                return 'なし'


        except Exception as e:
            self.logger.error(f"get_close_day 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# レビューの抽出

    def get_reviews(self, list_data):
        try:
            self.logger.info(f"******** get_reviews 開始 ********")

            # if list_data:
            self.logger.debug(f"list_dataの型は: \n{type(list_data)}")

            self.logger.debug(f"list_data: \n{list_data}")

            # list_data.to_csv('installer/result_output/list_data.csv')

            if isinstance(list_data, pd.Series):
                self.logger.debug(f"list_dataはSeriesになってる。")

                list_data = list_data.apply(lambda x: [''] if pd.isna(x) else x).tolist()
                # list_data = [item for sublist in list_data for item in sublist]

            # rank 順にソート
            sorted_reviews = sorted(list_data, key=lambda x: x['rating'], reverse=True)
            self.logger.debug(f"sorted_reviews: \n{sorted_reviews}")

            # 必要な情報を抜き取る
            review_dicts = [
                {
                    'rank': review['rating'],
                    'name': review['author_name'],
                    'text': review['text']
                } for review in sorted_reviews
            ]

            self.logger.debug(f"review_dicts: \n{review_dicts}")

            self.logger.info(f"******** get_reviews 終了 ********")

            return review_dicts

                # else:
                #     raise ValueError("list_data が None")


        except ValueError as ve:
            self.logger.error(f"list_data が None: {ve}")
            raise

        except Exception as e:
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {e}")
            sys.exit(1)

# ----------------------------------------------------------------------------------
# 各リストに処理を当て込めていく

    def add_dict_data(self, list_data, add_func):
        try:
            self.logger.info(f"******** add_process_value_in_list 開始 ********")

            self.logger.debug(f"list_data: \n{list_data}")

            original_data_list = []

            # 値に処理を加えてリストにまとめる
            for data in list_data:
                # もしデータがない場合には追記する
                if data is None or (isinstance(data, float) and math.isnan(data)):
                    self.logger.debug(f"dataがNone")

                    # TODO Googleマップに情報がなかったときにいれる文言
                    original_data_list.append("")

                else:
                    original_data = add_func(data)
                    self.logger.debug(f"original_data: {original_data}")

                    # もしリストのデータだったら結合させてリストに追加
                    if isinstance(original_data, list):
                        original_data_list.append(original_data)
                    else:
                        self.logger.error(f"データが違う可能性が高い。")

            self.logger.debug(f"original_data_list: {original_data_list}")

            self.logger.info(f"******** add_process_value_in_list 終了 ********")

            return original_data_list

        except Exception as e:
            self.logger.error(f"add_process_value_in_list 処理中にエラーが発生: {e}")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# jsonファイルからデータを取得

    def _get_json_data(self, select_series, none_res_data):
        try:
            self.logger.info(f"******** get_json_data 終了 ********")

            self.logger.debug(select_series.head(3))

            if isinstance(select_series, pd.Series):

                json_data_list = []
                for data in select_series:
                    if pd.isna(data):

                        # データがない場合のリンク
                        none_res = none_res_data

                        # noneのときにいれるデータを追加する
                        json_data_list.append(none_res)

                    else:
                        # json形式から辞書形式へ変換
                        # ダブルコーテへ変換する（シングルコーテはjson.loadsに対応してないため）
                        json_to_data = json.loads(data.replace("'", "\""))
                        json_data_list.append(json_to_data)

            self.logger.debug(f"json_data_list: \n{json_data_list}")

            self.logger.info(f"******** get_json_data 終了 ********")

            return json_data_list

        except json.JSONDecodeError as json_err:
            self.logger.error(f"JSONDecodeError 処理中にエラーが発生: {json_err}")
            raise

        except Exception as e:
            self.logger.error(f"get_json_data 処理中にエラーが発生: {e}")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {e}")
            sys.exit(1)



# ----------------------------------------------------------------------------------

# 辞書データから抽出してリストにする
# addressからデータを抜く基本のメソッド

    def _get_address_data(self, cell_data, address_type):
        try:
            self.logger.info(f"******** _get_address_data start ********")

            self.logger.debug(f"cell_data: {cell_data}, address_type: {address_type}")


            for address_dict_data in cell_data:
                self.logger.debug(f"address_dict_data:\n{address_dict_data}")

                if not isinstance(address_dict_data, dict):
                    self.logger.error(f"{address_dict_data} が期待してるデータではない")
                    raise TypeError(f"辞書データではない: {type(address_dict_data)}")

                if 'types' in address_dict_data and address_type in address_dict_data['types']:
                    address_data = address_dict_data['long_name']

                    self.logger.info(f"address_data: {address_data}")

                    self.logger.info(f"********  _get_address_data end ********")

                    return address_data


        except ValueError as ve:
            self.logger.error(f"_get_address_data 期待してる値ではない: {ve}")
            messagebox.showerror("エラー", f"期待してる値ではない: {e}")
            sys.exit(1)

        except TypeError as te:
            self.logger.error(f"_get_address_data 期待してるデータ型ではない: {te}")
            messagebox.showerror("エラー", f"期待してるデータ型ではない: {e}")
            sys.exit(1)

        except Exception as e:
            self.logger.error(f"_get_address_data 処理中にエラーが発生: {e}")
            messagebox.showerror("エラー", f"_get_address_data 処理中にエラーが発生しました: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
#  都道府県を追加

    def _get_prefectures(self, cell_data):
        try:
            self.logger.info(f"******** _get_prefectures start ********")

            prefectures_name = self._get_address_data(cell_data=cell_data, address_type='administrative_area_level_1')

            self.logger.info(f"prefectures_name: {prefectures_name}")

            self.logger.info(f"********  _get_prefectures end ********")

            return prefectures_name

        except Exception as e:
            self.logger.error(f"_get_prefectures 処理中にエラーが発生: {e}")
            messagebox.showerror("エラー", f"_get_prefectures 処理中にエラーが発生: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
#  市区町村を追加

    def _get_locality(self, cell_data):
        try:
            self.logger.info(f"******** _get_locality start ********")

            locality_name = self._get_address_data(cell_data=cell_data, address_type='locality')

            self.logger.info(f"locality_name: {locality_name}")

            self.logger.info(f"********  _get_locality end ********")

            return locality_name

        except Exception as e:
            self.logger.error(f"_get_locality 処理中にエラーが発生: {e}")
            messagebox.showerror("エラー", f"_get_locality 処理中にエラーが発生しました: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
#  町名を追加

    def _get_sublocality(self, cell_data):
        try:
            self.logger.info(f"******** _get_sublocality start ********")

            sublocality_name = self._get_address_data(cell_data=cell_data, address_type='sublocality_level_2')

            self.logger.info(f"sublocality_name: {sublocality_name}")

            self.logger.info(f"********  _get_sublocality end ********")

            return sublocality_name

        except Exception as e:
            self.logger.error(f"_get_sublocality 処理中にエラーが発生: {e}")
            messagebox.showerror("エラー", f"_get_sublocality 処理中にエラーが発生しました: {e}")
            sys.exit(1)



# ----------------------------------------------------------------------------------
#   写真のリンク先

    def _get_photo_link(self, cell_data):
        try:
            self.logger.info(f"******** _get_photo_link start ********")

            self.logger.debug(f"cell_data: {cell_data}")

            # 空の場合（NaN）の場合
            if cell_data is None or (isinstance(cell_data, float) and math.isnan(cell_data)):
                self.logger.debug(f"{cell_data} が None")
                return "GoogleMapには写真の掲載なし"

            # 写真データの最初の画像を使用
            if isinstance(cell_data, list) and len(cell_data) > 0:
                first_photo = cell_data[0]

                # 最初のリンクを使用
                if 'html_attributions' in first_photo and isinstance(first_photo['html_attributions'], list) and len(first_photo['html_attributions']) > 0:
                    photo_link = first_photo['html_attributions'][0]

                    self.logger.info(f"photo_link: {photo_link}")

                    self.logger.info(f"********  _get_photo_link end ********")

                    return photo_link

            self.logger.debug(f"適切な写真が見つかりませんでした。")

            self.logger.info(f"********  _get_photo_link end ********")

            return"GoogleMapには写真の掲載なし"


        except Exception as e:
            self.logger.error(f"_get_photo_link 処理中にエラーが発生: {e}")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------




# ----------------------------------------------------------------------------------
# photo_referenceを取得

    def _get_photo_reference(self, cell_data):
        try:
            self.logger.info(f"******** _get_photo_reference start ********")

            self.logger.debug(f"cell_data: {cell_data}")

            # 空の場合（NaN）の場合
            if cell_data is None or (isinstance(cell_data, float) and math.isnan(cell_data)):
                self.logger.debug(f"{cell_data} が None")
                return "GoogleMapには写真の掲載なし"

            # 写真データの最初の画像を使用
            if isinstance(cell_data, list) and len(cell_data) > 0:
                first_photo = cell_data[0]

                # 最初のリンクを使用
                if 'photo_reference' in first_photo and isinstance(first_photo['photo_reference'], str) and len(first_photo['photo_reference']) > 0:
                    photo_reference = first_photo['photo_reference']

                    self.logger.info(f"photo_reference: {photo_reference}")

                    self.logger.info(f"********  _get_photo_reference end ********")

                    return photo_reference

            self.logger.debug(f"適切な写真が見つかりませんでした。")

            self.logger.info(f"********  _get_photo_reference end ********")

            return"GoogleMapには写真の掲載なし"


        except Exception as e:
            self.logger.error(f"_get_photo_reference 処理中にエラーが発生: {e}")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# Google mapAPIへのrequest

    def generate_photo_url(self, cell_data, maxwidth=600):
        try:
            self.logger.info(f"******** _google_places_photo_api_request 開始 ********")

            self.logger.debug(f"cell_data: {cell_data}")

            # cell_dataに「適切な写真が見つかりませんでした。」が含まれている場合、Noneを返す
            if isinstance(cell_data, str) and "適切な写真が見つかりませんでした" in cell_data:
                self.logger.warning("適切な写真が見つかりませんでした。")
                return None


            photo_reference = self._get_photo_reference(cell_data=cell_data)

            endpoint_url = const.photo_endpoint_url

            params = {
                'photo_reference' : photo_reference,  # 検索ワード
                'key' : self.api_key,
                'maxwidth' : maxwidth
            }

            url = f"{endpoint_url}?photoreference={params['photo_reference']}&key={params['key']}&maxwidth={params['maxwidth']}"

            self.logger.warning(f"url: {url}")

            return url


        except requests.exceptions.Timeout:
            self.logger.error(f"_google_places_photo_api_request リクエストでのタイムアウトエラー")
            messagebox.showerror("エラー", f"リクエストでのタイムアウトエラー: {e}")
            sys.exit(1)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"_google_places_photo_api_request リクエストエラーが発生: {e}")
            messagebox.showerror("エラー", f"リクエストエラーが発生: {e}")
            sys.exit(1)

        except Exception as e:
            self.logger.error(f"_google_places_photo_api_request 処理中にエラーが発生: {e}")
            messagebox.showerror("エラー", f"_google_places_photo_api_request 処理中にエラーが発生しました: {e}")
            sys.exit(1)

        finally:
            self.logger.info(f"******** _google_places_photo_api_request 終了 ********")


# ----------------------------------------------------------------------------------
#  緯度と経度の中間を出す

    def _get_navi_position(self, df):
        try:
            self.logger.info(f"******** _get_navi_position start ********")

            if not df.empty:
                self.logger.debug(df.head(3))

                center_lat_lng_list = []

                required_columns =['geometry.viewport.northeast.lat', 'geometry.viewport.northeast.lng', 'geometry.viewport.southwest.lat', 'geometry.viewport.southwest.lng']

                # 必須のcolumnがDataFrameに存在するのを確認
                if all(column in df.columns for column in required_columns):
                    for index, row in df.iterrows():
                        northeast_lat = row['geometry.viewport.northeast.lat']
                        northeast_lng  = row['geometry.viewport.northeast.lng']
                        southwest_lat = row['geometry.viewport.southwest.lat']
                        southwest_lng = row['geometry.viewport.southwest.lng']

                        self.logger.debug(f"northeast_lat: {northeast_lat}")
                        self.logger.debug(f"northeast_lng: {northeast_lng}")
                        self.logger.debug(f"southwest_lat: {southwest_lat}")
                        self.logger.debug(f"southwest_lng: {southwest_lng}")

                        # 北東と南西の位置から中心を割り出す
                        center_lat = (northeast_lat + southwest_lat) / 2
                        center_lng = (northeast_lng + southwest_lng) / 2

                        self.logger.debug(f"center_lat: {center_lat}")
                        self.logger.debug(f"center_lng: {center_lng}")

                        # 辞書データにする
                        lat_lng_dict = {'center_lat' : center_lat,'center_lng' : center_lng}
                        center_lat_lng_list.append(lat_lng_dict)

                self.logger.info(f"{index} center_lat_lng_list: {center_lat_lng_list}")

                # 辞書データをDataFrameにする
                center_lat_lng_df = pd.DataFrame(center_lat_lng_list)


                self.logger.info(f"********  _get_navi_position end ********")

                return center_lat_lng_df

        except Exception as e:
            self.logger.error(f"_get_navi_position 処理中にエラーが発生: {e}")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {e}")
            sys.exit(1)



# ----------------------------------------------------------------------------------
# TODO  レビューをソートして

    def _sort_reviews_to_df(self, cell_data):
        try:
            self.logger.info(f"******** _sort_reviews_to_df start ********")

            self.logger.debug(f"cell_data: {cell_data}")

            # 空の場合（NaN）の場合
            if cell_data is None or (isinstance(cell_data, float) and math.isnan(cell_data)):
                self.logger.debug(f"{cell_data} が None")
                return 'レビューデータがありません。'

            # 'rating'にて降順にsort
            sorted_rating = sorted(cell_data, key=lambda x: x['rating'], reverse=True)

            self.logger.debug(f"sorted_rating: {sorted_rating}")

            # 辞書を作成する（Column名のケツに1を足していく）
            # 辞書を作る→DataFrameにした際にはKeyがColumnになる
            # 空のDataFrameを作成する際には全てに[None]を入れる

            review_columns = {f'review{ i + 1 }_rating' : [None] for i in range(5)}
            self.logger.debug(f"review_columns: {review_columns}")


            # .updateは追記するということ
            review_columns.update({f'review{ i + 1 }_name' : [None] for i in range(5)})
            review_columns.update({f'review{ i + 1 }_text' : [None] for i in range(5)})

            review_columns = {f'review{ i + 1 }_rating' : '-' for i in range(5)}

            # .updateは追記するということ
            review_columns.update({f'review{ i + 1 }_name' : '-' for i in range(5)})
            review_columns.update({f'review{ i + 1 }_text' : '-' for i in range(5)})


            self.logger.debug(f"review_columns: {review_columns}")

            # Columnの名称（順位）にそれぞれの値を埋め込んでいく
            # 作られたColumnに順位別に横に埋め込んでいく感じ
            # 辞書の値を追加する際には基本は代入
            for i, review in enumerate(sorted_rating[:5]):
                review_columns[f'review{ i + 1}_rating'] = review['rating']
                review_columns[f'review{ i + 1}_name'] = review['author_name']
                review_columns[f'review{ i + 1}_text'] = review['text']

            for key, value in review_columns.items():
                if value == '-':
                    review_columns[key] = None


            self.logger.debug(f"review_columns: {review_columns}")


            self.logger.info(f"********  _sort_reviews_to_df end ********")

            return review_columns


        except Exception as e:
            self.logger.error(f"_sort_reviews_to_df 処理中にエラーが発生: {e}")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# DataFrameを並び替える

    def df_sort(self, df, new_order):
        try:
            self.logger.info(f"******** df_sort 開始 ********")

            self.logger.debug(f"df: \n{df.head(3)}")
            self.logger.debug(f"new_order: {new_order}")

            if not df.empty:
                if all(col in df.columns for col in new_order):
                    sorted_df = df[new_order]



                else:
                    sorted_df.to_csv('installer/result_output/sorted_df.csv')
                    raise ValueError("new_orderで指定してるcolumnがDataFrameに存在しない")


            self.logger.debug(f"df: \n{sorted_df.head(3)}")

            self.logger.info(f"******** df_sort 終了 ********")

            return sorted_df

        except ValueError as ve:
            self.logger.error(f"new_orderで指定してるcolumnがDataFrameに存在しない: {ve}")
            messagebox.showerror("エラー", f"new_orderで指定してるcolumnがDataFrameに存在しない: {e}")
            sys.exit(1)

        except Exception as e:
            self.logger.error(f"df_sort 処理中にエラーが発生: {e}")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# Google mapAPIでjson取得
# jsonからplase_idを取得
# plase_idから詳細が掲載されてるjsonを取得
# jsonからDataFrameへ変換
# DataFrameから行ごとのデータをリストへ変換する

    def get_gm_df_list(self, query, columns):
        try:
            self.logger.info(f"******** get_gm_df_list 開始 ********")


            # gmAPIリクエスト
            json_data = self._google_map_api_request(query=query)
            self.logger.critical(f'json_data: {json_data}')
            time.sleep(2)

            # plase_id_listを取得
            plase_id_list = self._get_place_id(json_data=json_data)
            self.logger.critical(f'plase_id_list: {plase_id_list}')

            time.sleep(2)

            # 詳細データを取得
            details_data_list = self._place_id_requests_in_list(place_id_list=plase_id_list)
            self.logger.critical(f'details_data_list: {details_data_list}')
            time.sleep(2)

            # 詳細データリストからresult部分を抽出してリストを作成
            results_data_list= self._get_results_list(place_details_results_list=details_data_list)
            time.sleep(2)

            self.logger.critical(f'results_data_list: {results_data_list}')


            # 詳細データをDataFrameに変換
            df = self._get_json_to_dataframe(json_data=results_data_list)
            time.sleep(2)

            #! 変換しなければならない箇所
            # 住所→formatted_addressをGoogle Maps Geocoding APIを使うことで日本語変換する→dfにして結合


            #TODO レビュ→profile_photo_url, author_name, rating, text, →それぞれの項目を作成なし（-）

            #TODO 写真→ありなし




            # DataFrameから必要なcolumn情報をリストにして取得
            self.get_column_data_in_df(df=df, columns=columns)
            time.sleep(2)


            self.logger.info(f"******** get_gm_df_list 終了 ********")

        except Exception as e:
            self.logger.error(f"get_gm_df_list 処理中にエラーが発生: {e}")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {e}")
            sys.exit(1)


# ----------------------------------------------------------------------------------
