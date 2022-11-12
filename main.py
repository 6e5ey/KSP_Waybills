from dotenv import load_dotenv
import requests
import zipfile
import shutil
import json
import os

# environmental variables
load_dotenv()
DATA_MERCHANT_LOGIN = json.loads(os.getenv("DATA_MERCHANT_LOGIN"))  # dotenv stores in a string, so json.loads()
BOT_TOKEN_DAILY_REPORT = os.getenv("BOT_TOKEN_DAILY_REPORT")        # DailyReportMNS
BOT_CHAT_ID_YA = os.getenv("BOT_CHAT_ID_YA")                        # ЧАТ Я

####################    SEND WAYBILLS.zip to Telegram chat
def send_telegram_waybills():
        files = {"document": open(f"WAYBILLS/{file}", "rb")}
        send_file = 'https://api.telegram.org/bot' + BOT_TOKEN_DAILY_REPORT + '/sendDocument?chat_id=' + BOT_CHAT_ID_YA
        requests.post(send_file, files=files)




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

response_active_orders = requests.get('https://kaspi.kz/merchantcabinet/api/order/downloadWaybills', headers=headers_waybills,
                                       params=params_waybills, cookies=cookies_merchant)

with open('WAYBILLS.zip', 'wb') as f:
    f.write(response_active_orders.content)

###################    EXTRACTING the files FROM the .ZIP
try:
    if zipfile.is_zipfile('WAYBILLS.zip'):
        with zipfile.ZipFile('WAYBILLS.zip', 'r') as archive:
            archive.extractall("WAYBILLS")          # extract to folder
except:
    print("Not a valid zip file...")

files = os.listdir("WAYBILLS")
###################    CHECKING and SENDING, if NOT SENT
if os.path.exists("order_ids_sent.json"):
    with open("order_ids_sent.json", 'r') as oi:    # READING order_ids SENT to TG
        order_ids_sent_json = json.load(oi)

    ###################    READING filenames and sending to TG if NOT in the SENT list
    for file in files:
        order_id = file.split("_")[1]               # GETTING order_id from the file name

        if order_id in order_ids_sent_json:         # if already sent - skip
            continue

        send_telegram_waybills()
        order_ids_sent_json.append(order_id)        # APPEND UNSENT order_ids to a SENT ones

    with open("order_ids_sent.json", 'w') as oi:    # SAVING UNSENT that became SENT
        json.dump(order_ids_sent_json, oi, indent=2)

else:
    ###################    READING filenames and sending to TG if NOT in the SENT list
    order_ids_sent_json = []
    for file in files:
        order_id = file.split("_")[1]               # GETTING order_id from the file name
        send_telegram_waybills()
        order_ids_sent_json.append(order_id)        # APPEND UNSENT order_ids to a SENT ones

    with open("order_ids_sent.json", 'w') as oi:    # SAVING UNSENT that became SENT
        json.dump(order_ids_sent_json, oi, indent=2)


###################    CLEANING UP
os.remove("WAYBILLS.zip")
shutil.rmtree('WAYBILLS')


# ###################    GET ALL active ORDERS INFO - SHIPPED and UNSHIPPED
# headers_active_orders = {
#     'Accept': 'application/json, text/plain, */*',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Cache-Control': 'no-cache',
#     'Connection': 'keep-alive',
#     'Pragma': 'no-cache',
#     'Referer': 'https://kaspi.kz/mc/',
#     'Sec-Fetch-Dest': 'empty',
#     'Sec-Fetch-Mode': 'cors',
#     'Sec-Fetch-Site': 'same-origin',
#     'Sec-GPC': '1',
#     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
#     'x-source': 'v2',
# }
# params_active_orders = (                              # get orders from 11.11.22
#     ('orderStatus', 'null'),
#     ('searchTerm', ''),
#     ('cityId', 'undefined'),
#     ('filterFromDate', '11.11.2022'),
#     ('filterToDate', 'Invalid date'),
#     ('orderTab', 'KASPI_DELIVERY_TRANSMITTED'),
# )
#
# response_active_orders = requests.get('https://kaspi.kz/merchantcabinet/api/order/exportToExcel',
#                                         headers=headers_active_orders, params=params_active_orders,
#                                         cookies=cookies_merchant)
# with open('ACTIVE ORDERS.xlsx', 'wb') as zkz:
#     zkz.write(response_active_orders.content)
#
#
#
#
#
# ###################    GET ALL archive ORDERS INFO
# params_archive_orders = (
#     ('orderStatus', 'null'),
#     ('searchTerm', ''),
#     ('cityId', 'undefined'),
#     ('filterFromDate', '11.11.2022'),
#     ('filterToDate', 'Invalid date'),
#     ('orderTab', 'ARCHIVE'),
# )
#
# response_archive_orders = requests.get('https://kaspi.kz/merchantcabinet/api/order/exportToExcel',
#                                        headers=headers_active_orders, params=params_archive_orders,
#                                        cookies=cookies_merchant)
#
# with open('ARCHIVE ORDERS.xlsx', 'wb') as zkz:
#     zkz.write(response_archive_orders.content)


###################    (2) GET ALL active ORDERS INFO - SHIPPED and UNSHIPPED
headers_orders_to_excel = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
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
def orders_to_excel(order_tab, filename):
    params_orders_to_excel = (
        ('orderStatus', 'null'),
        ('searchTerm', ''),
        ('cityId', 'undefined'),
        ('filterFromDate', '11.11.2022'),
        ('filterToDate', 'Invalid date'),
        ('orderTab', order_tab),
    )
    response_orders_to_excel = requests.get('https://kaspi.kz/merchantcabinet/api/order/exportToExcel',
                                           headers=headers_orders_to_excel, params=params_orders_to_excel,
                                           cookies=cookies_merchant)
    with open(filename, 'wb') as zkz:
        zkz.write(response_orders_to_excel.content)


orders_to_excel('KASPI_DELIVERY_TRANSMITTED', "ACTIVE orders.xlsx")
orders_to_excel('ARCHIVE', "ARCHIVE orders.xlsx")
