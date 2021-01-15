# -*- coding: utf-8 -*-
import requests
import json


class Caiyun:
    def __init__(self, token=""):
        self.url = "http://api.interpreter.caiyunai.com/v1/translator"
        self.token = token

    def translate(self, content):
        try:
            payload = {
                "source": [content],
                "trans_type": "ja2zh",
                "request_id": "translate_nfo",
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
