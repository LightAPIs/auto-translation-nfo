# -*- coding: utf-8 -*-
import os
import json


class Tag:
    def __init__(self, path="tag.json"):
        if os.path.exists(path):
            with open(path, encoding="utf-8") as load_f:
                self.data = json.load(load_f)
        else:
            self.data = {"replace": [], "delete": []}

    def handler(self):
        return self.data
