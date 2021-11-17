# WebAPI系
from flask import Flask, request, abort
# 環境変数系
from dotenv import load_dotenv
import os
# LineBot系
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent
)
# 二要素認証
import pyotp

# Flask(API)の初期化
app = Flask(__name__)

# LineBotSDKの初期化(環境変数から読み取り)
load_dotenv('.env')
line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))

# 仮置きにつき、実際の利用時は まともなDBを用意すること
database = {
    'user_id': {
        'service': 'otpauth://totp/service?secret=secret&issuer=issuer'
    }
}


def sendMessage(token, texts):
    """
    メッセージを返す用のショートハンド
    (どうも reply_tokenは1度しか使えないようなので textsは配列にしてある)
    """
    line_bot_api.reply_message(
        token,
        [TextSendMessage(text=text) for text in texts]
    )


@app.route("/callback", methods=['POST'])
def callback():
    """
    LINE Botからのリクエストを受け取るエンドポイント
    """
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        # イベントの種別毎に適切な関数が呼ばれる
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("署名が不正です、ChannelIDとシークレットを確認してください")
        abort(400)
    return 'OK'


@handler.add(FollowEvent)
def handle_follow(event):
    """
    LINE Botからのリクエストのうち 友達登録に対する反応
    """
    reply_token = event.reply_token
    sendMessage(
        reply_token,
        [
            "\n".join([
                "友達登録ありがとうございます!",
                "このBotは、GoogleAuthenticatorのコード生成をLINEBot上で行うものです。",
                "下記のコマンド表をご覧の上操作してください。"
            ]),
            "\n".join([
                "(otpauth://totp/ ではじまるアドレス): 指定された認証鍵を登録します",
                "(認証コードを取得したいサービス名): 指定されたサービスの認証コードを送付します",
                "登録済みサービス一覧: 登録済みの認証鍵のサービス名一覧を送付します"
            ])
        ]
    )


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """
    LINE Botからのリクエストのうち テキストメッセージに対する反応
    """
    user_id = event.source.user_id
    message = event.message.text
    reply_token = event.reply_token

    # 認証鍵の登録
    if message.startswith("otpauth://totp/"):
        try:
            totp = pyotp.parse_uri(message)
            service_name = message.split("/")[3].split("?")[0]
            if user_id not in database:
                database[user_id] = {}
            database[user_id][service_name] = message
            sendMessage(reply_token, [f"{service_name}\nの認証鍵を登録しました"])
        except ValueError:
            sendMessage(reply_token, ["指定された認証鍵が正しくありません"])
        return
    # 認証鍵の一覧
    if message == "登録済みサービス一覧":
        if user_id in database:
            sendMessage(
                reply_token,
                [
                    "下記サービスの鍵が登録されています",
                    "\n".join(database[user_id].keys())
                ]
            )
        else:
            sendMessage(reply_token, ["現在登録済みのサービスはありません"])
        return
    # ユーザーIDがDBに存在したら
    if user_id in database:
        # そのユーザーの登録してるサービス名一覧を取ってきて
        for service_name in database[user_id]:
            # 頭文字が一致していれば(あまりよい処理でないが)
            if service_name.lower().startswith(message.lower()):
                # 認証鍵を発行して返す
                totp = pyotp.parse_uri(database[user_id][service_name])
                sendMessage(
                    reply_token,
                    [
                        f"{service_name}\nの認証コード",
                        totp.now()
                    ]
                )
                return


if __name__ == "__main__":
    app.run()
