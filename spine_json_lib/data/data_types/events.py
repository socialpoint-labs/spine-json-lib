from typing import Dict, Any

from spine_json_lib.data.data_types.base_type import SpineData


class Events(SpineData):
    DEFAULT_VALUES = {"int": 0, "float": 0, "string": ""}
    SPINE_3_8_DEFAULT_VALUES = DEFAULT_VALUES

    def __init__(self, values: Dict[str, Any] = None) -> None:
        values = values or {}

        self.int = values.get("int")
        self.float = values.get("float")
        self.string = values.get("string")

        super(Events, self).__init__(values)


class EventTimeline(SpineData):
    DEFAULT_VALUES = {"name": "", "int": 0, "float": 0, "string": ""}
    SPINE_3_8_DEFAULT_VALUES = {
        "time": 0,
        "name": "",
        "int": 0,
        "float": 0,
        "string": "",
        "audio": "",
        "volume": 1,
        "balance": 0,
    }

    def __init__(self, values=None):
        values = values or {}

        self.time: float = values.get("time")
        self.name: str = values.get("name")
        self.int: int = values.get("int")
        self.float: float = values.get("float")
        self.string: str = values.get("string")
        self.audio: str = values.get("audio")
        self.volume: int = values.get("volume")
        self.balance: int = values.get("balance")

        super(EventTimeline, self).__init__(values)
