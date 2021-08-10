# -*- coding: utf-8 -*-
import os
import configparser


class Config:
    def __init__(self, path="config.ini"):
        if os.path.exists(path):
            self.conf = configparser.ConfigParser()
            try:
                self.conf.read(path, encoding="utf-8-sig")
            except Exception:
                self.conf.read(path, encoding="utf-8")
        else:
            self.conf = self._default_config()

    def engine_type(self):
        return self.conf.get("engine", "type")

    def caiyun_token(self):
        return self.conf.get("caiyun", "token")

    def caiyun_trans_type(self):
        return self.conf.get("caiyun", "trans_type")

    def baidu_app_id(self):
        return self.conf.get("baidu", "app_id")

    def baidu_key(self):
        return self.conf.get("baidu", "key")

    def baidu_from(self):
        return self.conf.get("baidu", "from")

    def baidu_to(self):
        return self.conf.get("baidu", "to")

    @staticmethod
    def _default_config():
        conf = configparser.ConfigParser()

        sec1 = "engine"
        conf.add_section(sec1)
        conf.set(sec1, "type", "baidu")

        sec2 = "caiyun"
        conf.add_section(sec2)
        conf.set(sec2, "token", "")
        conf.set(sec2, "trans_type", "auto2zh")

        sec3 = "baidu"
        conf.add_section(sec3)
        conf.set(sec3, "app_id", "")
        conf.set(sec3, "key", "")
        conf.set(sec3, "from", "auto")
        conf.set(sec3, "to", "zh")

        return conf
