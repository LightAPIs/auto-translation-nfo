# -*- coding: utf-8 -*-
import hashlib
import random
import requests


class Baidu:
    def __init__(self, app_id="", key="", from_value="", to=""):
        self.url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
        self.app_id = str(app_id)
        self.key = key
        self.from_value = from_value
        self.to = to

    def translate(self, content: str):
        salt = str(random.randint(32768, 65536))
        query_str = content.replace(" ", "+")
        pre_sign = self.app_id + query_str + salt + self.key
        sign = hashlib.md5(pre_sign.encode()).hexdigest()
        params = {
            "q": query_str,
            "from": self.from_value,
            "to": self.to,
            "appid": self.app_id,
            "salt": salt,
            "sign": sign
        }

        try:
            reponse = requests.get(self.url, params=params)
            result_dict = reponse.json()
            if "trans_result" in result_dict:
                return (result_dict["trans_result"][0]["dst"]).replace(
                    "+", " ")
            else:
                return content
        except ValueError:
            return content

    @staticmethod
    def _md5(str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
