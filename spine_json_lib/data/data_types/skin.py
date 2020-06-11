import copy

from typing import Dict, Any, List

from spine_json_lib.data.data_types.base_type import SpineData


MESH_TYPE = "mesh"
PATH_TYPE = "path"
SLOT_TYPE = "slot"
LINKED_MESH_TYPE = "linkedmesh"
POINT_TYPE = "point"
CLIPPING_TYPE = "clipping"
BOUNDING_BOX_TYPE = "boundingbox"
REGION_TYPE = "region"

SKIN_ATTACHMENTS_TYPES = [
    MESH_TYPE,
    PATH_TYPE,
    SLOT_TYPE,
    POINT_TYPE,
    CLIPPING_TYPE,
    BOUNDING_BOX_TYPE,
    REGION_TYPE,
]


def parse_skin_attachment_data(attachments):
    result = copy.deepcopy(attachments)

    for attach_id in attachments:
        for slot_id in attachments[attach_id]:
            skin_data = attachments[attach_id][slot_id]
            skin_data_type = skin_data.get("type")
            if skin_data_type == PATH_TYPE:
                result[attach_id][slot_id] = SkinPath(values=skin_data)
            elif skin_data_type == MESH_TYPE:
                result[attach_id][slot_id] = SkinMesh(values=skin_data)
            elif skin_data_type == LINKED_MESH_TYPE:
                result[attach_id][slot_id] = SkinLinkedMesh(values=skin_data)
            elif skin_data_type == POINT_TYPE:
                result[attach_id][slot_id] = SkinPoint(values=skin_data)
            elif skin_data_type == CLIPPING_TYPE:
                result[attach_id][slot_id] = SkinClipping(values=skin_data)
            elif skin_data_type == BOUNDING_BOX_TYPE:
                result[attach_id][slot_id] = SkinBoundingBox(values=skin_data)
            elif skin_data_type is None:
                result[attach_id][slot_id] = SkinAttachment(values=skin_data)
            else:
                raise ValueError(
                    "Error: wrong skin attachment type {} in id {} when only {} are supported".format(
                        skin_data_type, slot_id, SKIN_ATTACHMENTS_TYPES
                    )
                )
    return result


class Skin38(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {"name": "", "attachments": {}}
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES

    def __init__(self, values: Dict[str, Any] = None) -> None:
        values = values or {}

        self.name = values.get("name")
        self.attachments = values.get("attachments")

        super(Skin38, self).__init__(values)

        if self.attachments is not None:
            self.attachments = parse_skin_attachment_data(self.attachments)


class SkinAttachment(SpineData):
    """
    In the docs this is identified as default type named "region"
    """

    DEFAULT_VALUES: Dict[str, Any] = {
        "x": 0,
        "y": 0,
        "rotation": 0,
        "scaleX": 1.0,
        "scaleY": 1.0,
    }
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES

    def __init__(self, values: Dict[str, Any] = None) -> None:
        values = values or {}

        self.x = values.get("x")
        self.y = values.get("y")
        self.rotation = values.get("rotation")
        self.width = values.get("width")
        self.height = values.get("height")
        self.scaleX = values.get("scaleX")
        self.scaleY = values.get("scaleY")
        self.name = values.get("name")
        self.path = values.get("path")
        self.color: str = values.get("color")

        super(SkinAttachment, self).__init__(values)


class SkinMesh(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {
        "uvs": [],
        "vertices": [],
        "edges": [],
        "triangles": [],
    }
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES

    def __init__(self, values: Dict[str, Any] = None) -> None:
        values = values or {}

        self.hull = values.get("hull")
        self.uvs: List[int] = values.get("uvs")
        self.vertices: List[float] = values.get("vertices")
        self.height: int = values.get("height")
        self.width: int = values.get("width")
        self.edges: List[int] = values.get("edges")
        self.type: str = values.get("type")
        self.triangles: List[int] = values.get("triangles")
        self.name: str = values.get("name")
        self.path: str = values.get("path")
        self.color: str = values.get("color")

        super(SkinMesh, self).__init__(values)


class SkinPath(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {
        "lengths": [],
        "vertexCount": 0,
        "vertices": [],
        "constantSpeed": True,
        "closed": False,
    }
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES

    def __init__(self, values: Dict[str, Any] = None) -> None:
        values = values or {}

        self.lengths: List[float] = values.get("lengths")
        self.vertexCount: int = values.get("vertexCount")
        self.type: str = values.get("type")
        self.name: str = values.get("name")
        self.vertices: List[float] = values.get("vertices")
        self.color: str = values.get("color")
        self.closed = values.get("closed")
        self.constantSpeed = values.get("constantSpeed")

        super(SkinPath, self).__init__(values)


class SkinLinkedMesh(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {}
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = {"deform": True}

    def __init__(self, values: Dict[str, Any] = None) -> None:
        values = values or {}

        self.path: str = values.get("path")
        self.height: int = values.get("height")
        self.width: int = values.get("width")
        self.name: str = values.get("name")
        self.parent: str = values.get("parent")
        self.deform: bool = values.get("deform")
        self.color: str = values.get("color")
        self.skin: str = values.get("skin")
        self.type: str = values.get("type")

        super(SkinLinkedMesh, self).__init__(values)


class SkinBoundingBox(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {}
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES

    def __init__(self, values: Dict[str, Any] = None) -> None:
        values = values or {}

        self.vertexCount: int = values.get("vertexCount")
        self.vertices: List[float] = values.get("vertices")
        self.color: str = values.get("color")

        super(SkinBoundingBox, self).__init__(values)


class SkinPoint(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {"x": 0, "y": 0, "rotation": 0}
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES

    def __init__(self, values: Dict[str, Any] = None) -> None:
        values = values or {}

        self.x = values.get("x")
        self.y = values.get("y")
        self.rotation = values.get("rotation")
        self.color = values.get("color")

        super(SkinPoint, self).__init__(values)


class SkinClipping(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {"vertexCount": 0, "vertices": []}
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES

    def __init__(self, values: Dict[str, Any] = None) -> None:
        values = values or {}

        self.end = values.get("end")
        self.vertexCount: int = values.get("vertexCount")
        self.vertices: List[float] = values.get("vertices")
        self.color: str = values.get("color")

        super(SkinClipping, self).__init__(values)
