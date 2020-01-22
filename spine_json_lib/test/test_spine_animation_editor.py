import os

import pytest
import json

from spine_json_lib.spine_animation_editor import SpineAnimationEditor
from deepdiff import DeepDiff
from typing import Any
from typing import Dict

SPINE_JSON_ERASE_SKIN_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data/original/masquerade_skeleton.json"
)
SPINE_IMAGES_JSON_ERASE_SKIN_REFS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data/cleaned_up/masquerade_json_images_refs.json",
)
SPINE_JSON_ERASE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data/original/elvira_original.json"
)
SPINE_JSON_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data/original/original.json"
)
IMAGES_JSON_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data/original/image_paths.json"
)
ELVIRA_CLEANED_JSON_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data/cleaned_up/elvira_cleaned_up.json"
)
ELVIRA_CLEANED_UP_IMAGES_JSON_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data/cleaned_up/images_path_cleaned_up.json",
)

_TEMPLATE_CONFIG = {
    "name": "export_bin_config.json",
    "is_json_exporter": False,
    "non_essential_info": False,
    "pretty_print": False,
}


def orderer(obj):
    if isinstance(obj, dict):
        return sorted((k, orderer(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(orderer(x) for x in obj)
    else:
        return obj


@pytest.fixture
def fixture_elvira_spine_json_data() -> Dict[str, Any]:
    with open(ELVIRA_CLEANED_JSON_PATH) as f:
        json_data = json.load(f)
    return json_data


class TestSpineAnimationEditor:
    def test_load_new_version(self):
        animation_editor = SpineAnimationEditor.from_json_file(
            json_path=SPINE_JSON_PATH
        )

        with open(SPINE_JSON_PATH) as f:
            json_data = json.load(f)

        assert (
            DeepDiff(animation_editor.to_json_data(), json_data, ignore_order=False)
            == {}
        )

    def test_erase_animation(self, fixture_elvira_spine_json_data):
        animation_editor = SpineAnimationEditor.from_json_file(
            json_path=SPINE_JSON_ERASE_PATH
        )
        result = animation_editor.erase_animations(
            animations_to_erase=["attack", "special1", "levelup", "prone"],
            strict_mode=True,
        )

        assert (
            DeepDiff(
                fixture_elvira_spine_json_data,
                result.result_data_json,
                ignore_order=False,
            )
            == {}
        )

        with open(ELVIRA_CLEANED_UP_IMAGES_JSON_PATH, "r") as f:
            data_image_refs = json.load(f)

        assert (
            DeepDiff(
                animation_editor.images_references, data_image_refs, ignore_order=False
            )
            == {}
        )

    def test_images_refs(self):
        animation_editor = SpineAnimationEditor.from_json_file(
            json_path=SPINE_JSON_PATH
        )
        with open(IMAGES_JSON_PATH, "r") as f:
            data_image_refs = json.load(f)

        assert (
            DeepDiff(
                animation_editor.images_references, data_image_refs, ignore_order=False
            )
            == {}
        )

    def test_erase_skins(self):
        animation_editor = SpineAnimationEditor.from_json_file(
            json_path=SPINE_JSON_ERASE_SKIN_PATH
        )
        clean_up_removed_data, skin_related_images = animation_editor.erase_skins(
            skins_to_erase=["basic"]
        )
        # import ipdb; ipdb.set_trace()
        assert sorted(skin_related_images) == sorted(
            [
                "sherezar/belt_l",
                "sherezar/ponytail_2",
                "sherezar/eye_l",
                "sherezar/leg_r",
                "sherezar/foot_l",
                "sherezar/foot_r",
                "sherezar/leg_l",
                "sherezar/skirt",
                "sherezar/belt",
                "sherezar/beard_1",
                "sherezar/beard_2",
                "sherezar/beard_3",
                "sherezar/ear_l",
                "sherezar/chest",
                "sherezar/ear_r",
                "sherezar/belt_r",
                "sherezar/eye_r",
                "sherezar/ponytail_1",
                "sherezar/shirt",
                "sherezar/mask",
                "sherezar/mouth",
                "sherezar/foot_l",
                "sherezar/beard_4",
                "sherezar/shoulder_l_2",
                "sherezar/finger_r_4",
                "sherezar/finger_r_3",
                "sherezar/finger_r_2",
                "sherezar/finger_r_1",
                "sherezar/shoulder_l_1",
                "sherezar/finger_r_2",
                "sherezar/head",
                "sherezar/finger_r_4",
                "sherezar/arm_l_1",
                "sherezar/finger_r_3",
                "sherezar/arm_l_2",
                "sherezar/shoulder_r_1_front",
                "sherezar/shoulder_r_2",
                "sherezar/forearm_r",
                "sherezar/forearm_l",
                "sherezar/palm_r",
                "sherezar/palm_r",
                "sherezar/stick_up",
                "sherezar/arm_r",
                "sherezar/finger_r_1",
                "sherezar/stick_down",
                "sherezar/hips",
            ]
        )
        slots_removed, attachments_removed = clean_up_removed_data
        assert sorted(slots_removed) == sorted(
            [
                "ponytail_4",
                "fx/purple_smoke12",
                "fx/purple_smoke11",
                "fx/purple_smoke10",
                "eye_r",
                "ear_l",
                "ponytail_3",
                "ear_r",
                "fx/purple_smoke7",
                "eye_l",
                "fx/purple_smoke9",
                "fx/purple_smoke8",
                "skirt",
            ]
        )
        assert attachments_removed == frozenset(
            [
                "fx_purple_smoke_5",
                "fx_purple_smoke_4",
                "fx_purple_smoke_7",
                "fx_purple_smoke_basis",
                "fx_purple_smoke_1",
                "fx_purple_smoke_0",
                "fx_purple_smoke_3",
                "fx_purple_smoke_2",
                "fx_purple_smoke_6",
                "fx_purple_smoke_8",
            ]
        )

        assert "basic" not in [
            skin_data.name for skin_data in animation_editor.spine_anim_data.data.skins
        ]

        with open(SPINE_IMAGES_JSON_ERASE_SKIN_REFS_PATH, "r") as f:
            imgs_refs_expected = json.load(f)

        assert DeepDiff(animation_editor.images_references, imgs_refs_expected) == {}
