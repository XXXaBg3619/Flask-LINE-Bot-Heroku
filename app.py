from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler

from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from random import choice
import os
import psycopg2
from random import choice
text_all = [True, False]
app = Flask(name)

line_bot_api = LineBotApi(os.environ.get(
    'u0ooJQtQaKfviCcS1fQNH8bcaOxMoGzBDGgEXGu+CAnG0ortULU/B1Ce628MGhm3hNgkngpuD49W/zik8x+JXQAal1+WxK8NtdPAjJvXz01Zj4H0P6NefQVWjdhZQunBIg4E+quJrXan2LI5dDMAKgdB04t89/1O/w1cDnyilFU='))
handler = WebhookHandler(os.environ.get('496a695efa3e35da186774ccc0a60898'))


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


DATABASE_URL = os.environ['postgres://xseaswlvhvhgnm:a6383e19f7ab5a17b0b89671e2d8c363ce18a229550faaac57d61058e8269929@ec2-34-233-64-238.compute-1.amazonaws.com:5432/de3mlq5i95dhst']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

cursor = conn.cursor()
record = (choice(text_all))
table_columns = '(orderstate)'
postgres_insert_query = f"""INSERT INTO orderInfo {table_columns} VALUES (%s);"""


cursor.execute(postgres_insert_query, record)

conn.commit()
count = cursor.rowcount


cursor.close()
conn.close()


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "我的商品狀態":
        text = choice(text_all)
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text))
    else:
        text = "抱歉，我不清楚"
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text))


if '__name__' == '__main__':
    app.run()
