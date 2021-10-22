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
id_developer = "Ud88738728f539076c18e761ae8ce06cd"


limit = 5    # 每次傳送之商品數上限
Help = """若想在 pchome/momo/shopee 搜尋商品
請傳：  商品名稱;平台 (大小寫、全半型皆可)
ex:  PS5;pchome 、 滑鼠；MOMO
要看下一頁則輸入2 3 4 5.... (請不要跳頁)

*注意*
pchome回傳時間約1~3秒
shopee回傳時間約3~5秒
momo回傳時間約10~15秒 (可悲慢

若是需要查詢使用方式則輸入help即可
祝泥使用愉快～"""
mode_off = """機器人目前測試中
請稍後再使用"""
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
class PchomeSpider():
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'}

    # 送出 GET 請求
    def request_get(self, url, params=None, to_json=True):
        # param url: 請求網址
        # param params: 傳遞參數資料
        # param to_json: 是否要轉為 JSON 格式
        # return data: requests 回應資料
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
        # param keyword: 搜尋關鍵字
        # param max_page: 抓取最大頁數
        # param shop: 賣場類別 (全部、24h購物、24h書店、廠商出貨、PChome旅遊)
        # param sort: 商品排序 (有貨優先、精準度、價錢由高至低、價錢由低至高、新上市)
        # param price_min: 篩選"最低價" (需與 price_max 同時用)
        # param price_max: 篩選"最高價" (需與 price_min 同時用)
        # param is_store_pickup: 篩選"超商取貨"
        # param is_ipost_pickup: 篩選"i 郵箱取貨"
        # return products: 搜尋結果商品
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
        params = {'q': keyword, 'sort': all_sort[sort], 'page': 0}
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
            except:
                products = []
                products_info[id] = products
    except:
        products = []
        products_info = {id: products}
    if page == 1 and products == []:
        products = PchomeSpider().search_products(name)
    elif len(products) < page * limit:
        products = PchomeSpider().search_products(name, (page*limit)//20+1)
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
def momo_search(keyword, pages = 1):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
    urls = []
    amount = 20 // limit
    page = pages // amount + 1
    pages = pages % amount if pages % amount != 0 else 4
    if pages != 1:
        with open("urls_momo.json") as file:
            urls = json.load(file)
    else:
        url = 'https://m.momoshop.com.tw/search.momo?_advFirst=N&_advCp=N&curPage={}&searchType=1&cateLevel=2&ent=k&searchKeyword={}&_advThreeHours=N&_isFuzzy=0&_imgSH=fourCardType'.format(page, keyword)
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, features="html.parser")
            for item in soup.select('li.goodsItemLi > a'):
                urls.append('https://m.momoshop.com.tw'+item['href'])
        with open("urls_momo.json", "w") as file:
            json.dump(urls, file)
    products = []
    urls = urls[limit*(pages-1):limit*pages]
    for i, url in enumerate(urls):
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, features="html.parser")
        name = soup.find('meta',{'property':'og:title'})['content']
        try:
            price = soup.find('meta',{'property':'product:price:amount'})['content']
        except:
            price = re.sub(r'\r\n| ','',soup.find('del').text)
        products.append({
            "link": url, 
            "name": name, 
            "price": price
            })
    with open("products_info_momo.json", "w") as file:
        json.dump(products, file)
    return products
    
def momo(id, name, pages = 1):
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
    if pages == 1 and products == []:
        products = momo_search(name)
    else:
        products += momo_search(name, pages)
    with open("products_info_momo.json", "w") as file:
        json.dump(products_info, file)
    message = ""
    for i in range(limit*(pages-1), limit*pages):
        message += products[i]["link"] + "\n"
        message += products[i]["name"] + "\n"
        message += "$" + products[i]["price"] + "\n"
    message += " " * 20 + f"[第{pages}頁]"
    return message


# Shopee線上購物 爬蟲
def shopee_search(name, page = 1, order = "desc"):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68',
        'x-api-source': 'pc',
        'referer': f'https://shopee.tw/search?keyword={urllib.parse.quote(name)}'
    }
    if order == "desc":
        url = f'https://shopee.tw/api/v2/search_items/?by=relevancy&keyword={name}&limit=20&newest={50*(page-1)}&order=desc&page_type=search&version=2'
    elif order == "asc":
        url = f'https://shopee.tw/api/v2/search_items/?by=price&keyword={name}&limit=20&newest={20*(page-1)}&order=asc&page_type=search&version=2'
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
    if page == 1 and products == []:
        print("check point")
        products = shopee_search(name, 1)
    else:
        pages = page // (50 // limit) + 1
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
    if page == 1 and products == []:
        products = PchomeSpider().search_products(name, sort = "價錢由低至高")
        products += shopee_search(name, order = "asc")
    elif len(products) < page * limit:
        print("len:", len(products))
        pages = page // (20 // limit) + 1
        products += PchomeSpider().search_products(name, pages, sort = "價錢由低至高")
        products += shopee_search(name, pages, "asc")
    products = sorted(products, key = lambda d: d["price_avg"]) 
    with open("products_info_price.json", "w") as file:
        json.dump(products_info, file)
    message = ""
    for i in range(limit*(page-1), limit*page):
        message += products[i]["link"] + "\n"
        message += products[i]["name"] + "\n"
        message += "$" + str(products[i]["price"]) + "\n"
    message += " " * 20 + f"[第{page}頁]"
    return message
    

def search(id, info, page = 1):
    info["platform"] = info["platform"].lower().rstrip().strip()
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
        return """無法搜尋到商品
        請確認商品名稱或平台名稱是否有誤～"""



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
    text = event.message.text
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
        info = {"mode_off": False, id: info_id}
    if info["mode_off"]:
        message = mode_off
    elif ";" in text:
        info_id["search_name"], info_id["platform"] = text.split(";")
        message = search(id, info_id)
    elif "；" in text:
        info_id["search_name"], info_id["platform"] = text.split("；")
        message = search(id, info_id)
    elif text.isdigit() == True:
        message = search(id, info_id, int(text))
    elif text.lower().rstrip().strip()[:4] == "help":
        message = Help
    elif text == "mode:off" and id == id_developer:
        info["mode_off"] = True
        print("mode off")
        message = "mode off"
    elif text == "mode:on" and id == id_developer:
        info["mode_off"] = False
        print("mode on")
        message = "mode on"
    else:
        print(id)
        message = id
    with open("search_info.json", "w") as file:
        json.dump(info, file)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = message))
    end = time.time()
    print("time:", end - start, "s")

if __name__ == "__main__":
    app.run()
