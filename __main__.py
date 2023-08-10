# This is a sample Python script.

import datetime
import re
import os
import requests
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests as rq
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent

x_deployment_id = os.getenv('X_DEPLOYMENT_ID')
userid = os.getenv('USERID')
passwd = os.getenv('PASSWD')
hostname = os.getenv('DB_HOSTNAME')
def get_soup_retry(url):
    ua = UserAgent()
    uag_random = ua.random

    header = {
        'User-Agent': uag_random,
        'Accept-Language': 'en-US,en;q=0.9'
    }
    isCaptcha = True
    while isCaptcha:
        page = rq.get(url, headers=header)
        assert page.status_code == 200
        soup = bs(page.content, 'html5lib')
        if 'captcha' in str(soup):
            uag_random = ua.random
            print(f'\rBot has been detected... retrying ... use new identity: {uag_random} ', end='', flush=True)
            continue
        else:
            print('Bot bypassed')
            return soup

def get_data( url: str):
    try:

        soup=get_soup_retry(url)
        if soup.find(class_='a-price-whole') is not None:
            price=soup.find(class_='a-price-whole').text
        else:
            price=soup.find(class_='a-size-medium a-color-price').text
        price_clean=price.replace(',','')
        price_clean=re.sub('[^0-9\.]','',price_clean)
        #price_clean = price_clean.replace('.', '')
        print(price_clean)
        if soup.find('input',{'id':'ASIN'}) is not None:
            asin=soup.find('input',{'id':'ASIN'}).get('value')
        else:
            asin = soup.find('input', {'id': 'asin'}).get('value')
        print(asin)
        title=soup.find('span',{'id':'productTitle'}).text.strip()
        print(title)
        print(datetime.datetime.utcnow())
        return asin,title , price_clean, datetime.datetime.utcnow()
    except Exception as e:
        print("url not working error  {}".format(e))


def save_data(url,access_token):
    asin , title,price,ctime=get_data(url)


    api = "/dbapi/v4/"
    host = 'https://'+hostname+ api
    userinfo = {"userid":userid,"password":passwd}

    auth_header = {'content-type': "application/json","authorization": "Bearer " + access_token,
    'x-deployment-id': x_deployment_id
           }
    sql = "insert into PRICE values('{}','{}',{},'{}')".format(asin,title,price,ctime)
    sql_command = {"commands": sql, "limit": 100, "separator": ";", "stop_on_error": "no"}
    service = "/sql_jobs"
    r = requests.post(host + service, headers=auth_header, json=sql_command)
    r = requests.get(host + service+'/'+r.json()['id'], headers=auth_header)
    print(r.json())

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    api = "/dbapi/v4/"
    host = 'https://'+hostname+ api
    userinfo = {"userid":userid,"password":passwd}
    service = 'auth/tokens'
    headers1 = {
        'content-type': "application/json",
        'x-deployment-id': x_deployment_id
    }
    r = requests.post(host + service,headers=headers1, json=userinfo)
    print(r.text)
    access_token = r.json()['token']
    auth_header = {'content-type': "application/json","authorization": "Bearer " + access_token,
    'x-deployment-id': x_deployment_id
           }
    sql_command = {"commands": "select urls from LIST_OF_URLS", "limit": 100, "separator": ";", "stop_on_error": "no"}
    service = "/sql_jobs"
    r = requests.post(host + service, headers=auth_header, json=sql_command)
    r = requests.get(host + service+'/'+r.json()['id'], headers=auth_header)
    urls=r.json()['results'][0]['rows']
    for url in urls:
        try:
            save_data(url[0],access_token)
        except Exception as e:
            print(e)


