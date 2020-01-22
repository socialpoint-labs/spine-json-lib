from typing import Dict, Any

from spine_json_lib.data.data_types.base_type import SpineData


class Transform(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {
        "name": "",
        "order": 0,
        "bone": "",
        "target": "",
        "rotation": 0,
        "x": 0,
        "y": 0,
        "scaleX": 1.0,
        "scaleY": 1.0,
        "shearX": 0,
        "shearY": 0,
    }
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES

    def __init__(self, values=None):
        values = values if values is not None else {}

        self.name = values.get("name")
        self.order = values.get("order")
        self.bone = values.get("bone")
        self.bones = values.get("bones")
        self.target = values.get("target")
        self.rotation = values.get("rotation")
        self.x = values.get("x")
        self.y = values.get("y")
        self.scaleX = values.get("scaleX")
        self.scaleY = values.get("scaleY")
        self.shearX = values.get("shearX")
        self.shearY = values.get("shearY")
        self.rotateMix = values.get("rotateMix")
        self.translateMix = values.get("translateMix")
        self.scaleMix = values.get("scaleMix")
        self.shearMix = values.get("shearMix")
        self.local = values.get("local")
        self.relative = values.get("relative")

        super(Transform, self).__init__(values)


class TransformTimeline(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {"curve": []}

    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = {
        "curve": [],
        "time": 0,
        "c2": 0,
        "c3": 1,
        "c4": 1,
    }

    def __init__(self, values=None):
        values = values or {}

        self.time: float = values.get("time")
        self.rotateMix: float = values.get("rotateMix")
        self.translateMix: float = values.get("translateMix")
        self.scaleMix: float = values.get("scaleMix")
        self.shearMix: float = values.get("shearMix")
        self.curve = values.get("curve")
        self.c2 = values.get("c2")
        self.c3 = values.get("c3")
        self.c4 = values.get("c4")

        super(TransformTimeline, self).__init__(values)
