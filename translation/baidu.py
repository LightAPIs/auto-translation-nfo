# -*- coding: utf-8 -*-
import hashlib
import random
import requests
import re


class Baidu:
    def __init__(self, app_id="", key="", from_value="", to=""):
        self.url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
        self.app_id = str(app_id)
        self.key = key
        self.from_value = from_value
        self.to = to

    def translate(self, content: str):
        salt = str(random.randint(32768, 65536))
        query_str = self._convert_space(content)
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
                result = ""
                for dict in result_dict["trans_result"]:
                    result += "\n" + \
                        self._remove_space(
                            dict["dst"]) if result else self._remove_space(dict["dst"])
                return result
            else:
                return content
        except ValueError:
            return content

    @staticmethod
    def _md5(str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()

    @staticmethod
    def _remove_space(str):
        s = str.replace("+", " ")
        space_patten = re.compile(r"([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])")
        s = space_patten.sub(r"\1\2", s)
        s = space_patten.sub(r"\1\2", s)
        return s

    @staticmethod
    def _convert_space(str):
        suffix_patten = re.compile(r"([\u4e00-\u9fa5])\s+")
        s = suffix_patten.sub(r"\1+", str)
        prefix_patten = re.compile(r"\s+([\u4e00-\u9fa5])")
        s = prefix_patten.sub(r"+\1", s)
        return s
