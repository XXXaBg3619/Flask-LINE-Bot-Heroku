from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

import configparser

import urllib
import re
import random

app = Flask(__name__)

line_bot_api = LineBotApi("S1NRUscHr3pXdpnYh28UZlZmeEnmEbfX6rkSC3WHo/zSbBxUJcKgLEGtOoTlaHB7ntc/QBgAKFcwDuEvM5Kmtwhph1DdYBOeCcVB+N7Cnt9KRyrjdR6vA/+KONhX/VBvK+fqUq6yFpxsahuV3YRPQAdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("e104139d44baead65940861cbf50b707")


# 接收 LINE 的資訊
@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 請 pixabay 幫我們找圖
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        try:
                        
            img_list = []

            img_search = {'tbm': 'isch', 'q': event.message.text}
            query = urllib.parse.urlencode(img_search)
            base  = "https://www.google.com/search?"
            url   = str(base+query)

            headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

            res  = urllib.request.Request(url, headers=headers)
            con  = urllib.request.urlopen(res)
            data = con.read()

            pattern = '"(https://encrypted-tbn0.gstatic.com[\S]*)"'

            for match in re.finditer(pattern, str(data, "utf-8")):
                img_list.append(match.group(1))

            random_img_url = img_list[random.randint(0, len(img_list)+1)]

            message = ImageSendMessage(
                original_content_url = random_img_url,
                preview_image_url    = random_img_url
            )
            line_bot_api.reply_message(event.reply_token, message)
        # 如果找不到圖，就學你說話
        except:
            line_bot_api.reply_message(
                event.reply_token,
                #TextSendMessage(text=event.message.text)
                TextSendMessage(text="https://www.learncodewithmike.com/2020/02/python-beautifulsoup-web-scraper.html")
            )
            pass

if __name__ == "__main__":
    app.run()
