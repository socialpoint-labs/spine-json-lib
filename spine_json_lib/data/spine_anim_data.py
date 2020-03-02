import copy
import functools

from typing import Dict, Any, List, Union, FrozenSet, TypeVar, Tuple

from spine_json_lib.data.data_types.animation import Animation
from spine_json_lib.data.data_types.bone import Bone
from spine_json_lib.data.data_types.events import Events
from spine_json_lib.data.data_types.ik import Ik
from spine_json_lib.data.data_types.path import Path
from spine_json_lib.data.data_types.skin import (
    Skin38,
    SkinLinkedMesh,
    SkinAttachment,
    SkinMesh,
)
from spine_json_lib.data.data_types.slot import Slot, SlotTimeline
from spine_json_lib.data.data_types.transform import Transform
from spine_json_lib.data.data_types.base_type import SpineData
from spine_json_lib.data.spine_exceptions import SpineJsonEditorError
from spine_json_lib.data.spine_version_type import SpineVersion


# Mypy forward declarations
JsonSpineAnimationDataType = TypeVar(
    "JsonSpineAnimationDataType", bound="JsonSpineAnimationData"
)
SpineAnimationDataType = TypeVar("SpineAnimationDataType", bound="SpineAnimationData")


class JsonSpineAnimationData:
    def __init__(self, data):
        self.skeleton = copy.deepcopy(data["skeleton"])
        self.spine_version: SpineVersion = SpineVersion(version=self.skeleton["spine"])
        self.data = self.load_data(data=data)

    def load_data(self, data: Dict[str, Any]) -> SpineAnimationDataType:
        _data = SpineAnimationData(data=data)
        _data.set_default_values(version=self.spine_version)
        return _data

    def to_json_data(self) -> Dict[str, Any]:
        json_data = self.data.to_json(self.spine_version)
        json_data["skeleton"] = copy.deepcopy(self.skeleton)
        return json_data


class SpineAnimationData(SpineData):
    DEFAULT_VALUES: Dict[str, Any] = {
        "bones": [],
        "slots": [],
        "events": {},
        "ik": [],
        "transform": [],
        "path": [],
        "animations": {},
    }
    SPINE_3_8_DEFAULT_VALUES: Dict[str, Any] = DEFAULT_VALUES

    def __init__(self, data: Dict[str, Any]) -> None:
        _data = copy.deepcopy(data)
        del _data["skeleton"]

        self.bones: List[Bone] = [Bone(value) for value in _data["bones"]]
        self.slots: List[Slot] = [Slot(value) for value in _data["slots"]]
        self.skins: Union[Dict[str, Any], List[Skin38]] = [
            Skin38(value) for value in _data["skins"]
        ]

        self.events: Dict[str, Events] = {
            key: Events(_data["events"][key]) for key in _data.get("events", {})
        }

        self.ik: List[Ik] = [Ik(value) for value in _data.get("ik", [])]
        self.transform: List[Transform] = [
            Transform(value) for value in _data.get("transform", [])
        ]

        self.path: List[Path] = [Path(value) for value in _data.get("path", [])]

        self.animations: Dict[str, Animation] = {
            key: Animation(_data["animations"][key])
            for key in _data.get("animations", {})
        }

        super(SpineAnimationData, self).__init__(_data)

    def get_bone(self, bone_id: str) -> Union[Bone, None]:
        for bone in self.bones:
            if bone.name == bone_id:
                return bone
        return None

    @staticmethod
    def parse_skins_from_version(version: SpineVersion, data_skins) -> List[Skin38]:
        return [Skin38(value) for value in data_skins]

    def get_skin(self, skin_id):
        for skin in self.skins:
            if skin.name == skin_id:
                return skin
        return None

    def remove_skin(self, skin_name):
        skins = [skin for skin in self.skins if skin.name != skin_name]
        if len(skins) == len(self.skins):
            raise SpineJsonEditorError(
                message="Trying to remove skin with name {} but was not found".format(
                    skin_name
                )
            )

        skin_to_remove = self.get_skin(skin_name)

        for skin in skins:
            for attachment_id, attachment in skin.attachments.items():
                attachment_data = copy.deepcopy(attachment)
                for slot_id, slot_data in attachment_data.items():
                    if (
                        isinstance(slot_data, SkinLinkedMesh)
                        and slot_data.skin == skin_name
                    ):

                        # In case of a LinkedMesh linked to a mesh existing into the skin we want to remove
                        # we need to copy the Mesh information to this LinkedMesh
                        skin_removed_slot_mesh = skin_to_remove.attachments[
                            attachment_id
                        ][slot_id]

                        copied_mesh = copy.deepcopy(skin_removed_slot_mesh)
                        copied_mesh.name = slot_data.name
                        copied_mesh.path = slot_data.path
                        copied_mesh.width = slot_data.width
                        copied_mesh.height = slot_data.height

                        attachment[slot_id] = copied_mesh

        # Get images removed from spine
        removed_images = []
        removed_attachments = {}
        for attachment_id, attachment in skin_to_remove.attachments.items():
            for slot_id, slot_data in attachment.items():
                if isinstance(slot_data, SkinAttachment):
                    image_path = slot_data.path or slot_data.name
                    if image_path is not None:
                        removed_attachments.setdefault(attachment_id, {})
                        removed_attachments[attachment_id][slot_id] = image_path
                elif isinstance(slot_data, SkinMesh):
                    mesh_image_path = slot_data.path or slot_data.name
                    removed_images.append(mesh_image_path)
                elif hasattr(slot_data, "path") and slot_data.path is not None:
                    removed_images.append(slot_data.path)

        # Remove deforms with references to skin we want to remove <skin_name>
        # it should be in any case validated before going into this point as deforms add
        # a performance overhead to the game runtime
        for anim_data in self.animations.values():
            if anim_data.deform and skin_name in anim_data.deform.keys():
                del anim_data.deform[skin_name]

        self.skins = skins

        return removed_images, removed_attachments

    def get_slots_with_alpha_zero(self) -> List[str]:
        """
        Return a list of id of slots with alpha set as 0 on color info attrib
        """
        not_visible_slots = []
        for slot in self.slots:
            if slot.color is not None:
                alpha_value = int("0x{}".format(slot.color), 16) & 0xFF
                if alpha_value == 0:
                    not_visible_slots.append(slot.name)
        return not_visible_slots

    def get_slots_not_visible_in_setup_pose(self) -> List[str]:
        """
        Return a list of not visible slots in setup mode
        """
        no_attachment_slot = []
        for slot in self.slots:
            if (
                slot.attachment is None
                and slot.dark is None
                and slot.blend is None
                and slot.color is None
            ):
                no_attachment_slot.append(slot.name)

        return no_attachment_slot

    def get_visible_slots_and_attachments(
        self, anim_slots, visible_slots, alpha_zero_slots, no_attachment_slots
    ):
        # type: (Dict[str, SlotTimeline], FrozenSet[str], List[str], List[str]) -> Tuple[FrozenSet[str], Dict[str, FrozenSet[str]]]
        anim_visible_slots = frozenset(visible_slots)

        anim_list_visible_slots = [
            slot for slot in self.slots if slot.name in anim_visible_slots
        ]
        anim_used_attachments = {
            slot.name: frozenset([slot.attachment]) for slot in anim_list_visible_slots
        }

        slots_dict = {slot.name: slot for slot in self.slots if slot.name}

        for slot_id, slot_data in anim_slots.items():
            # By default we have to add the slot attachment base data as they are normally missing
            # in the json info for optimization
            slot_used_attachments = slot_data.get_used_attachments() + [
                slots_dict[slot_id].attachment
            ]

            # Discarding slot if:
            # 1 -) At least 1 animation it is not empty
            # 2 -) The slot has alpha 0 but has color information
            # 3 -) Has no setup attachments and is not adding any in animation data
            if (
                slot_data.is_empty()
                or (slot_id in alpha_zero_slots and not slot_data.has_color())
                or (slot_id in no_attachment_slots and not slot_used_attachments)
            ):
                # Mark slot as invisible
                anim_visible_slots -= frozenset([slot_id])
                anim_used_attachments[slot_id] = frozenset([])

            else:
                # Save used attachments
                anim_used_attachments[slot_id] = frozenset(slot_used_attachments)

                # Mark slot as visible
                anim_visible_slots |= frozenset([slot_id])

        return anim_visible_slots, anim_used_attachments

    def get_unused_slots_and_attachments(self) -> (FrozenSet[Any], List[str]):
        """
        - Slots can be visible or invisible by default:
        1 - Visible slots:
            - can only be removed if it is marked in every animation as invisible or zeroed
        2 - Invisible slots:
            - can only be removed if it is not used in any animation or the ones using it are also
            marked to not be shown
        """

        slots_set = frozenset([slot.name for slot in self.slots])
        alpha_zero_slots = self.get_slots_with_alpha_zero()
        no_attachment_slots = self.get_slots_not_visible_in_setup_pose()

        default_invisible_slots = frozenset(alpha_zero_slots + no_attachment_slots)
        default_visible_slots = slots_set - default_invisible_slots

        visible_slots = frozenset([])
        l_attachments_used = frozenset([])

        for anim_id, anim_data in self.animations.items():
            (
                anim_visible_slots,
                anim_used_attachments,
            ) = self.get_visible_slots_and_attachments(
                anim_slots=anim_data.slots,
                visible_slots=default_visible_slots,
                alpha_zero_slots=alpha_zero_slots,
                no_attachment_slots=no_attachment_slots,
            )
            visible_slots |= anim_visible_slots

            l_attachments_used |= functools.reduce(
                (lambda x, y: x | y), anim_used_attachments.values()
            )

        attachments_to_remove: FrozenSet[Any] = frozenset([])

        # Only not visible slots and the ones not being used can be erased
        for skin in self.skins:
            for slot_id, attachment_data in skin.attachments.items():
                attachments_ids = attachment_data.keys()

                for attachment_id in attachments_ids:
                    path_attachment = None
                    if hasattr(attachment_data[attachment_id], "path"):
                        path_attachment = attachment_data[attachment_id].path
                    attachment_unique_id = (
                        path_attachment
                        or attachment_data[attachment_id].name
                        or attachment_id
                    )

                    if attachment_id not in l_attachments_used:
                        attachments_to_remove |= frozenset([attachment_unique_id])

        invisible_slots = slots_set - visible_slots
        return invisible_slots, attachments_to_remove
