import pytest

from spine_json_lib.utils import get_tags_from_name
from deepdiff import DeepDiff


@pytest.mark.parametrize(
    "tag_name, result",
    [
        ("master[scale : 0.5]", {"scale": 0.5}),
        ("master[ scale:0.5 ]", {"scale": 0.5}),
        ("master[ scale : 0.5 ]", {"scale": 0.5}),
        ("master[scale:0.5", {}),
        ("masterscale:0.5]", {}),
        ("master[scale0.5]", {}),
    ],
)
def test_get_tag_from_name_ok(tag_name, result):
    tags_result = get_tags_from_name(tag_name)
    assert DeepDiff(result, tags_result, ignore_order=False) == {}


def test_unsupported_tag():
    bone_name = "bone1[unsupported : empty]"
    with pytest.raises(ValueError) as e:
        get_tags_from_name(bone_name)

    assert str(e.value) == f"Found unsupported TAG [unsupported] in {bone_name}"


def test_wrong_type_tag_value():
    invalid_tag_value = "invalid_str"
    bone_name = f"bone_layer[ scale:{invalid_tag_value} ]"
    with pytest.raises(ValueError) as e:
        get_tags_from_name(bone_name)

    assert str(e.value) == f"could not convert string to float: '{invalid_tag_value}'"
