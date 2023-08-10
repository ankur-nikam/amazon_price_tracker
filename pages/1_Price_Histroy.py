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
    print("ok")
    st.session_state.access_token = get_token()

def get_prod_data():
    x=st.session_state.options
    auth_header = {'content-type': "application/json", "authorization": "Bearer " + st.session_state.access_token,
                   'x-deployment-id': x_deployment_id
                   }
    sql_command = {"commands": "select * from price where asin='"+x+"'", "limit": 100, "separator": ";", "stop_on_error": "no"}
    service = "/sql_jobs"
    r = requests.post(host + service, headers=auth_header, json=sql_command)
    r = requests.get(host + service + '/' + r.json()['id'], headers=auth_header)
    df=pd.DataFrame(data=r.json()['results'][0]['rows'],columns=['asin','title','price','time'])
    st.divider()
    st.write('Product name: **'+df.iloc[0][1]+'**')

    fig = px.line(df, x="time", y="price", text="price")
    st.plotly_chart(fig, theme=None, use_container_width=True)
    print(df)


st.title("Amazon india price tracker")
if 'products' not in st.session_state:
    auth_header = {'content-type': "application/json","authorization": "Bearer " + st.session_state.access_token,
    'x-deployment-id': x_deployment_id
           }
    sql_command = {"commands": "select asin from LIST_OF_URLS", "limit": 100, "separator": ";", "stop_on_error": "no"}
    service = "/sql_jobs"
    r = requests.post(host + service, headers=auth_header, json=sql_command)
    r = requests.get(host + service+'/'+r.json()['id'], headers=auth_header)
    st.session_state.products=[x[0] for x in r.json()['results'][0]['rows']]

st.session_state.options = st.selectbox('Select product by ASIN. you can find ASIN from ALL product page',
    options=["<select product>"]+st.session_state.products
    )

if st.button('show'):
    get_prod_data()
