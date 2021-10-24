from __future__ import unicode_literals, with_statement
import json, requests, re, urllib, contextlib, time
from urllib.parse import urlencode
from urllib.request import urlopen
from emoji import UNICODE_EMOJI
from bs4 import BeautifulSoup
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage


app = Flask(__name__)

line_bot_api = LineBotApi("S1NRUscHr3pXdpnYh28UZlZmeEnmEbfX6rkSC3WHo/zSbBxUJcKgLEGtOoTlaHB7ntc/QBgAKFcwDuEvM5Kmtwhph1DdYBOeCcVB+N7Cnt9KRyrjdR6vA/+KONhX/VBvK+fqUq6yFpxsahuV3YRPQAdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("e104139d44baead65940861cbf50b707")
id_developer = "U1e38384f12f22c77281ec3e8611025c8"


limit = 10    # 每次傳送之商品數上限
Help = """【搜尋功能】
若想在 pchome/momo/shopee 搜尋商品
請先輸入 平台名稱 ，機器人回應後再輸入 產品名稱
Ex: PChome、PS5、MOMO、switch
要看第ｎ頁則輸入n

【比價功能】
請先輸入 price1/price2 ，機器人回應後再輸入 產品名稱
price1：價錢由低至高
price2：價錢由高至低
Ex:  price1、PS5、Price2、滑鼠
要看第ｎ頁則輸入n

若是需要查詢使用方式則輸入help即可
祝泥使用愉快～"""
mode_off = """機器人目前測試中
請稍後再使用
輸入help可查詢使用方式及新增功能"""
Except = """無法搜尋到商品
請確認輸入是否有誤～"""
# products_info = {id: products, ...}
# products = [{"url": url, "name": name, "price": price}, ...]

def bubble_reload(nameList, priceList, urlList, Platform):
    platform = f"〈{Platform}〉" 
    bubble = {
        "type": "carousel",
        "contents": [
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": platform,
                            "color": "#00ff00",
                            "size": "32px"
                        },
                        {
                            "type": "text",
                            "text": nameList[0],
                            "weight": "bold",
                            "size": "sm",
                            "wrap": True
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"${priceList[0]}",
                                    "weight": "bold",
                                    "size": "md",
                                    "flex": 0
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "uri",
                                "label": "商品連結",
                                "uri":  urlList[0]
                            }
                        }
                    ]
                }
            },
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": platform,
                            "color": "#00ff00",
                            "size": "32px"
                        },
                        {
                            "type": "text",
                            "text": nameList[1],
                            "weight": "bold",
                            "size": "sm",
                            "wrap": True
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"${priceList[1]}",
                                    "weight": "bold",
                                    "size": "md",
                                    "flex": 0
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "uri",
                                "label": "商品連結",
                                "uri": urlList[1]
                            }
                        }
                    ]
                }
            },
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": platform,
                            "color": "#00ff00",
                            "size": "32px"
                        },
                        {
                            "type": "text",
                            "text": nameList[2],
                            "weight": "bold",
                            "size": "sm",
                            "wrap": True
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"${priceList[2]}",
                                    "weight": "bold",
                                    "size": "md",
                                    "flex": 0
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "uri",
                                "label": "商品連結",
                                "uri": urlList[2]
                            }
                        }
                    ]
                }
            },
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": platform,
                            "color": "#00ff00",
                            "size": "32px"
                        },
                        {
                            "type": "text",
                            "text": nameList[3],
                            "weight": "bold",
                            "size": "sm",
                            "wrap": True
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"${priceList[3]}",
                                    "weight": "bold",
                                    "size": "md",
                                    "flex": 0
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "uri",
                                "label": "商品連結",
                                "uri": urlList[3]
                            }
                        }
                    ]
                }
            },
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": platform,
                            "color": "#00ff00",
                            "size": "32px"
                        },
                        {
                            "type": "text",
                            "text": nameList[4],
                            "weight": "bold",
                            "size": "sm",
                            "wrap": True
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"${priceList[4]}",
                                    "weight": "bold",
                                    "size": "md",
                                    "flex": 0
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "uri",
                                "label": "商品連結",
                                "uri": urlList[4]
                            }
                        }
                    ]
                }
            },
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": platform,
                            "color": "#00ff00",
                            "size": "32px"
                        },
                        {
                            "type": "text",
                            "text": nameList[5],
                            "weight": "bold",
                            "size": "sm",
                            "wrap": True
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"${priceList[5]}",
                                    "weight": "bold",
                                    "size": "md",
                                    "flex": 0
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "uri",
                                "label": "商品連結",
                                "uri": urlList[5]
                            }
                        }
                    ]
                }
            },
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": platform,
                            "color": "#00ff00",
                            "size": "32px"
                        },
                        {
                            "type": "text",
                            "text": nameList[6],
                            "weight": "bold",
                            "size": "sm",
                            "wrap": True
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"${priceList[6]}",
                                    "weight": "bold",
                                    "size": "md",
                                    "flex": 0
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "uri",
                                "label": "商品連結",
                                "uri": urlList[6]
                            }
                        }
                    ]
                }
            },
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": platform,
                            "color": "#00ff00",
                            "size": "32px"
                        },
                        {
                            "type": "text",
                            "text": nameList[7],
                            "weight": "bold",
                            "size": "sm",
                            "wrap": True
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"${priceList[7]}",
                                    "weight": "bold",
                                    "size": "md",
                                    "flex": 0
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "uri",
                                "label": "商品連結",
                                "uri": urlList[7]
                            }
                        }
                    ]
                }
            },
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": platform,
                            "color": "#00ff00",
                            "size": "32px"
                        },
                        {
                            "type": "text",
                            "text": nameList[8],
                            "weight": "bold",
                            "size": "sm",
                            "wrap": True
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"${priceList[8]}",
                                    "weight": "bold",
                                    "size": "md",
                                    "flex": 0
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "uri",
                                "label": "商品連結",
                                "uri": urlList[8]
                            }
                        }
                    ]
                }
            },
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": platform,
                            "color": "#00ff00",
                            "size": "32px"
                        },
                        {
                            "type": "text",
                            "text": nameList[9],
                            "weight": "bold",
                            "size": "sm",
                            "wrap": True
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"${priceList[9]}",
                                    "weight": "bold",
                                    "size": "md",
                                    "flex": 0
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "uri",
                                "label": "商品連結",
                                "uri": urlList[9]
                            }
                        }
                    ]
                }
            }
        ]
    }
    return bubble


# PChome線上購物 爬蟲
def pchome_search(keyword, page, sort='有貨優先'):
    all_sort = {'有貨優先': 'sale/dc', '價錢由高至低': 'prc/dc', '價錢由低至高': 'prc/ac'}
    name_enc = urllib.parse.quote(keyword)
    url = f"https://ecshweb.pchome.com.tw/search/v3.3/all/results?q={name_enc}&page={page}&sort={all_sort[sort]}"
    data = json.loads(requests.get(url).text)
    products = data['prods']
    for i in products:
        i["link"] = "https://24h.pchome.com.tw/prod/" + i["Id"]
        i["price_avg"] = int(i["price"])
    return products


def pchome(nameList, priceList, urlList, id, name, page):
    try:
        with open("products_info_pchome.json") as file:
            products_info = json.load(file)
            try:
                products = products_info[id]["products"]
            except:
                products = []
                products_info[id]["products"] = products
    except:
        products = []
        products_info = {id: {"name": name, "products": products}}
    if products_info[id]["name"] != name:
        products = []
        products_info = {id: {"name": name, "products": products}}
    pages = ((page - 1) * limit) // 20 + 1
    if (page == 1 and products == []) or len(products) < page * limit:
        products += pchome_search(name, pages)
    with open("products_info_pchome.json", "w") as file:
        json.dump(products_info, file)
    for i in range(limit*(page-1), limit*page):
        nameList.append(products[i]["name"])
        priceList.append(products[i]["price"])
        urlList.append(products[i]["link"])

# MOMO線上購物 爬蟲


def momo_search(name, page, Type=1):
    name_enc = urllib.parse.quote(name)
    url = f"https://m.momoshop.com.tw/search.momo?searchKeyword={name_enc}&searchType={Type}&cateLevel=-1&curPage={page}&maxPage=16.html"
    headers = {'User-Agent': 'mozilla/5.0 (Linux; Android 6.0.1; '
                             'Nexus 5x build/mtc19t applewebkit/537.36 (KHTML, like Gecko) '
                             'Chrome/51.0.2702.81 Mobile Safari/537.36'}
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    products = []
    for elem in soup.find_all("li", "goodsItemLi"):
        item_url = 'http://m.momoshop.com.tw' + elem.find('a')['href']
        item_name = elem.find("h3", "prdName").text.strip()
        item_price = elem.find("b", {"class": "price"}).text.strip()
        products.append({'link': item_url, 'name': item_name,
                        'price': item_price, 'price_avg': int(item_price)})
    return products


def momo(nameList, priceList, urlList, id, name, page):
    try:
        with open("products_info_momo.json") as file:
            products_info = json.load(file)
            try:
                products = products_info[id]["products"]
            except:
                products = []
                products_info[id]["products"] = products
    except:
        products = []
        products_info = {id: {"name": name, "products": products}}
    if products_info[id]["name"] != name:
        products = []
        products_info = {id: {"name": name, "products": products}}
    pages = ((page - 1) * limit) // 20 + 1
    if (page == 1 and products == []) or len(products) < page * limit:
        products += momo_search(name, pages)
    with open("products_info_momo.json", "w") as file:
        json.dump(products_info, file)
    for i in range(limit*(page-1), limit*page):
        nameList.append(products[i]["name"])
        priceList.append(products[i]["price"])
        urlList.append(products[i]["link"])


# Shopee線上購物 爬蟲
def shopee_search(name, page, order="desc", by="relevancy"):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68',
        'x-api-source': 'pc',
        'referer': f'https://shopee.tw/search?keyword={urllib.parse.quote(name)}'
    }
    url = f'https://shopee.tw/api/v2/search_items/?by={by}&keyword={name}&limit=20&newest={20*(page-1)}&order={order}&page_type=search&version=2'
    resq = requests.Session().get(url, headers=headers)
    if resq.status_code == requests.codes.ok:
        data = resq.json()
    products = []
    for item in data["items"]:
        title = item["name"]
        shopid, itemid = item["shopid"], item["itemid"]
        title_fix = title.replace(" ", "-")
        link = f"https://shopee.tw/{title_fix}-i.{shopid}.{itemid}"
        price_min, price_max = int(
            item["price_min"])//100000, int(item["price_max"])//100000
        if price_min == price_max:
            price = str(int(item["price"] // 100000))
        else:
            price = f"{price_min} ~ {price_max}"
        products.append({"link": link, "name": title, "price": price})
        if by == "price":
            price_avg = round((price_max+price_min) / 2) if "~" in price else int(price)
            products[-1]["price_avg"] = price_avg
    return products


def shopee(nameList, priceList, urlList, id, name, page):
    try:
        with open("products_info_shopee.json") as file:
            products_info = json.load(file)
            try:
                products = products_info[id]["products"]
            except:
                products = []
                products_info[id]["products"] = products
    except:
        products = []
        products_info = {id: {"name": name, "products": products}}
    if products_info[id]["name"] != name:
        products = []
        products_info = {id: {"name": name, "products": products}}
    pages = ((page - 1) * limit) // 20 + 1
    if (page == 1 and products == []) or len(products) < page * limit:
        products += shopee_search(name, pages)
    with open("products_info_shopee.json", "w") as file:
        json.dump(products_info, file)
    for i in range(limit*(page-1), limit*page):
        nameList.append(products[i]["name"])
        priceList.append(products[i]["price"])
        urlList.append(products[i]["link"])


def price(nameList, priceList, urlList, id, name, page, sort):
    pc = {"lth": "價錢由低至高", "htl": "價錢由高至低"}
    mo = {"lth": 2, "htl": 3}
    sh = {"lth": "asc", "htl": "desc"}
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
    pages = ((page - 1) * limit) // 20 + 1
    if (page == 1 and products == []) or len(products) < page * limit:
        products += pchome_search(name, pages, pc[sort])
        products += momo_search(name, pages, mo[sort])
        products += shopee_search(name, pages, sh[sort], "price")
    products = sorted(products, key=lambda d: d["price_avg"])
    if sort == "htl":
        products.reverse()
    with open("products_info_price.json", "w") as file:
        json.dump(products_info, file)
    for i in range(limit*(page-1), limit*page):
        urlList.append(products[i]["link"])
        if "pchome" in products[i]["link"]:
            name = "〈PChome〉" + products[i]["name"]
            nameList.append(name)
        else:
            name = "〈Shopee〉" + products[i]["name"]
            nameList.append(name)
        priceList.append(products[i]["price"])


def search(id, info, page=1):
    nameList = []
    priceList = []
    urlList = []
    if info["platform"][:6] == "pchome":
        pchome(nameList, priceList, urlList, id, info["search_name"], page)
        return bubble_reload(nameList, priceList, urlList, info["platform"])
    elif info["platform"] == "momo":
        momo(nameList, priceList, urlList, id, info["search_name"], page)
        return bubble_reload(nameList, priceList, urlList, info["platform"])
    elif info["platform"] in ("shopee", "蝦皮"):
        shopee(nameList, priceList, urlList, id, info["search_name"], page)
        return bubble_reload(nameList, priceList, urlList, info["platform"])
    elif info["platform"] == "price1":
        price(nameList, priceList, urlList, id, info["search_name"], page, "lth")
        return bubble_reload(nameList, priceList, urlList, "價錢由低至高")
    elif info["platform"] == "price2":
        price(nameList, priceList, urlList, id, info["search_name"], page, "htl")
        return bubble_reload(nameList, priceList, urlList, "價錢由高至低")
    else:
        return Except
        # """無法搜尋到商品，請確認輸入是否有誤～"""



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
        message = "mode off"
    elif text == "mode on" and id == id_developer:
        info["mode_off"] = False
        message = "mode on"
    else:
        message = Except
    with open("search_info.json", "w") as file:
        json.dump(info, file)
    if message in (Help, Except, "mode on", "mode off"):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = message))
    else:
        interface = FlexSendMessage(alt_text='func2', contents = message)
        line_bot_api.reply_message(event.reply_token, interface)
    end = time.time()
    print("time:", end - start, "s")

if __name__ == "__main__":
    app.run()
