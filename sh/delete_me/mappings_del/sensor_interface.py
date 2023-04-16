from datetime import datetime
from typing import Any


class SensorInterface:
    def id(self) -> str:
        pass

    def value(self) -> Any:
        pass

    def timestamp(self) -> datetime:
        pass

    def type(self) -> str:
        pass
