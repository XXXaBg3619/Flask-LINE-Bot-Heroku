from __future__ import unicode_literals
import os, json, requests, configparser, urllib, re, random
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage


app = Flask(__name__)

line_bot_api = LineBotApi("S1NRUscHr3pXdpnYh28UZlZmeEnmEbfX6rkSC3WHo/zSbBxUJcKgLEGtOoTlaHB7ntc/QBgAKFcwDuEvM5Kmtwhph1DdYBOeCcVB+N7Cnt9KRyrjdR6vA/+KONhX/VBvK+fqUq6yFpxsahuV3YRPQAdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("e104139d44baead65940861cbf50b707")


send_products_limit = 5    # 每次傳送之商品數上限
last_search = ["", [], 0]    # 最新一次搜尋商品的名稱/紀錄/頁數


# PChome線上購物 爬蟲
class PchomeSpider():
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
        }

    # 送出 GET 請求
    def request_get(self, url, params=None, to_json=True):
        """
        param url: 請求網址
        param params: 傳遞參數資料
        param to_json: 是否要轉為 JSON 格式
        return data: requests 回應資料
        """
        r = requests.get(url, params)
        print(r.url)
        if r.status_code != requests.codes.ok:
            print(f'網頁載入發生問題：{url}')
        try:
            if to_json:
                data = r.json()
            else:
                data = r.text
        except Exception as e:
            print(e)
            return None
        return data

    # 搜尋商品
    def search_products(self, keyword, max_page=1, shop='全部', sort='有貨優先', price_min=-1, price_max=-1, is_store_pickup=False, is_ipost_pickup=False):
        """
        param keyword: 搜尋關鍵字
        param max_page: 抓取最大頁數
        param shop: 賣場類別 (全部、24h購物、24h書店、廠商出貨、PChome旅遊)
        param sort: 商品排序 (有貨優先、精準度、價錢由高至低、價錢由低至高、新上市)
        param price_min: 篩選"最低價" (需與 price_max 同時用)
        param price_max: 篩選"最高價" (需與 price_min 同時用)
        param is_store_pickup: 篩選"超商取貨"
        param is_ipost_pickup: 篩選"i 郵箱取貨"
        return products: 搜尋結果商品
        """
        products = []
        all_shop = {
            '全部': 'all',
            '24h購物': '24h',
            '24h書店': '24b',
            '廠商出貨': 'vdr',
            'PChome旅遊': 'tour',
        }
        all_sort = {
            '有貨優先': 'sale/dc',
            '精準度': 'rnk/dc',
            '價錢由高至低': 'prc/dc',
            '價錢由低至高': 'prc/ac',
            '新上市': 'new/dc',
        }

        url = f'https://ecshweb.pchome.com.tw/search/v3.3/{all_shop[shop]}/results'
        params = {
            'q': keyword,
            'sort': all_sort[sort],
            'page': 0
        }
        if price_min >= 0 and price_max >= 0:
            params['price'] = f'{price_min}-{price_max}'
        if is_store_pickup:
            params['cvs'] = 'all'   # 超商取貨
        if is_ipost_pickup:
            params['ipost'] = 'Y'   # i 郵箱取貨

        while params['page'] < max_page:
            params['page'] += 1
            data = self.request_get(url, params)
            if not data:
                print(f'請求發生錯誤：{url}{params}')
                break
            if data['totalRows'] <= 0:
                print('找不到有關的產品')
                break
            products.extend(data['prods'])
            if data['totalPage'] <= params['page']:
                break
        return products

    # 取得商品販售狀態
    def get_products_sale_status(self, products_id):
        """
        param products_id: 商品 ID
        return data: 商品販售狀態資料
        """
        if type(products_id) == list:
            products_id = ','.join(products_id)
        url = f'https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/button&id={products_id}'
        data = self.request_get(url)
        if not data:
            print(f'請求發生錯誤：{url}')
            return []
        return data

    # 取得商品規格種類
    def get_products_specification(self, products_id):
        """
        param products_id: 商品 ID
        return data: 商品規格種類
        """
        if type(products_id) == list:
            products_id = ','.join(products_id)
        url = f'https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/spec&id={products_id}&_callback=jsonpcb_spec'
        data = self.request_get(url, to_json=False)
        data = json.loads(data[17:-48])    # 去除前後 JS 語法字串
        return data

    # 取得搜尋商品分類(網頁左側)
    def get_search_category(self, keyword):
        """
        param keyword: 搜尋關鍵字
        return data: 分類資料
        """
        url = f'https://ecshweb.pchome.com.tw/search/v3.3/all/categories?q={keyword}'
        data = self.request_get(url)
        return data

    # 取得商品子分類的名稱(網頁左側)
    def get_search_categories_name(self, categories_id):
        """
        param categories_id: 分類 ID
        return data: 子分類名稱資料
        """
        if type(categories_id) == list:
            categories_id = ','.join(categories_id)
        url = f'https://ecapi-pchome.cdn.hinet.net/cdn/ecshop/cateapi/v1.5/store&id={categories_id}&fields=Id,Name'
        data = self.request_get(url)
        return data
pchome_spider = PchomeSpider()

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

# 使用 pchome 搜尋商品
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global last_search
    message = ""
    text = event.message.text
    # 搜尋商品時
    if text.isdigit() == False:
        products = pchome_spider.search_products(text)
        last_search = [text, products, 1]
    # 查找頁數(已爬下來)
    elif len(last_search[1])//5 >= int(text):
        products = last_search[1]
        last_search[2] = int(text)
    # 查找頁數(未爬下來)
    else:
        products = pchome_spider.search_products(last_search[0], int(text)//4 + 1)
        last_search[1::] = [products, int(text)]
    large_len = 0
    print(last_search[0], last_search[2])
    try:
        for i in range(send_products_limit*(last_search[2]-1), send_products_limit*last_search[2]):
            message += "https://24h.pchome.com.tw/prod/" + products[i]["Id"] + "\n"
            message += products[i]["name"] + "\n"
            message += "$" + str(products[i]["price"]) + "\n"
            large_len = max(
                len("https://24h.pchome.com.tw/prod/"+products[i]["Id"]), 
                len(products[i]["name"]), 
                len("$" + str(products[i]["price"]))
                )
        message += " " * (large_len//2) + f"[第{last_search[2]}頁]"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = message))
    except:
        print(send_products_limit*(last_search[2]-1), send_products_limit*last_search[2])
    # 如果搜不到商品，就學你說話
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=event.message.text)
    # )

if __name__ == "__main__":
    app.run()
