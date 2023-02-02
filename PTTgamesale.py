import json
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import requests
from bs4 import BeautifulSoup 
import re
def linebot(request):
    try:
        body = request.get_data(as_text=True)
        json_data = json.loads(body)
        access_token = 'from line developers'
        secret = 'from line developers'
        line_bot_api = LineBotApi(access_token)
        handler = WebhookHandler(secret)
        signature = request.headers['X-Line-Signature']   #to verify text send from line
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']
        type = json_data['events'][0]['message']['type']

        if type=='text':
            msg = json_data['events'][0]['message']['text']   # text from line
            print(msg)
            request_url = "https://www.ptt.cc/bbs/Gamesale/index.html"
            cookies = {"cookie": "over18=1"} 
            gd_link = []
            for i in range(10):   #browse 10 pages once
                r = requests.get(request_url,headers = cookies)
                soup = BeautifulSoup(r.text,"html.parser")
                gd_title = soup.select("div.title a")
                url_title = soup.select("div.btn-group.btn-group-paging a")
                request_url = "https://www.ptt.cc"+ url_title[1]["href"] #previous page
                for s in gd_title:    #grab title included keywords and store into gd_title
                    if str(s).find("NS") != -1 and str(s).find("售") != -1 and str(s).find(msg) != -1 : ## <------key words
                        gd_link.append(s["href"])


            cookies = {"cookie": "over18=1"} 
            price_list = []
            for i in gd_link:   #all weblinks from goods
                r = requests.get("https://www.ptt.cc"+i , headers = cookies)
                soup = BeautifulSoup(r.text,"html.parser")
                main_cont = soup.find(id="main-container")
                all_text = main_cont.text
                aa = all_text.split('--')[0]
                aa = aa.split('\n')
                contents = aa[2:]
                print(contents)
                for s in contents: 
                    if str(s).find(msg) != -1:
                        price_list.append(s)
                    if s.find("售") != -1:
                        # price = re.findall(r'\d+',s)
                        # price_list.append(int(price[0]))
                        price_list.append(s)

            reply = msg
        else:
            reply = "Input must be text"
        # print(reply)
        line_bot_api.reply_message(tk,TextSendMessage('\n'.join(price_list)))
    except:
        print("try was wrong!!")
        print(request.args)                                          
    return 'OK'  

# if __name__ == "__main__":
#     app.run(port=5003)
