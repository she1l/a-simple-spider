#!/usr/bin/env python
# utf-8

import requests
requests.packages.urllib3.disable_warnings()
import redis
import json
import time
import sys

username = 'user001'
password = 'pass123456789'

redis_host = '127.0.0.1'
redis_pass = '123456'
redis_db = 15
redis_port = 6379


def login():
    login_url = 'https://open-api.dianba6.com/api/v1/member/login'

    header = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,fr;q=0.7,zh-TW;q=0.6,lb;q=0.5,ca;q=0.4,mt;q=0.3,pt;q=0.2,sv;q=0.1,la;q=0.1,sm;q=0.1,ceb;q=0.1',
        'App-Sign': 'ZXlKMlpYSnphVzl1SWpvaU1TNHdJaXdpWVhCd1gybGtJam9pTWpBd01DSXNJblJwYldVaU9qRTJORGM1TkRRMk9ESjlkYlUxTnViUHdsa3hoaHRuRmNrdWlXVFk5Nm5Yc1lvZw==',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'open-api.dianba6.com',
        'Origin': 'https://shopee.dianba6.com',
        'Referer': 'https://shopee.dianba6.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'
    }

    payload = {
        # "type": "pwd",
        "type": "child",
        "username": username,
        "password": password,
        # "country_code": "0086"
    }

    response = (requests.post(login_url, headers=header, data=payload)).json()

    if response['data'] is None:
        return None
    else:
        token = response['data']['token']
        return token


def spider():
    generalData_url = 'https://api.shopee.dianba6.com/api/analyst/hotKeyword/generalData'
    hotSaleTag_url = 'https://api.shopee.dianba6.com/api/analyst/tagWord/hotSaleTag'
    switchSite_url = 'https://api.shopee.dianba6.com/api/switchSite'

    token = login()
    if token is None:
        sys.exit('--- 获取 Token 失败')

    client = redis.Redis(host=redis_host, port=redis_port, password=redis_pass, db=redis_db, decode_responses=True)

    header = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,fr;q=0.7,zh-TW;q=0.6,lb;q=0.5,ca;q=0.4,mt;q=0.3,pt;q=0.2,sv;q=0.1,la;q=0.1,sm;q=0.1,ceb;q=0.1',
        'Authorization': token,
        'Host': 'api.shopee.dianba6.com',
        'Origin': 'https://shopee.dianba6.com',
        'Referer': 'https://shopee.dianba6.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'
    }

    site = {
        'Singapore': {'id': '1'},
        'Indonesia': {'id': '2'},
        'Taiwan': {'id': '3'},
        'Thailand': {'id': '4'},
        'Malaysia': {'id': '5'},
        'Vietnam': {'id': '6'},
        'Philippines': {'id': '7'},
        'Brasilia': {'id': '8'},
        'Mexico': {'id': '9'}
    }

    session = requests.session()
    date = time.strftime("%Y%m%d",time.localtime(time.time()))

    for area, payload in site.items():
        switchSite = session.post(switchSite_url, headers=header, data=site[area])
        switchSite_http_code = (switchSite.json())['status']
        if switchSite_http_code != 200:
            sys.exit('--- switchSite URL 错误')
        time.sleep(1)

        hotSaleTag = session.get(url=hotSaleTag_url, headers=header, verify=False)
        hotSaleTag_http_code = (hotSaleTag.json())['status']
        if hotSaleTag_http_code != 200:
            sys.exit('--- hotSaleTag URL 错误')
        hotSaleTag_data = (hotSaleTag.json())['data']['data']
        client.hset('hotSaleTag'+'-'+date, area, json.dumps(hotSaleTag_data))
        time.sleep(1)

        generalData = session.get(url=generalData_url, headers=header, verify=False)
        generalData_http_code = (generalData.json())['status']
        if generalData_http_code != 200:
            sys.exit('--- generalData URL 错误')
        generalData_data = (generalData.json())['data']['data']
        client.hset('generalData'+'-'+date, area, json.dumps(generalData_data))

    client.expire('hotSaleTag'+'-'+date, 2678400)
    client.expire('generalData'+'-'+date, 2678400)

    client.close()
    sys.exit('--- Done ---')


spider()


