import copy
from collections import OrderedDict
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

    @staticmethod
    def _reorder_slots_with_offset(slot_offsets, original_slots):
        new_slots_draw_order = copy.deepcopy(original_slots)
        operations = []
        pop_indexes = []
        for index, slot in enumerate(original_slots):
            if slot.name in slot_offsets:
                new_index = index + slot_offsets[slot.name].offset
                operations.append({"slot": slot, "new_index": new_index})
                pop_indexes.append(index)

        for _index in reversed(pop_indexes):
            new_slots_draw_order.pop(_index)

        sorted_operations = sorted(operations, key=lambda x: x["new_index"])
        for cached in sorted_operations:
            new_slots_draw_order.insert(cached["new_index"], cached["slot"])

        return new_slots_draw_order

    @staticmethod
    def _adjust_draw_oder_offset_with_erased_slots(
            slots_to_be_removed, slots, slot_offsets, original_slots
    ):
        plain_reordered_slots = [_slot.name for _slot in slots]
        plain_original_slots = [_slot.name for _slot in original_slots]
        adjusted_draw_order_offsets = copy.deepcopy(slot_offsets)
        for name, slot in slot_offsets.items():
            end_index = plain_reordered_slots.index(slot.slot)
            original_index = plain_original_slots.index(slot.slot)
            for slot_to_remove in slots_to_be_removed:
                _index = plain_reordered_slots.index(slot_to_remove)
                if original_index <= _index <= end_index:
                    adjusted_draw_order_offsets[name].offset -= 1
                elif end_index <= _index <= original_index:
                    adjusted_draw_order_offsets[name].offset += 1
                else:
                    pass

        return adjusted_draw_order_offsets

    def remove_offsets_with_ids(self, slots_ids, original_slots):
        """
        When we remove a slot, the position of the slot removed could interfere directly
        to the offsets saved in the drawOrder lists of every animation raising
        an ArrayIndexOutOfBoundsException on loading time in Spine.
        We need to update the drawOrder offsets bearing in mind the slots removed
        and the new position in the slots array.
        """
        slot_offsets = OrderedDict({offset.slot: offset for offset in self.offsets})
        new_slots_draw_order = self._reorder_slots_with_offset(
            slot_offsets, original_slots
        )
        adjusted_draw_order_offsets = self._adjust_draw_oder_offset_with_erased_slots(
            slots_ids, new_slots_draw_order, slot_offsets, original_slots
        )
        self.offsets = [
            offset
            for offset in adjusted_draw_order_offsets.values()
            if offset.slot not in slots_ids
        ]
