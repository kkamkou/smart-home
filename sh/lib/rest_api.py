from typing import Any

import requests


class RestApi:
    __url = "http://localhost"
    __usr = "noname"

    def __new__(cls, url: str, usr: str) -> Any:
        cls.__url = url
        cls.__usr = usr
        return super().__new__(cls)

    def sensors(self):
        return requests.get(self.url("sensors")).json()

    def url(self, path):
        return "/".join([self.__url, self.__usr, path])
