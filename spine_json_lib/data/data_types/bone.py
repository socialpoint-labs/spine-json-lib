from typing import Dict, Any, List

from spine_json_lib.data.data_types.base_type import SpineData


class Bone(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {
        "x": 0,
        "y": 0,
        "scaleX": 1.0,
        "scaleY": 1.0,
        "shearX": 0,
        "shearY": 0,
        "transform": "normal",
        "inheritRotation": False,
        "rotation": 0,
        "length": 0,
        "inheritScale": False,
    }
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES

    REQUIRED = ["name"]

    def __init__(self, values: Dict[str, Any] = None) -> None:
        values = values or {}

        self.name: str = values.get("name")
        self.parent: str = values.get("parent")
        self.color: str = values.get("color")
        self.scaleX: float = values.get("scaleX")
        self.transform: str = values.get("transform")
        self.shearY: float = values.get("shearY")
        self.scaleY: float = values.get("scaleY")
        self.inheritRotation: bool = values.get("inheritRotation")
        self.length = values.get("length")
        self.y: float = values.get("y")
        self.x: float = values.get("x")
        self.rotation: float = values.get("rotation")
        self.shearX: float = values.get("shearX")
        self.inheritScale: bool = values.get("inheritScale")

        super(Bone, self).__init__(values)

    def scale(self, scaleX, scaleY):
        self.scaleX *= scaleX
        self.scaleY *= scaleY


class BoneTranslateAndShearKeyframe(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {"curve": []}
    UNSUPPORTED_VALUES_OLD_VERSION = ["c2", "c3", "c4"]

    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = {
        "curve": [],
        "angle": 0,
        "time": 0,
        "x": 0,
        "y": 0,
        "c2": 0,
        "c3": 1,
        "c4": 1,
    }

    def __init__(self, values=None):
        values = values or {}

        self.time = values.get("time")
        self.curve = values.get("curve")
        self.angle = values.get("angle")
        self.x = values.get("x")
        self.y = values.get("y")
        self.c2 = values.get("c2")
        self.c3 = values.get("c3")
        self.c4 = values.get("c4")

        super(BoneTranslateAndShearKeyframe, self).__init__(values)


class BoneRotateAndScaleKeyframe(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {"curve": []}
    UNSUPPORTED_VALUES_OLD_VERSION = ["c2", "c3", "c4"]

    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = {
        "curve": [],
        "angle": 0,
        "x": 1,
        "y": 1,
        "time": 0,
        "c2": 0,
        "c3": 1,
        "c4": 1,
    }

    def __init__(self, values=None):
        values = values or {}

        self.time = values.get("time")
        self.curve = values.get("curve")
        self.angle = values.get("angle")
        self.x = values.get("x")
        self.y = values.get("y")
        self.c2 = values.get("c2")
        self.c3 = values.get("c3")
        self.c4 = values.get("c4")

        super(BoneRotateAndScaleKeyframe, self).__init__(values)


class BoneTimeline(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {
        "rotate": [],
        "translate": [],
        "scale": [],
        "shear": [],
    }
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES

    def __init__(self, values=None):
        values = values or {}

        self.rotate: List[BoneRotateAndScaleKeyframe] = [
            BoneRotateAndScaleKeyframe(value) for value in values.get("rotate", [])
        ]
        self.translate: List[BoneTranslateAndShearKeyframe] = [
            BoneTranslateAndShearKeyframe(value)
            for value in values.get("translate", [])
        ]
        self.scale: List[BoneRotateAndScaleKeyframe] = [
            BoneRotateAndScaleKeyframe(value) for value in values.get("scale", [])
        ]
        self.shear: List[BoneTranslateAndShearKeyframe] = [
            BoneTranslateAndShearKeyframe(value) for value in values.get("shear", [])
        ]

        super(BoneTimeline, self).__init__(values)
