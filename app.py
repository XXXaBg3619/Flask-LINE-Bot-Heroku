from __future__ import unicode_literals, with_statement
import json, requests, re, urllib, contextlib, time
from urllib.parse import urlencode
from urllib.request import urlopen
from emoji import UNICODE_EMOJI
from bs4 import BeautifulSoup
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage


app = Flask(__name__)

line_bot_api = LineBotApi("S1NRUscHr3pXdpnYh28UZlZmeEnmEbfX6rkSC3WHo/zSbBxUJcKgLEGtOoTlaHB7ntc/QBgAKFcwDuEvM5Kmtwhph1DdYBOeCcVB+N7Cnt9KRyrjdR6vA/+KONhX/VBvK+fqUq6yFpxsahuV3YRPQAdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("e104139d44baead65940861cbf50b707")
id_developer = "U1e38384f12f22c77281ec3e8611025c8"


limit = 5    # 每次傳送之商品數上限
Help = """【【搜尋功能】
若想在 pchome/momo/shopee 搜尋商品
請輸入：  商品名稱;平台 
(英文請輸入半型)
Ex:  PS5;pchome 、 滑鼠；MOMO
要看下一頁則輸入2 3 4 5.... (請不要向後跳頁)

【比價功能】
請輸入： 商品名稱;price  
(英文請輸入半型)
Ex:  PS5;price 、 滑鼠；Price
要看下一頁則輸入2 3 4 5.... (請不要向後跳頁)
*目前只能從最低價開始排*

【注意】
pchome回傳時間約1~3秒
shopee回傳時間約3~5秒
momo回傳時間約1~3秒
price回傳時間約3~5秒

若是需要查詢使用方式則輸入help即可
祝泥使用愉快～"""
mode_off = """機器人目前測試中
請稍後再使用
輸入help可查詢使用方式及新增功能"""
Except = """無法搜尋到商品
請確認輸入是否有誤～"""
# products_info = {id: products, ...}
# products = [{"url": url, "name": name, "price": price}, ...]



def make_tiny(url):
    request_url = "http://tinyurl.com/api-create.php?" + urlencode({"url": url})
    with contextlib.closing(urlopen(request_url)) as response:
        return response.read().decode("utf-8")
def isEmoji(content):
    for emoji in UNICODE_EMOJI['en']:
        if content.count(emoji) > 0:
            return True
    return False


# PChome線上購物 爬蟲
def pchome_search(keyword, page=1, sort='有貨優先'):
    all_sort = {'有貨優先': 'sale/dc', '價錢由高至低': 'prc/dc', '價錢由低至高': 'prc/ac'}
    name_enc = urllib.parse.quote(keyword) 
    url = f"https://ecshweb.pchome.com.tw/search/v3.3/all/results?q={name_enc}&page={page}&sort={all_sort[sort]}"
    data = json.loads(requests.get(url).text)
    products = data['prods']
    for i in products:
        i["link"] = "https://24h.pchome.com.tw/prod/" + i["Id"]
        i["price_avg"] = i["price"]
    return products

def pchome(id, name, page = 1):
    try:
        with open("products_info_pchome.json") as file:
            products_info = json.load(file)
            try:
                products = products_info[id]
                print("1-1")
            except:
                products = []
                products_info[id] = products
                print("1-2")
    except:
        products = []
        products_info = {id: products}
        print("1-3")
    if (page*limit) % 20 != 0:
        pages = (page*limit) // 20 + 1
    else:
        pages = (page*limit) // 20
    if page == 1 and products == []:
        products = pchome_search(name)
        print("len:", len(products))
    elif len(products) < page * limit:
        print("check point")
        products += pchome_search(name, pages)
    with open("pchome_porducts_info.json", "w") as file:
        json.dump(products_info, file)
    message = ""
    for i in range(limit*(page-1), limit*page):
        message += products[i]["link"] + "\n"
        message += products[i]["name"] + "\n"
        message += "$" + str(products[i]["price"]) + "\n"
    message += " " * 20 + f"[第{page}頁]"
    return message

# MOMO線上購物 爬蟲
def momo_search(name, page = 1, Type = 1):
    name_enc = urllib.parse.quote(name)
    if (page*limit) % 20 != 0:
        pages = (page*limit) // 20 + 1
    else:
        pages = (page*limit) // 20
    url = f"https://m.momoshop.com.tw/search.momo?searchKeyword={name_enc}&searchType={Type}&cateLevel=-1&curPage={pages}&maxPage=16.html"
    headers = {'User-Agent': 'mozilla/5.0 (Linux; Android 6.0.1; '
                             'Nexus 5x build/mtc19t applewebkit/537.36 (KHTML, like Gecko) '
                             'Chrome/51.0.2702.81 Mobile Safari/537.36'}
    resp = requests.get(url, headers=headers)
    if not resp:
        return []
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    products = []
    for elem in soup.find_all("li", "goodsItemLi"):
        item_url = 'http://m.momoshop.com.tw' + elem.find('a')['href']
        item_name = elem.find("h3", "prdName").text.strip()
        item_price = elem.find("b", {"class": "price"}).text.strip()
        if not item_price:
            continue
        products.append({
            'link': item_url,
            'name': item_name,
            'price': item_price,
            'price_avg': item_price
        })
    return products
    
def momo(id, name, page = 1):
    try:
        with open("products_info_momo.json") as file:
            products_info = json.load(file)
            try:
                products = products_info[id]
            except:
                products = []
                products_info[id] = products
    except:
        products = []
        products_info = {id: products}
    if (page*limit) % 20 != 0:
        pages = (page*limit) // 20 + 1
    else:
        pages = (page*limit) // 20
    if page == 1 and products == []:
        products = momo_search(name)
    else:
        products += momo_search(name, pages)
    with open("products_info_momo.json", "w") as file:
        json.dump(products_info, file)
    message = ""
    for i in range(limit*(page-1), limit*page):
        message += products[i]["link"] + "\n"
        message += products[i]["name"] + "\n"
        message += "$" + products[i]["price"] + "\n"
    message += " " * 20 + f"[第{page}頁]"
    return message


# Shopee線上購物 爬蟲
def shopee_search(name, page = 1, order = "desc"):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68',
        'x-api-source': 'pc',
        'referer': f'https://shopee.tw/search?keyword={urllib.parse.quote(name)}'
    }
    if order == "desc":
        new = 50
    elif order == "asc":
        new = 20
    url = f'https://shopee.tw/api/v2/search_items/?by=price&keyword={name}&limit=20&newest={new*(page-1)}&order={order}&page_type=search&version=2'
    resq = requests.Session().get(url, headers=headers)
    if resq.status_code == requests.codes.ok:
        data = resq.json()
    products = []
    for item in data["items"]:
        title = item["name"]
        shopid, itemid = item["shopid"], item["itemid"]
        title_fix = title.replace(" ", "-")
        if isEmoji(title) == True:
            link = make_tiny(f"https://shopee.tw/{title_fix}-i.{shopid}.{itemid}")
            tiny = True
        else:
            for i in ("[", "<", ":", "：", "【"):
                if i in title:
                    link = make_tiny(f"https://shopee.tw/{title_fix}-i.{shopid}.{itemid}")
                    tiny = True
                    break
                tiny = False
        if not tiny:
            link = f"https://shopee.tw/{title_fix}-i.{shopid}.{itemid}"
        price_min, price_max = int(item["price_min"])//100000, int(item["price_max"])//100000
        if price_min == price_max:
            price = str(int(item["price"] // 100000))
        else:
            price = f"{price_min} ~ {price_max}"
        products.append({"link": link, "name": title, "price": price})
        if order == "asc":
            price_avg = round((price_max+price_min)/2) if "~" in price else int(price)
            products[-1]["price_avg"] = price_avg
    return products

def shopee(id, name, page = 1):
    try:
        with open("products_info_shopee.json") as file:
            products_info = json.load(file)
            try:
                products = products_info[id]
            except:
                products = []
                products_info[id] = products
    except:
        products = []
        products_info = {id: products}
    if (page*limit) % 50 != 0:
        pages = (page*limit) // 50 + 1
    else:
        pages = (page*limit) // 50
    if page == 1 and products == []:
        print("check point")
        products = shopee_search(name, 1)
    else:
        products += shopee_search(name, pages)
    with open("products_info_shopee.json", "w") as file:
        json.dump(products_info, file)
    message = ""
    for i in range(limit*(page-1), limit*page):
        message += products[i]["link"] + "\n"
        message += products[i]["name"] + "\n"
        message += "$" + str(products[i]["price"]) + "\n"
    message += " " * 20 + f"[第{page}頁]"
    return message


def price(id, name, page = 1):
    try:
        with open("products_info_price.json") as file:
            products_info = json.load(file)
            try:
                products = products_info[id]
            except:
                products = []
                products_info[id] = products
    except:
        products = []
        products_info = {id: products}
    if (page*limit) % 20 != 0:
        pages = (page*limit) // 20 + 1
    else:
        pages = (page*limit) // 20
    if page == 1 and products == []:
        products = pchome_search(name, sort = "價錢由低至高")
        products += momo_search(name, Type = 2)
        products += shopee_search(name, order = "asc")
    elif len(products) < page * limit:
        products += pchome_search(name, pages, sort = "價錢由低至高")
        products += momo_search(name, pages, Type = 2)
        products += shopee_search(name, pages, "asc")
    products = sorted(products, key = lambda d: d["price_avg"]) 
    with open("products_info_price.json", "w") as file:
        json.dump(products_info, file)
    message = ""
    for i in range(limit*(page-1), limit*page):
        message += products[i]["link"] + "\n"
        if "pchome" in products[i]["link"]:
            message += "〈PChome〉" + products[i]["name"] + "\n"
        else:
            message += "〈Shopee〉" + products[i]["name"] + "\n"
        message += "$" + str(products[i]["price"]) + "\n"
    message += " " * 20 + f"[第{page}頁]"
    return message
    

def search(id, info, page = 1):
    if len(info["platform"]) >= 6:
        info["platform"] = info["platform"][:6]
    if info["platform"] == "pchome":
        return pchome(id, info["search_name"], page)
    elif info["platform"] == "momo":
        return momo(id, info["search_name"], page)
    elif info["platform"] in ("shopee", "蝦皮"):
        return shopee(id, info["search_name"], page)
    elif info["platform"] == "price":
        return price(id, info["search_name"], page)
    else:
        return Except



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

# 搜尋商品
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    start = time.time()
    text = event.message.text.lower().rstrip().strip()
    id = event.source.user_id
    try:
        with open("search_info.json") as file:
            info = json.load(file)
            try:
                info_id = info[id]
            except:
                info_id = {}
                info[id] = info_id
    except:
        info_id = {}
        info = {"mode_off": True, id: info_id}
    if text == "help":
        message = Help
    elif info["mode_off"] and id != id_developer:
        message = mode_off
    elif ";" in text:
        info_id["search_name"], info_id["platform"] = text.split(";")
        message = search(id, info_id)
    elif "；" in text:
        info_id["search_name"], info_id["platform"] = text.split("；")
        message = search(id, info_id)
    elif text.isdigit() == True:
        message = search(id, info_id, int(text))
    elif text == "mode off" and id == id_developer:
        info["mode_off"] = True
        print("mode off")
        message = "mode off"
    elif text == "mode on" and id == id_developer:
        info["mode_off"] = False
        print("mode on")
        message = "mode on"
    else:
        message = Except
    with open("search_info.json", "w") as file:
        json.dump(info, file)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = message))
    end = time.time()
    print("time:", end - start, "s")

if __name__ == "__main__":
    app.run()
