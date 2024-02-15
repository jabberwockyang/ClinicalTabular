from __future__ import annotations
import requests
import random
import json
from hashlib import md5


class BaiduTranslate():
    def __init__(self,appid = '20231129001895209',appkey = 'kmNIq_DDrfNNWwXlG7CU',from_lang = 'zh',to_lang = 'en'):
        # Set your own appid/appkey.
        self.appid =  appid
        self.appkey = appkey
        # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
        self.from_lang = from_lang
        self.to_lang =  to_lang
    def translator(self, query):
        endpoint = 'http://api.fanyi.baidu.com'
        path = '/api/trans/vip/translate'
        url = endpoint + path
        # Generate salt and sign
        def make_md5(s, encoding='utf-8'):
            return md5(s.encode(encoding)).hexdigest()

        salt = random.randint(32768, 65536)
        sign = make_md5(self.appid + query + str(salt) + self.appkey)

        # Build request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': self.appid, 'q': query, 'from': self.from_lang, 'to': self.to_lang, 'salt': salt, 'sign': sign}

        # Send request
        r = requests.post(url, params=payload, headers=headers)
        result = r.json() 
        text = [item['dst'] for item in result['trans_result']]
        text = ' '.join(text)

        return text
if __name__=='__main__':
    bt = BaiduTranslate(from_lang = 'zh',to_lang ='en')
    bt.translator('你好')