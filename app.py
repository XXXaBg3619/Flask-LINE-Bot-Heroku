from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (MessageEvent,
                            TextMessage,
                            TextSendMessage,
                            ImageSendMessage,
                            VideoSendMessage,
                            AudioSendMessage,
                            LocationSendMessage,
                            StickerSendMessage,
                            ImagemapSendMessage,
                            TemplateSendMessage,
                            ButtonsTemplate,
                            MessageTemplateAction,
                            PostbackEvent,
                            PostbackTemplateAction)
import os

app = Flask(__name__)

line_bot_api = LineBotApi("S1NRUscHr3pXdpnYh28UZlZmeEnmEbfX6rkSC3WHo/zSbBxUJcKgLEGtOoTlaHB7ntc/QBgAKFcwDuEvM5Kmtwhph1DdYBOeCcVB+N7Cnt9KRyrjdR6vA/+KONhX/VBvK+fqUq6yFpxsahuV3YRPQAdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("e104139d44baead65940861cbf50b707")


@app.route("/", methods=["GET", "POST"])
def callback():

    if request.method == "GET":
        return "Hello Heroku"
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text

    def text_reply(content):
        reply = TextSendMessage(text=content)
        line_bot_api.reply_message(event.reply_token, reply)

    if isinstance(event, MessageEvent):
        if get_message == 'test':
            line_bot_api.reply_message(  # 回復傳入的訊息文字
                event.reply_token,
                TemplateSendMessage(  # 選單
                    alt_text='Buttons template',
                    template=ButtonsTemplate(
                        title='功能選單',
                        text='請選擇功能',
                        actions=[
                            MessageTemplateAction(
                                label='購買商品',
                                text='購買商品',
                                data='A&func1'
                            ),
                            MessageTemplateAction(
                                label='快速上架',
                                text='快速上架',
                                data='A&func2'
                            ),
                            MessageTemplateAction(
                                label='物流追蹤',
                                text='物流追蹤',
                                data='A&func3'
                            )
                        ]
                    )
                )
            )
    elif isinstance(event, PostbackEvent):
        if event.postback.data == "A&func1":  # 如果回傳值為「購買商品」
            text_reply('請輸入關鍵字:')
