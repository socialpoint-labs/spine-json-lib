from typing import List, Dict, Any

from spine_json_lib.data.data_types.base_type import SpineData
from spine_json_lib.data.data_types.bone import BoneTimeline
from spine_json_lib.data.data_types.deform import Deform
from spine_json_lib.data.data_types.draworder import DrawOrderTimeline
from spine_json_lib.data.data_types.events import EventTimeline
from spine_json_lib.data.data_types.ik import IkTimeline
from spine_json_lib.data.data_types.path import PathTimeline
from spine_json_lib.data.data_types.slot import SlotTimeline
from spine_json_lib.data.data_types.transform import TransformTimeline


class Animation(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {
        "ik": {},
        "drawOrder": [],
        "bones": {},
        "slots": {},
        "events": [],
        "transform": {},
        "deform": {},
        "path": {},
    }
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES

    def __init__(self, values=None):
        values = values or {}

        self.ik: Dict[str, List[IkTimeline]] = {
            key: [IkTimeline(ik) for ik in values["ik"][key]]
            for key in values.get("ik", {})
        }

        self.drawOrder: List[DrawOrderTimeline] = [
            DrawOrderTimeline(v) for v in values.get("drawOrder", [])
        ]

        self.bones: Dict[str, BoneTimeline] = {
            key: BoneTimeline(values["bones"][key]) for key in values.get("bones", {})
        }

        self.slots: Dict[str, SlotTimeline] = {
            key: SlotTimeline(values["slots"][key]) for key in values.get("slots", {})
        }

        self.events: List[EventTimeline] = [
            EventTimeline(value) for value in values.get("events", [])
        ]

        self.transform: Dict[str, List[TransformTimeline]] = {
            key: [
                TransformTimeline(transform) for transform in values["transform"][key]
            ]
            for key in values.get("transform", {})
        }

        self.path: Dict[str, Dict[str, List[PathTimeline]]] = self.parse_path(
            values.get("path", {})
        )
        self.deform: Dict[str, Dict[str, Dict[str, List[Deform]]]] = self.parse_deform(
            values.get("deform", {})
        )

        super(Animation, self).__init__(values)

    @staticmethod
    def parse_path(
        path_data: Dict[str, Any]
    ) -> Dict[str, Dict[str, List[PathTimeline]]]:
        return {
            k: {
                k2: [PathTimeline(path) for path in path_list]
                for k2, path_list in v.items()
            }
            for k, v in path_data.items()
        }

    @staticmethod
    def parse_deform(
        deform_data: Dict[str, Any]
    ) -> Dict[str, Dict[str, Dict[str, List[Deform]]]]:
        return {
            k: {
                k2: {
                    k3: [Deform(deform) for deform in deform_list]
                    for k3, deform_list in v2.items()
                }
                for k2, v2 in v.items()
            }
            for k, v in deform_data.items()
        }

    def remove_draw_order_with_ids(self, slots_ids, original_slots):
        for draw_order in self.drawOrder:
            draw_order.remove_offsets_with_ids(slots_ids, original_slots)
