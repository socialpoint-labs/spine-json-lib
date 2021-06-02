import re
from typing import List, Any

SEPARATOR = ":"

TYPE_NUMBER = "number"
TYPE_STRING = "string"
TYPE_BOOLEAN = "boolean"
TYPE_INTEGER = "integer"

SCALE_TAG = "scale"

TAGS_SUPPORTED = {SCALE_TAG: TYPE_NUMBER}

tag_detector = re.compile(r"\[\s*[\w0-9-]+\s*:\s*[\w0-9.\s]+\s*\]")


def cast_element(value, value_type):
    parsed_value = value
    if value_type == TYPE_NUMBER:
        parsed_value = float(parsed_value)
    elif value_type == TYPE_INTEGER:
        parsed_value = int(float(parsed_value))
    elif value_type == TYPE_STRING:
        parsed_value = str(parsed_value)
    elif value_type == TYPE_BOOLEAN:
        if (
            not isinstance(parsed_value, str)
            and not isinstance(parsed_value, str)
            and not isinstance(parsed_value, bool)
        ):
            raise ValueError(
                "Wrong type: value '{}', needs to be boolean or string, instead of {}".format(
                    parsed_value, type(parsed_value)
                )
            )

        if isinstance(parsed_value, str):
            to_lower = str(parsed_value).lower()
            if to_lower == "true":
                parsed_value = True
            elif to_lower == "false":
                parsed_value = False

    return parsed_value


def get_tags_from_name(name):
    tags_result = {}
    tags: List[Any] = tag_detector.findall(name)
    for tag in tags:
        # Remove brackets from tag
        tag_str = str(tag)[1:-1]
        tag_name, tag_value = tag_str.split(sep=SEPARATOR)
        tag_name = tag_name.strip()
        tag_value = tag_value.strip()

        if tag_name in tags_result:
            raise ValueError(f"Found TAG [{tag_name}] repeated in name")

        if tag_name not in TAGS_SUPPORTED.keys():
            raise ValueError(f"Found unsupported TAG [{tag_name}] in {name}")

        tag_type = TAGS_SUPPORTED[tag_name]
        tags_result[tag_name] = cast_element(tag_value, tag_type)

    return tags_result
