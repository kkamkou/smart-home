from json import dumps
from typing import Any

import requests


class RestApi:
    __url = "http://localhost"
    __usr = "noname"

    def __new__(cls, url: str, usr: str) -> Any:
        cls.__url = url
        cls.__usr = usr
        return super().__new__(cls)

    def lights(self, lid: int):
        return requests.get(self.url(f'lights/{lid}')).json()

    def lights_state(self, lid: int, state: dict):
        return requests.put(self.url(f'lights/{lid}/state'), data=dumps(state)).json()

    def url(self, path):
        return '/'.join([self.__url, self.__usr, path])
