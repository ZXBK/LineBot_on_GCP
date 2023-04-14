#當前版本
import json
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import requests
from bs4 import BeautifulSoup 
import re
def craw_PTTmobilesales_gdLink(pages,msg):
  request_url = "https://www.ptt.cc/bbs/mobilesales/index.html"
  cookies = {"cookie": "over18=1"} 
  gdLink = []
  for i in range(pages): 
      r = requests.get(request_url,headers = cookies)
      soup = BeautifulSoup(r.text,"html.parser")
      gd_title = soup.select("div.title a")
      url_title = soup.select("div.btn-group.btn-group-paging a")
      request_url = "https://www.ptt.cc"+ url_title[1]["href"] #上一頁的網址
      for gd in gd_title: #找出含有文字的url並儲存到gd_link
        if "賣" in str(gd) and str(msg).lower() in str(gd).lower() :
          gdLink.append(gd["href"])  
  return gdLink
def craw_mobilesales_price(pages,msg):
  cookies = {"cookie": "over18=1"}
  price_list = []
  gdLink = craw_PTTmobilesales_gdLink(pages,msg)
  for gd in gdLink:
    r = requests.get("https://www.ptt.cc"+gd , headers = cookies)
    soup = BeautifulSoup(r.text,"html.parser")
    main_cont = soup.find(id="main-container")
    all_text = main_cont.text
    contents = all_text.split('--')[0]

    good_name = re.compile(r'物品：(.*)物品',re.DOTALL).search(contents) ##re.DOTALL為了讓"."這個regex也能包含"\n"
    if good_name:
      good = good_name.group(1)
      price_list.append("➜ ➜ ➜商品名稱:\n"+good)
    else:
      print('Error!! Did not get goods name')
      print(contents)
      price_list.append("➜ ➜ ➜商品名稱: 窩抓不到QQ\n")

    price_name = re.compile(r'售價格：(.*)交易方式',re.DOTALL).search(contents)
    if price_name:
      price_name = price_name.group(1)
      price_list.append("售價:\n"+price_name)
    else:
      print('Error!! Did not get price name')
      print(contents)
      price_list.append("售價: 窩抓不到QQ \n")
    price_list.append("https://www.ptt.cc"+gd+'\n')
  return price_list
def linebot(request):
    try:
        body = request.get_data(as_text=True)                # 取得收到的訊息內容
        json_data = json.loads(body)                         # json 格式化訊息內容
        access_token = 'user_access'
        secret = 'user_secret'
        line_bot_api = LineBotApi(access_token)              # 確認 token 是否正確
        handler = WebhookHandler(secret)                     # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        #為了：驗證訊息來源(http post訊息若來自LINE，一定會有X-Line-Signature此數位簽章),channel secret 作為密鑰
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        #為了：確認signature與token,secret
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        txt_type = json_data['events'][0]['message']['type']     # 取得 LINe 收到的訊息類型
        if txt_type=='text': 
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
            print("Messange from LINE: ",msg)
            if craw_PTTmobilesales_gdLink(5,msg):  #若關鍵字找的到
              price_list = craw_mobilesales_price(5,msg)
            else:
              price_list = "Not Found"
            reply = msg
        else:
            reply = "Input must be text"
        print("輸入：",reply)
        line_bot_api.reply_message(tk,TextSendMessage(''.join(price_list)))# 回傳訊息
    except:
        print("try was wrong!! "+request.args)               # 如果發生錯誤，印出收到的內容
    return 'OK'                                              # 驗證 Webhook 使用，不能省略
