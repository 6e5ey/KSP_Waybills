import requests
from dotenv import load_dotenv
import json
import os
import zipfile

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


###################    EXTRACTING the files FROM the .ZIP
try:
    if zipfile.is_zipfile('WAYBILLS.zip'):
        with zipfile.ZipFile('WAYBILLS.zip', 'r') as archive:
            archive.extractall("WAYBILLS")                      # extract to folder
except:
    print("Not a valid zip file...")

###################    CHECKING orders already sent to TG
try:
    with open("order_ids_sent.json", 'r') as oi:                # READING order_ids SENT to TG
        order_ids_sent_json = json.load(oi)
except:
    print("order_ids_sent.json is not found. But MOVING ON...")

###################    READING filenames and sending to TG if NOT in the SENT list
order_ids_unsent = []
files = os.listdir("WAYBILLS")

for file in files:
    order_id = file.split("_")[1]                               # GETTING order_id from the file name
    try:
        if order_id in order_ids_sent_json:                     # if already sent - skip
            continue
    except:
        print("order_ids_sent.json is not found once again. But MOVING ON...")

    order_ids_unsent.append(order_id)                           # UNSENT order_ids to a list

    ####################    SEND WAYBILLS.zip to Telegram chat
    files = {"document": open(f"WAYBILLS/{file}", "rb")}
    send_file = 'https://api.telegram.org/bot' + BOT_TOKEN_DAILY_REPORT + '/sendDocument?chat_id=' + BOT_CHAT_ID_YA
    requests.post(send_file, files=files)

with open("order_ids_sent.json", 'w') as oi:                    # SAVING UNSENT that became SENT
    json.dump(order_ids_unsent, oi, indent=2)









