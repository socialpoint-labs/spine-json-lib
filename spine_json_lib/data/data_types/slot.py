from typing import Dict, Any, List

from spine_json_lib.data.data_types.base_type import SpineData


class Slot(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {}
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES
    REQUIRED = ["name", "bone"]

    def __init__(self, values: Dict[str, Any] = None) -> None:
        values = values or {}

        self.name = values.get("name")
        self.bone = values.get("bone")
        self.attachment = values.get("attachment")
        self.color = values.get("color")
        self.dark = values.get("dark")
        self.blend = values.get("blend")

        super(Slot, self).__init__(values)


class SlotKeyframe(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {"curve": [], "name": None}
    UNSUPPORTED_VALUES_OLD_VERSION = ["c2", "c3", "c4"]

    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = {
        "curve": [],
        "name": None,
        "time": 0,
        "c2": 0,
        "c3": 1,
        "c4": 1,
    }

    def __init__(self, values=None):
        values = values or {}

        self.name: str = values.get("name")
        self.time: float = values.get("time")
        self.curve: List[float] = values.get("curve")
        self.color: str = values.get("color")
        self.dark = values.get("dark")
        self.light = values.get("light")
        self.c2 = values.get("c2")
        self.c3 = values.get("c3")
        self.c4 = values.get("c4")

        super(SlotKeyframe, self).__init__(values)

    def is_empty(self):
        return self.name == "None" or self.name is None


class SlotTimeline(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {
        "attachment": [],
        "color": [],
        "twoColor": [],
    }
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES

    def __init__(self, values=None):
        values = values or {}

        self.attachment: List[SlotKeyframe] = [
            SlotKeyframe(v) for v in values.get("attachment", [])
        ]
        self.color: List[SlotKeyframe] = [
            SlotKeyframe(v) for v in values.get("color", [])
        ]
        self.twoColor = [SlotKeyframe(v) for v in values.get("twoColor", [])]

        super(SlotTimeline, self).__init__(values)

    def is_empty(self):
        """
        In case of having only 1 attachment of type image ('attachment')
        and this attachment also being empty we can consider this Timeline as empty
        """
        return (
            not self.color
            and not self.twoColor
            and (
                len(self.attachment) == 0
                or (
                    len(self.attachment) == 1
                    and self.attachment[0].is_empty()
                    and self.attachment[0].time == 0
                )
            )
        )

    def get_used_attachments(self):
        used_attachments = []
        for attachment in self.attachment:
            if not attachment.is_empty():
                used_attachments.append(attachment.name)
        return used_attachments

    def has_color(self):
        return len(self.color) > 0 or len(self.twoColor) > 0
