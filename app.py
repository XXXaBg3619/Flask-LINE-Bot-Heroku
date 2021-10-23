from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler

from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from random import choice
import os
import psycopg2
from random import choice
text_all = [True, False]
app = Flask(__name__)

line_bot_api = LineBotApi("S1NRUscHr3pXdpnYh28UZlZmeEnmEbfX6rkSC3WHo/zSbBxUJcKgLEGtOoTlaHB7ntc/QBgAKFcwDuEvM5Kmtwhph1DdYBOeCcVB+N7Cnt9KRyrjdR6vA/+KONhX/VBvK+fqUq6yFpxsahuV3YRPQAdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("e104139d44baead65940861cbf50b707")


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


DATABASE_URL = 'postgres://xseaswlvhvhgnm:a6383e19f7ab5a17b0b89671e2d8c363ce18a229550faaac57d61058e8269929@ec2-34-233-64-238.compute-1.amazonaws.com:5432/de3mlq5i95dhst'
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
