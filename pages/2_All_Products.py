import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from dotenv import load_dotenv
import os
import requests
load_dotenv()

x_deployment_id = os.getenv('X_DEPLOYMENT_ID')
userid = os.getenv('USERID')
passwd = os.getenv('PASSWD')
hostname = os.getenv('DB_HOSTNAME')
api = "/dbapi/v4/"
host = 'https://' + hostname + api
service = 'auth/tokens'
def get_token():
    userinfo = {"userid": userid, "password": passwd}
    headers1 = {
        'content-type': "application/json",
        'x-deployment-id': x_deployment_id
    }
    r = requests.post(host + service, headers=headers1, json=userinfo)
    return r.json()['token']
if 'access_token' not in st.session_state:
    st.session_state.access_token = get_token()

def get_all_prod():

    auth_header = {'content-type': "application/json", "authorization": "Bearer " + st.session_state.access_token,
                   'x-deployment-id': x_deployment_id
                   }
    sql_command = {"commands": "select \"URLS\", \"ASIN\", \"IMG\", \"TITLE\" ,(select PRICE from price where price.ASIN = LIST_OF_URLS.asin order by ctime desc limit 1) from LIST_OF_URLS", "limit": 100, "separator": ";", "stop_on_error": "no"}
    service = "/sql_jobs"
    r = requests.post(host + service, headers=auth_header, json=sql_command)
    r = requests.get(host + service + '/' + r.json()['id'], headers=auth_header)
    df=pd.DataFrame(data=r.json()['results'][0]['rows'],columns=['url','asin','img','title','cprice'])
    return df
st.set_page_config("All products", "📃",layout="wide")

st.title("Amazon india price tracker")

column_configuration = {
    "asin": st.column_config.TextColumn(
        "ASIN", help="The ASIN of product", max_chars=100
    ),
    "img": st.column_config.ImageColumn("icon", help="The product's icon"),
    "url": st.column_config.LinkColumn(
        "url", help="The url of product"
    ),
"cprice": st.column_config.NumberColumn("Price (in INR)", help="The price of the product in USD", format="₹%d"),
    "title": st.column_config.TextColumn(
        "Name of product",
        help="Name of product"
        ,width=200
    ),
}
st.data_editor(
    get_all_prod(),
    column_config=column_configuration,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
)