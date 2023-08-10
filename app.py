import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os
import streamlit_extras
import streamlit as st
import requests as rq
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
import re
import datetime
from streamlit_extras.badges import badge
from streamlit_extras.function_explorer import function_explorer
from streamlit_extras.mention import mention
from streamlit_extras.switch_page_button import switch_page
load_dotenv()
x_deployment_id = os.getenv('X_DEPLOYMENT_ID')
userid = os.getenv('USERID')
passwd = os.getenv('PASSWD')
hostname = os.getenv('HOSTNAME')
api = "/dbapi/v4/"
host = 'https://' + hostname + api
service = 'auth/tokens'
def get_token():
    userinfo = {"userid": userid, "password": passwd}
    headers1 = {
        'content-type': "application/json",
        'x-deployment-id': x_deployment_id
    }
    r = rq.post(host + service, headers=headers1, json=userinfo)
    return r.json()['token']
if 'access_token' not in st.session_state:
    st.session_state.access_token = get_token()
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
        if soup.find('input',{'id':'ASIN'}) is not None:
            asin=soup.find('input',{'id':'ASIN'}).get('value')
        else:
            asin = soup.find('input', {'id': 'asin'}).get('value')
        title=soup.find('span',{'id':'productTitle'}).text.strip()
        if soup.find('img',{'id':'landingImage'}) is not None:
            img_url=soup.find('img',{'id':'landingImage'}).get('src')
        return asin,img_url,title
    except Exception as e:
        print("url not working error  {}".format(e))
st.set_page_config(page_title='home')
st.title("Amazon india price tracker")
st.write("""
This app is built using python
streamlit was used for frontend

database used is db2 cloud instance

A python process runs every hour to scrap prices for all urls in db
""")
url = st.text_input('Paste url of product you want to track', '')
if st.button('Track price'):
    try:
        if 'http' not in url:
            raise Exception()
        asin,img_url,title, = get_data(url)
        if asin is None or title is None:
            raise Exception()
        auth_header = {'content-type': "application/json", "authorization": "Bearer " + st.session_state.access_token,
                       'x-deployment-id': x_deployment_id
                       }
        sql_command = {"commands": "INSERT INTO LIST_OF_URLS (\"URLS\",\"ASIN\",\"IMG\",\"TITLE\") \
        VALUES('"+url+"','"+asin+"','"+img_url+"','"+title+"')", "limit": 100, "separator": ";",
                       "stop_on_error": "no"}
        service = "/sql_jobs"
        r = rq.post(host + service, headers=auth_header, json=sql_command)
        r = rq.get(host + service + '/' + r.json()['id'], headers=auth_header)
        if 'error' in r.json()["results"][0]:
            raise Exception()
        st.success(title+' Added to tracker', icon="✅")
    except:
        st.error("could not add this url to tracker please make secure url is correct")
