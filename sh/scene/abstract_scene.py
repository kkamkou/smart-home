from abc import ABC, abstractmethod
from types import MappingProxyType

from lib import RestApi


class AbstractScene(ABC):
    def __init__(self, api: RestApi, params: MappingProxyType, event: MappingProxyType):
        self.__params = params
        self.__event = event
        self.__api = api

    @property
    def params(self):
        return self.__params

    @property
    def event(self):
        return self.__event

    def _api(self):
        return self.__api

    @classmethod
    @abstractmethod
    def run(cls):
        raise NotImplementedError('Re-define this method')
