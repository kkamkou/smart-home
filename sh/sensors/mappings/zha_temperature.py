from datetime import datetime
from typing import Any

from .sensor_interface import SensorInterface


class ZhaTemperature(SensorInterface):
    __obj = {}

    def __new__(cls, obj: dict) -> Any:
        cls.__obj = obj
        return super().__new__(cls)

    def id(self) -> str:
        return self.__obj['uniqueid']

    def value(self) -> float:
        return self.__obj['state']['temperature'] / 100

    def timestamp(self):
        return datetime.fromisoformat(self.__obj['state']['lastupdated'])

    def type(self) -> str:
        return self.__obj['type']
