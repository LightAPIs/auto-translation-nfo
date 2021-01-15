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

    def caiyun_token(self):
        return self.conf.get("api", "caiyun_token")

    @staticmethod
    def _default_config():
        conf = configparser.ConfigParser()

        sec1 = "api"
        conf.add_section(sec1)
        conf.set(sec1, "caiyun_token", "")

        return conf
