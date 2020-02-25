from typing import Dict, Any, List

from spine_json_lib.data.data_types.base_type import SpineData


class Ik(SpineData):
    DEFAULT_VALUES = {
        "name": "",
        "order": 0,
        "bones": [],
        "target": "",
        "bendPositive": True,
        "softness": 0,
        "compress": False,
        "stretch": False,
        "uniform": False,
    }
    SPINE_3_8_DEFAULT_VALUES = DEFAULT_VALUES

    def __init__(self, values: Dict[str, Any] = None) -> None:
        values = values if values is not None else {}

        self.name = values.get("name")
        self.order = values.get("order")
        self.bones = values.get("bones")
        self.target = values.get("target")
        self.mix = values.get("mix")
        self.bendPositive = values.get("bendPositive")
        self.softness = values.get("softness")
        self.compress = values.get("compress")
        self.stretch = values.get("stretch")
        self.uniform = values.get("uniform")

        super(Ik, self).__init__(values)


class IkTimeline(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {"bendPositive": True, "curve": []}
    UNSUPPORTED_VALUES_OLD_VERSION: List[str] = ["c2", "c3", "c4"]

    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = {
        "time": 0,
        "bendPositive": True,
        "stretch": False,
        "curve": [],
        "c2": 0,
        "c3": 1,
        "c4": 1,
    }

    def __init__(self, values=None):
        values = values or {}

        self.time: float = values.get("time")
        self.mix: float = values.get("mix")
        self.bendPositive: bool = values.get("bendPositive")
        self.curve: List[float] = values.get("curve")
        self.c2 = values.get("c2")
        self.c3 = values.get("c3")
        self.c4 = values.get("c4")
        self.stretch = values.get("stretch")

        super(IkTimeline, self).__init__(values)
