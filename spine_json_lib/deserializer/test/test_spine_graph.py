import json
import os

import pytest

from spine_json_lib.deserializer.spine_nodes import (
    SpineNodeFactory,
    SpineGraphParser,
)
from typing import Any
from typing import Dict

SPINE_JSON_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data/spine_json_example.json"
)


@pytest.fixture
def spine_node_factory():
    return SpineNodeFactory()


@pytest.fixture
def spine_json_data() -> Dict[str, Any]:
    with open(SPINE_JSON_PATH) as f:
        json_data = json.load(f)
    return json_data


def orderer(obj):
    if isinstance(obj, dict):
        return sorted((k, orderer(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(orderer(x) for x in obj)
    else:
        return obj


class TestSpineGraph:
    def test_spine_graph_creation(self, spine_node_factory, spine_json_data):
        """
        Create a graph from spine_json an generate the json from graph and check if it is equal to original

        :param spine_node_factory:
        :param spine_json_data:
        :return:
        """
        graph = SpineGraphParser.create_from_json_file(
            json_file=SPINE_JSON_PATH, node_factory=spine_node_factory
        )
        graph_json_data = json.loads(SpineGraphParser.to_json(graph=graph))

        json_data_to_compare = {}
        for key, value in graph_json_data.items():
            json_data_to_compare[str(key)] = spine_json_data[str(key)]

        # Comparing de-serialised json with the original one
        assert orderer(json_data_to_compare) == orderer(graph_json_data)
