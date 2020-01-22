from typing import List, Dict, Any

from spine_json_lib.data.data_types.base_type import SpineData


class DrawOrderTimelineOffset(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {"slot": "", "offset": 0}
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES

    def __init__(self, values=None):
        values = values or {}

        self.slot: str = values.get("slot")
        self.offset: int = values.get("offset")

        super(DrawOrderTimelineOffset, self).__init__(values)


class DrawOrderTimeline(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {"offset": []}
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = {"time": 0, "offset": []}

    def __init__(self, values=None):
        values = values or {}

        self.time: float = values.get("time", 0)
        self.offsets: List[DrawOrderTimelineOffset] = [
            DrawOrderTimelineOffset(v) for v in values.get("offsets", [])
        ]

        super(DrawOrderTimeline, self).__init__(values)

    def remove_offsets_with_ids(self, slots_ids):
        self.offsets = [
            offset for offset in self.offsets if offset.slot not in slots_ids
        ]
