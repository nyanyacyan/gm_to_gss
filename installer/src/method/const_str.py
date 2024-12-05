#  coding: utf-8
# 文字列をすべてここに保管する
# ----------------------------------------------------------------------------------
# 2024/7/17 更新
# tree -I 'venv|resultOutput|__pycache__'

# ----------------------------------------------------------------------------------
from enum import Enum


# ----------------------------------------------------------------------------------
#! 基本必須 →　pathで使ってる

class Dir(Enum):
    result='resultOutput'
    input='inputData'


# ----------------------------------------------------------------------------------
#! 基本必須

class SubDir(Enum):
    pickles='pickles'
    cookies='cookies'
    DBSubDir='DB'
    SCREEN_SHOT='screenshot'
    DEBUG_CSV='debug_csv'


# ----------------------------------------------------------------------------------
#! 基本必須

class FileName(Enum):
    JSON_KEY="handy-station-424804-j2-736b08fedd3a.json"


# ----------------------------------------------------------------------------------
#! 基本必須

class Extension(Enum):
    text='.txt'
    csv='.csv'
    json='.json'
    pickle='.pkl'
    excel='.xlsx'
    yaml='.yaml'
    cookie='cookie.pkl'
    DB='.db'
    PNG='.png'



# ----------------------------------------------------------------------------------
# サイトURL

class SiteUrl(Enum):
    LOGIN_URL='https://auth.es-account.com/u/login?state=hKFo2SB3QVZpdlM5eG9sR1JaTlVKTER3STFzZ1dkRWxOSmxmZ6Fur3VuaXZlcnNhbC1sb2dpbqN0aWTZIFVOMHBPX0F5eTFNdWRIdWVVNFVOOXgzX0RqbDBvSV9Po2NpZNkgYUlTZzRxQmxHWEpYZHpoZklSTnNwZFZMTkdtY3JsU2s'
    HOME_URL='https://www.xdomain.ne.jp/'
    TARGET_URL=''

    GSS_URL=''


# ----------------------------------------------------------------------------------


class GssInfo(Enum):
    SITE='https://docs.google.com/spreadsheets/d/1Ya6EJe4laeENG_3lMVJqzV_qYOWEF6NpSeHxVE37yTE/edit?gid=0#gid=0'

    SHEET_ID='1Ya6EJe4laeENG_3lMVJqzV_qYOWEF6NpSeHxVE37yTE'

    WORKSHEET_1='gm'




# ----------------------------------------------------------------------------------


class Encoding(Enum):
    utf8='utf-8'


# ----------------------------------------------------------------------------------
# DiscordUrl

class Debug(Enum):
    discord = 'https://discord.com/api/webhooks/1220239805204660314/niMRY1OVJwYh3PY9X9EfF2O6C7ZPhukRDoXfsXlwGBz4n1HKE81MA1B6TQiy2FUnzHfk'


# ----------------------------------------------------------------------------------
# 通知メッセージ

class ErrorMessage(Enum):
    chromeDriverManagerErrorTitle = "ChromeDriver セットアップエラー"
    chromeDriverManagerError = (
        "ChromeDriver のセットアップに失敗しました。以下の手順を確認してください：\n"
        "1. ChromeDriver のバージョンがインストールされている Chrome ブラウザと一致しているか\n"
        "2. 必要な権限が不足していないか\n"
        "3. PATH 環境変数に ChromeDriver のパスが正しく設定されているか\n"
        "4. 必要であれば、システムを再起動して環境をリフレッシュしてください。\n"
        "詳細なエラー内容はログをご確認ください。"
    )


# ----------------------------------------------------------------------------------

# Endpoint

class EndPoint(Enum):
    Line ="https://notify-api.line.me/api/notify"
    Chatwork = 'https://api.chatwork.com/v2'
    Slack = 'https://slack.com/api/chat.postMessage'
    Discord = 'https://discord.com/api/webhooks/1220239805204660314/niMRY1OVJwYh3PY9X9EfF2O6C7ZPhukRDoXfsXlwGBz4n1HKE81MA1B6TQiy2FUnzHfk'

    ChatGPT = 'https://api.openai.com/v1/engines/{}/completions'
    GOOGLE_MAP="https://maps.googleapis.com/maps/api/place/textsearch/json"
    GOOGLE_MAP_PLACE="https://maps.googleapis.com/maps/api/place/details/json"

# ----------------------------------------------------------------------------------

# ChatgptUtils

class ChatgptUtils(Enum):
    # "gpt-4o-mini-2024-07-18" or "gpt-4o-2024-08-06"
    model='gpt-4o-mini-2024-07-18'

    endpointUrl='https://api.openai.com/v1/chat/completions'

    MaxToken=16000

# ----------------------------------------------------------------------------------


class ChatGptPrompt(Enum):
    recommend="""
    渡す店舗情報（JSON形式）から、過去1年以内に出店した店舗を厳選して収集してください。該当する店舗がない場合は「該当なし」と明記してください。
    例.
    [
        {
            "店舗名": "洪記餃子",
            "住所": "日本、〒157-0062 東京都世田谷区南烏山５丁目１８−１９",
            "電話番号": "03-4362-0796",
            "出店日": "2023-11-01",
            "Googleマップリンク": "https://goo.gl/maps/example"
        }
    ]

    収集すべき情報:
    ・店舗名
    ・住所
    ・電話番号
    ・出店日（YYYY-MM-DD形式）
    ・Googleマップのリンク
    ・フィルタ条件:

    出店日が本日から1年以内の間であること。
    出店日が不明な場合は、出力先に明記しない。


    方法:
    ・渡されたデータの中からフィルタ条件に合致する店舗を厳選してください。
    ・出店日の情報が不足している場合は、その店舗を無視してください。

    入力データ形式（例）:
    ```json
    [
        {
            "店舗名": "洪記餃子",
            "住所": "日本、〒157-0062 東京都世田谷区南烏山５丁目１８−１９",
            "電話番号": "03-4362-0796",
            "出店日": "2023-11-01",
            "Googleマップリンク": "https://goo.gl/maps/example"
        },
        {
            "店舗名": "山田そば店",
            "住所": "日本、〒150-0002 東京都渋谷区渋谷1丁目1-1",
            "電話番号": "03-1234-5678",
            "出店日": "2022-10-20",
            "Googleマップリンク": "https://goo.gl/maps/example2"
        }
    ]

    該当する店舗がない場合は、以下のように出力してください。
    該当なし

    注意点:
    ・出店日の精度が高い情報を優先してください。
    ・情報が不明な場合は「不明」と記載し、データの精度を維持すること。
    ・レビュー内で出店日を示唆する記述がある場合、その根拠を併記してください（例: 「2023年2月にオープンしました」というレビューがある場合）。
    ・この指示に従い、指定された期間内に出店した店舗情報を収集・整理してください。
    ・Outputデータのみ返答してください。

    店舗情報
    {json}
    """


# ----------------------------------------------------------------------------------

