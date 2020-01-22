from spine_json_lib.data.data_types.base_type import SpineData


class Path(SpineData):
    DEFAULT_VALUES = {
        "name": "",
        "bones": [],
        "target": "",
        "positionMode": "",
        "spacingMode": "",
        "rotateMode": "",
        "rotation": 0,
        "position": 0,
        "spacing": 1,
        "rotateMix": 1,
        "translateMix": 1,
        "skin": False,
    }
    SPINE_3_8_DEFAULT_VALUES = DEFAULT_VALUES

    def __init__(self, values=None):
        values = values or {}

        self.name = values.get("name")
        self.order = values.get("order")
        self.skin = values.get("skin")
        self.bones = values.get("bones")
        self.target = values.get("target")
        self.positionMode = values.get("positionMode")
        self.spacingMode = values.get("spacingMode")
        self.rotateMode = values.get("rotateMode")
        self.rotation = values.get("rotation")
        self.position = values.get("position")
        self.spacing = values.get("spacing")
        self.rotateMix = values.get("rotateMix")
        self.translateMix = values.get("translateMix")

        super(Path, self).__init__(values)


class PathTimeline(SpineData):
    DEFAULT_VALUES = {"position": 0, "spacing": 1, "rotateMix": 1, "translateMix": 1}
    SPINE_3_8_DEFAULT_VALUES = {
        "position": 0,
        "spacing": 1,
        "rotateMix": 1,
        "translateMix": 1,
        "curve": [],
        "c2": 0,
        "c3": 1,
        "c4": 1,
    }

    def __init__(self, values=None):
        values = values or {}

        self.time = values.get("time")
        self.position = values.get("position")
        self.spacing = values.get("spacing")
        self.rotateMix = values.get("rotateMix")
        self.translateMix = values.get("translateMix")
        self.curve = values.get("curve")
        self.c2 = values.get("c2")
        self.c3 = values.get("c3")
        self.c4 = values.get("c4")

        super(PathTimeline, self).__init__(values)
