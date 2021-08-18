# -*- coding: utf-8 -*-
import requests
import json


class Caiyun:
    def __init__(self, token="", trans_type=""):
        self.url = "http://api.interpreter.caiyunai.com/v1/translator"
        self.token = token
        self.trans_type = trans_type

    def translate(self, content):
        try:
            payload = {
                "source": [content],
                "trans_type": self.trans_type,
                "request_id": "translate_nfo",
                "detect": True,
            }

            headers = {
                "content-type": "application/json",
                "x-authorization": "token " + self.token,
            }

            response = requests.request("POST",
                                        self.url,
                                        data=json.dumps(payload),
                                        headers=headers)

            return json.loads(response.text)["target"][0]
        except ValueError:
            return content
