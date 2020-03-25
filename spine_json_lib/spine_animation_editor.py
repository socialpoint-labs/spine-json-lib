import copy
import json
import os
from collections import namedtuple

from typing import List, TypeVar

from spine_json_lib.data.constants import SPINE_3_8_VERSION
from spine_json_lib.data.data_types.bone import Bone
from spine_json_lib.data.data_types.ik import Ik
from spine_json_lib.data.data_types.skin import SkinPath
from spine_json_lib.data.data_types.slot import Slot
from spine_json_lib.data.spine_anim_data import JsonSpineAnimationData
from spine_json_lib.data.spine_exceptions import SpineJsonEditorError
from spine_json_lib.deserializer.spine_nodes import SpineGraphParser, NodeType
from spine_json_lib.spine_graph_container import SpineGraphContainer

ANIMATION_EMPTY_ATTACHMENT = {"time": 0, "name": None}
ErasingResult = namedtuple("ErasingResult", "result_data_json result_summary")


class AnimationEraserResult:
    def __init__(self):
        self.nodes_erased = {}

    def save_node_erased(self, node):
        if node.node_type not in self.nodes_erased.keys():
            self.nodes_erased[node.node_type] = frozenset([])

        self.nodes_erased[node.node_type] |= frozenset([node.id])

    def get_attachments(self):
        return self.nodes_erased.get(NodeType.ATTACHMENT.name, frozenset([]))


SpineAnimationEditorType = TypeVar(
    "SpineAnimationEditorType", bound="SpineAnimationEditor"
)


class SpineAnimationEditor(object):
    """
    Class to provide a way to interact and modify an spine json.
    Actions supported:
    - Convert between versions of spine.
    - Erase certain animations.
    - Clean/Optimize animations
    - Scale animation.
    """

    def __init__(self, json_data):
        self.spine_anim_data = JsonSpineAnimationData(data=json_data)

        self.images_references = self.get_images_references()

        json_data = self.spine_anim_data.to_json_data()
        self.spine_graph = SpineGraphContainer(json_data)

    @staticmethod
    def from_json_file(json_path: str) -> SpineAnimationEditorType:
        with open(json_path) as f:
            spine_json_data = json.load(f)

        return SpineAnimationEditor(json_data=spine_json_data)

    def erase_skins(self, skins_to_erase):
        images_skins_refs = []
        skin_attachments_removed = {}
        for skin_name in skins_to_erase:
            (
                skin_removed_images,
                attachments_removed,
            ) = self.spine_anim_data.data.remove_skin(skin_name=skin_name)
            images_skins_refs += skin_removed_images
            skin_attachments_removed[skin_name] = attachments_removed

        json_data = self.spine_anim_data.to_json_data()
        self.spine_graph = SpineGraphContainer(json_data)

        # Flattening images refs in skins
        for skin_name, attachments in skin_attachments_removed.items():
            for slot_data in attachments.values():
                for attachment_path in slot_data.values():
                    images_skins_refs.append(attachment_path)

        # Check which attachments are not being used in the remaining skins
        images_to_remove = []

        for img in images_skins_refs:
            attachment_graph_id = SpineGraphParser._to_graph_id(
                node_type_name=NodeType.ATTACHMENT.name, node_base_id=img
            )
            if not self.spine_graph.graph.get_node(attachment_graph_id):
                images_to_remove.append(img)

        removed_data = self.clean_animation()
        self._clean_images_references(attachments_ids=images_to_remove)

        return removed_data, images_to_remove

    def erase_animations(
        self, animations_to_erase: List[str], strict_mode: bool = True
    ) -> ErasingResult:
        if self.images_references is None:
            raise SpineJsonEditorError(
                message="Internal value error: 'images_json' not initialized"
            )

        if not isinstance(animations_to_erase, list):
            raise TypeError(
                "animations_to_erase needs to be a list of the animation ids to erase"
            )

        self._erase_raw_animations_data(
            animations_to_erase=animations_to_erase, strict_mode=strict_mode
        )

        # After removing animations we have to clean references to slots/attachments
        # that were only used only in the part of the animations removed
        # or are not visible anymore
        removed_data = self.clean_animation()
        return ErasingResult(self.spine_anim_data.to_json_data(), removed_data)

    def clean_animation(self):
        """
        - This method clean empty SLOTS and ATTACHMENTS that are not being
        used or are invisible(with alpha 0) in the animation.
        - In the case of ATTACHMENTS removed being of type region attachments we have to
        update also reference to sprites in the animation.
        - Also we recursively look for slots that are leaves in the animation
        meaning that they have not any attachment attached and can be safely removed.
        - We cannot remove BONES because it affect the weight on meshes and the vertices
        information saved in the binary.
        """
        # Save slots before removing. Needed to recalculate offsets when removing
        # slots in a drawOrder array.
        slots_before_removing = copy.deepcopy(self.spine_anim_data.data.slots)
        (
            slots_to_remove,
            attachments_to_remove,
        ) = self.spine_anim_data.data.get_unused_slots_and_attachments()
        self.spine_graph.remove_slots(list(slots_to_remove))
        self.spine_graph.remove_attachments(list(attachments_to_remove))

        # Removing leaves that are slots, which means
        # they don't have any attachment as children and can be removed from animation
        leaf_slots = self.spine_graph.remove_empty_slots()
        slots_to_remove = list(slots_to_remove | frozenset(leaf_slots))

        # Convert spine graph back to json data
        output_json_data = self.spine_graph.graph.to_json_data(SpineGraphParser)
        self.spine_anim_data.data.bones = [Bone(b) for b in output_json_data["bones"]]
        self.spine_anim_data.data.slots = [Slot(s) for s in output_json_data["slots"]]
        self.spine_anim_data.data.ik = [Ik(i) for i in output_json_data["ik"]]
        self.spine_anim_data.data.set_default_values(self.spine_version)

        # Remove references in animations/skins/etc of elements erased
        self.remove_slots(slots_ids=slots_to_remove, original_slots=slots_before_removing)
        print("Removed slots {}".format(slots_to_remove))

        self.remove_attachments(attachments_ids=attachments_to_remove)
        print("Removed attachments {}".format(attachments_to_remove))

        # Remove reference to region attachments in images json file
        self._clean_images_references(attachments_ids=attachments_to_remove)
        return list(slots_to_remove), attachments_to_remove

    def remove_slots(self, slots_ids, original_slots):
        self._clean_slots_in_skins(slots_ids)
        self._clean_slots_in_animations(slots_ids)
        self._clean_draw_order_refs(slots_ids, original_slots)

    def remove_attachments(self, attachments_ids):
        self._clean_attachments_in_skins(attachment_ids=attachments_ids)
        self._clean_attachments_in_slots(attachments_ids=attachments_ids)

    def scale_animation(self, scaleX, scaleY):
        # To scale the animation we have to scale the root bone,
        # but also all the bones with 'noScale', 'onlyTranslation' and 'noScaleOrReflection'
        # attributes as these don't inherit scale from parent roots
        spine_data = self.spine_anim_data.data
        for bone in spine_data.bones:

            if bone.transform in ["noScale", "noScaleOrReflection", "onlyTranslation"]:
                bone.scale(scaleX=scaleX, scaleY=scaleY)
        spine_data.get_bone("root").scale(scaleX=scaleX, scaleY=scaleY)

    @property
    def spine_version(self):
        return self.spine_anim_data.spine_version

    def to_json_data(self):
        return self.spine_anim_data.to_json_data()

    def to_json(self, output_json):
        base_dir = os.path.dirname(output_json)
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)

        with open(output_json, "w") as outfile:
            json.dump(self.to_json_data(), outfile, indent=4)

    def get_images_references(self):
        paths = {}

        images_folder = self.spine_anim_data.skeleton.get("images", "./images/")
        for skin in self.spine_anim_data.data.skins:
            if self.spine_version >= SPINE_3_8_VERSION:
                skin_data = skin.attachments
            else:
                skin_data = self.spine_anim_data.data.skins[skin]

            for part_name in skin_data:
                for sub_part_key in skin_data[part_name]:
                    skin_sub_part_instance = skin_data[part_name][sub_part_key]
                    if not isinstance(skin_sub_part_instance, SkinPath):
                        relative_path = (
                            skin_sub_part_instance.path
                            or skin_sub_part_instance.name
                            or sub_part_key
                        )

                        image_path = os.path.join(images_folder, relative_path)
                        paths[relative_path] = {"path": image_path}

        return paths

    def save_images_json(self, images_json):
        base_dir = os.path.dirname(images_json)
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)

        with open(images_json, "w") as outfile:
            json.dump(self.images_references, outfile)

    def _erase_raw_animations_data(
        self, animations_to_erase: List[str], strict_mode: bool
    ) -> None:
        # Erasing animation from the json
        not_found_animations = []
        for animation_name in animations_to_erase:
            if animation_name in self.spine_anim_data.data.animations:
                del self.spine_anim_data.data.animations[animation_name]
            else:
                not_found_animations.append(animation_name)

        if not_found_animations and strict_mode:
            raise ValueError(
                "Animations with ids {} could not be found inside the spine file".format(
                    not_found_animations
                )
            )

    def _clean_images_references(self, attachments_ids: List[str]) -> None:
        copy_json = copy.deepcopy(self.images_references)
        removed_images = []
        for img_id, img_abs_path in self.images_references.items():
            if img_id in attachments_ids:
                removed_images.append(img_id)
                del copy_json[img_id]

        if removed_images:
            print("Removed images: {}".format(removed_images))

        self.images_references = copy_json

    def _clean_slots_in_skins(self, slots_ids: List[str]) -> None:
        skins_data = copy.deepcopy(self.spine_anim_data.data.skins)
        for index_skin, data in enumerate(self.spine_anim_data.data.skins):
            skin_attachment = {
                idx: data.attachments[idx]
                for idx in data.attachments
                if idx not in slots_ids
            }
            skins_data[index_skin].attachments = skin_attachment

        self.spine_anim_data.data.skins = skins_data

    def _clean_attachments_in_skins(self, attachment_ids: List[str]) -> None:
        skins_data = copy.deepcopy(self.spine_anim_data.data.skins)
        for index_skin, data in enumerate(self.spine_anim_data.data.skins):
            data_current_skin = skins_data[index_skin]

            for slot_id, slot_data in data.attachments.items():
                for attachment_id in slot_data.keys():
                    name_attachment = slot_data[attachment_id].name or attachment_id
                    if name_attachment in attachment_ids:
                        del data_current_skin.attachments[slot_id][attachment_id]

        self.spine_anim_data.data.skins = skins_data

    def _clean_attachments_in_slots(self, attachments_ids: List[str]) -> None:
        """ Cleaning default attachments in slots """

        copy_slots_data = copy.deepcopy(self.spine_anim_data.data.slots)
        for slot_idx, slot_data in enumerate(self.spine_anim_data.data.slots):
            default_attachment_id = slot_data.get("attachment")
            if default_attachment_id is not None:
                attachment_graph_id = SpineGraphParser._to_graph_id(
                    NodeType.ATTACHMENT.name, default_attachment_id
                )
                if attachment_graph_id in attachments_ids:
                    copy_slots_data[slot_idx].attachment = None

        self.spine_anim_data.data.slots = copy_slots_data

    def _clean_slots_in_animations(self, slots_ids: List[str]) -> None:
        for anim_id, anim_data in self.spine_anim_data.data.animations.items():
            anim_data_slots = copy.deepcopy(anim_data.slots)
            for slot_id, slots_data in anim_data.slots.items():
                if slot_id in slots_ids:
                    del anim_data_slots[slot_id]

            anim_data.slots = anim_data_slots

    def _clean_draw_order_refs(self, slots_ids: List[str], original_slots: List[Slot]) -> None:
        for animation in self.spine_anim_data.data.animations.values():
            animation.remove_draw_order_with_ids(slots_ids=slots_ids, original_slots=original_slots)
