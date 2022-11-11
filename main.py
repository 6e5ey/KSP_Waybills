import requests
from dotenv import load_dotenv
import json
import os

# environmental variables
load_dotenv()
DATA_MERCHANT_LOGIN = json.loads(os.getenv("DATA_MERCHANT_LOGIN"))  # dotenv stores in a string, so json.loads()
BOT_TOKEN_DAILY_REPORT = os.getenv("BOT_TOKEN_DAILY_REPORT")        # DailyReportMNS
BOT_CHAT_ID_YA = os.getenv("BOT_CHAT_ID_YA")                        # ЧАТ Я


###################    LOGGING into MERCHANT to get cookies
headers_merchant_login = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://kaspi.kz',
    'Pragma': 'no-cache',
    'Referer': 'https://kaspi.kz/merchantcabinet/login',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Sec-GPC': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
}
session_merchant_login = requests.session()
response_merchant_login = session_merchant_login.post('https://kaspi.kz/merchantcabinet/login',
                                                      headers=headers_merchant_login,
                                                      data=DATA_MERCHANT_LOGIN)
cookies_merchant = {'kaspi.storefront.cookie.city': '750000000', 'ks.cc': '-1',
                    "X-Mc-Api-Session-Id": session_merchant_login.cookies['X-Mc-Api-Session-Id']}

###################    DOWNLOADING WAYBILLS and SAVING as WAYBILLS.zip
headers_waybills = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': 'https://kaspi.kz/mc/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-GPC': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'x-source': 'v2',
}
params_waybills = (('orderStatus', ['ACCEPTED_BY_MERCHANT', 'SUSPENDED']),
                    ('orderTab', 'KASPI_DELIVERY_WAIT_FOR_COURIER'),)

response = requests.get('https://kaspi.kz/merchantcabinet/api/order/downloadWaybills', headers=headers_waybills,
                        params=params_waybills, cookies=cookies_merchant)

with open('WAYBILLS.zip', 'wb') as f:
    f.write(response.content)



####################    SEND WAYBILLS.zip
files = {"document": open("WAYBILLS.zip", "rb")}
send_file = 'https://api.telegram.org/bot' + BOT_TOKEN_DAILY_REPORT + '/sendDocument?chat_id=' + BOT_CHAT_ID_YA
requests.post(send_file, files=files)


