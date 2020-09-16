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
        original_slots_names = [_slot.name for _slot in original_slots]
        # Filter out slots we want to remove
        clean_original_slots = list(
            filter(lambda x: x not in slots_to_be_removed, original_slots_names)
        )

        reordered_slots_names = [_slot.name for _slot in slots]
        # Filter out slots we want to remove
        clean_reordered_slots = list(
            filter(lambda x: x not in slots_to_be_removed, reordered_slots_names)
        )

        adjusted_draw_order_offsets = copy.deepcopy(slot_offsets)

        for name, slot_offset in adjusted_draw_order_offsets.items():
            if name in slots_to_be_removed:
                continue
            index_original = clean_original_slots.index(name)
            index_final = clean_reordered_slots.index(name)
            slot_offset.offset = index_final - index_original

        return [
            offset
            for offset in adjusted_draw_order_offsets.values()
            if offset.slot not in slots_to_be_removed and offset.offset != 0
        ]

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

        self.offsets = self._adjust_draw_oder_offset_with_erased_slots(
            slots_to_be_removed=slots_ids,
            slots=new_slots_draw_order,
            slot_offsets=slot_offsets,
            original_slots=original_slots,
        )
