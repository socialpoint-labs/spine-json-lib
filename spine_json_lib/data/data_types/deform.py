from typing import Dict, Any, List

from spine_json_lib.data.data_types.base_type import SpineData


class Deform(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {"vertices": [], "curve": []}
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = {
        "time": 0,
        "vertices": [],
        "curve": [],
        "offset": [],
        "c2": 0,
        "c3": 1,
        "c4": 1,
    }

    def __init__(self, values: Dict[str, Any] = None) -> None:
        values = values or {}

        self.vertices: List[float] = values.get("vertices")
        self.time: float = values.get("time")
        self.curve = values.get("curve")
        self.offset = values.get("offset")
        self.c2 = values.get("c2")
        self.c3 = values.get("c3")
        self.c4 = values.get("c4")

        super(Deform, self).__init__(values)
