import copy
import json

from enum import Enum

from spine_json_lib.data.constants import SPINE_3_8_VERSION
from spine_json_lib.data.spine_version_type import SpineVersion
from spine_json_lib.graph.spamnode import SpamNode, DEFAULT_NODE_TYPE
from spine_json_lib.graph.factories import INodeFactory, IGraphParser
from spine_json_lib.graph.dagraph import DAGraph
from typing import Any
from typing import Dict
from typing import Optional


class NodeType(Enum):
    """
    If you want to iterate this as if were an array just add this:
    __order__ = 'DEFAULT BONE SLOT ....'
    """

    DEFAULT = DEFAULT_NODE_TYPE
    BONE = 1
    SLOT = 2
    PATH = 3
    IK = 4
    ATTACHMENT = 5


SPINE_JSON_MAPPED_IDS = {"BONE": "bones", "SLOT": "slots", "IK": "ik"}


class SpineNodeFactory(INodeFactory):
    def create_node(
        self,
        node_type: str,
        node_id: str,
        order: int,
        node_data: Dict[str, Any] = None,
        public_id: Optional[str] = None,
    ) -> SpamNode:
        created_node = None
        if node_type == NodeType.BONE.name:
            created_node = SpamNode(
                id_value=node_id,
                data=node_data,
                node_type=NodeType.BONE.name,
                children_types_forbidden=[NodeType.ATTACHMENT.name],
                order=order,
            )
        elif node_type == NodeType.SLOT.name:
            created_node = SpamNode(
                id_value=node_id,
                data=node_data,
                node_type=NodeType.SLOT.name,
                children_types_forbidden=[
                    NodeType.BONE.name,
                    NodeType.PATH.name,
                    NodeType.IK.name,
                ],
                order=order,
            )
        elif node_type == NodeType.IK.name:
            created_node = SpamNode(
                id_value=node_id,
                data=node_data,
                node_type=NodeType.IK.name,
                children_types_forbidden=[
                    NodeType.PATH.name,
                    NodeType.IK.name,
                    NodeType.ATTACHMENT.name,
                ],
                order=order,
            )
        elif node_type == NodeType.ATTACHMENT.name:
            created_node = SpamNode(
                id_value=node_id,
                data=node_data,
                node_type=NodeType.ATTACHMENT.name,
                children_types_forbidden=[_type.name for _type in list(NodeType)],
                order=order,
            )

        return created_node


class SpineNodeData(object):
    def __init__(
        self,
        node_data: Dict[str, Any],
        node_type: NodeType,
        node_base_id: str,
        idx: int = -1,
    ) -> None:
        node_graph_id = SpineGraphParser._to_graph_id(
            node_type_name=node_type.name, node_base_id=node_base_id
        )
        # Adding idx to node_data
        _node_data = copy.deepcopy(node_data)
        _node_data = {"idx": idx, "data": _node_data}

        self.node_type = node_type.name
        self.node_id = node_graph_id
        self.node_data = _node_data


class SpineGraphParser(IGraphParser):
    @classmethod
    def create_from_json_file(
        cls, json_file: str, node_factory: SpineNodeFactory
    ) -> DAGraph:
        # Parse json
        with open(json_file) as f:
            json_data = json.load(f)

        return SpineGraphParser.create_from_json_data(
            json_data=json_data, node_factory=node_factory
        )

    @classmethod
    def to_json(cls, graph: DAGraph) -> str:
        return json.dumps(cls.to_json_data(graph))

    @classmethod
    def to_json_data(cls, graph: DAGraph) -> Dict[str, Any]:
        json_result: Dict[str, Any] = {"slots": [], "bones": [], "ik": []}

        for node_id, node in graph._nodes.items():
            # IMPORTANT: We ignore attachments when generating json from graph
            if node.node_type is NodeType.ATTACHMENT.name:
                continue

            node_type_json_key = SPINE_JSON_MAPPED_IDS[str(node.node_type)]
            # IMPORTANT: Erase the reference of default attachments already erased from the slots
            if (
                node.node_type is NodeType.SLOT
                and "attachment" in node._data
                and SpineGraphParser._to_graph_id(
                    node_type_name=NodeType.ATTACHMENT.name,
                    node_base_id=node._data["attachment"],
                )
                not in node.children.keys()
            ):
                del node._data["attachment"]

            json_result[node_type_json_key].append(node._data)

        # Sort by ids
        for _, json_id in SPINE_JSON_MAPPED_IDS.items():
            if not json_result.get(json_id):
                continue
            json_result[json_id] = sorted(
                json_result[json_id], key=lambda node_data: node_data["idx"]
            )
            json_result[json_id] = [
                node_info["data"] for node_info in json_result[json_id]
            ]
        return json_result

    @classmethod
    def create_from_json_data(
        cls, json_data: Dict[str, Any], node_factory: SpineNodeFactory
    ) -> DAGraph:
        graph = DAGraph(node_factory)

        for idx, bone_data in enumerate(json_data["bones"]):
            node_data = SpineNodeData(
                node_data=bone_data,
                node_type=NodeType.BONE,
                node_base_id=bone_data["name"],
                idx=idx,
            )
            graph.add_node(
                node_type=node_data.node_type,
                node_id=node_data.node_id,
                node_data=node_data.node_data,
            )

            # Getting optional parent from bone
            parent_id = SpineGraphParser._to_graph_id(
                node_type_name=NodeType.BONE.name, node_base_id=bone_data.get("parent")
            )
            parent = graph.get_node(parent_id)
            if parent:
                graph.add_edge(parent.id, node_data.node_id)

        slots_json_data = json_data.get("slots", [])
        for idx, _slot_data in enumerate(slots_json_data):
            spine_slot_data = SpineNodeData(
                node_data=_slot_data,
                node_type=NodeType.SLOT,
                node_base_id=_slot_data["name"],
                idx=idx,
            )

            graph.add_node(
                node_type=spine_slot_data.node_type,
                node_id=spine_slot_data.node_id,
                node_data=spine_slot_data.node_data,
            )

            def add_slot_skinned_to_graph(graph, slot_skinned):
                for _id in slot_skinned:
                    _data = slot_skinned[_id]
                    attachment_data = SpineNodeData(
                        node_data=_data,
                        node_type=NodeType.ATTACHMENT,
                        node_base_id=_data.get("path") or _data.get("name") or _id,
                    )

                    if graph.get_node(attachment_data.node_id) is None:
                        graph.add_node(
                            node_type=attachment_data.node_type,
                            node_id=attachment_data.node_id,
                            node_data=attachment_data.node_data,
                        )
                    graph.add_edge(spine_slot_data.node_id, attachment_data.node_id)

            # Adding attachments as child to slots differentiating between versions:
            for data in json_data["skins"]:
                skin_data = data.get("attachments")
                if skin_data:
                    slot_skinned = skin_data.get(_slot_data["name"], [])

                    add_slot_skinned_to_graph(graph=graph, slot_skinned=slot_skinned)

            # Getting optional parents from slot
            parent_id = SpineGraphParser._to_graph_id(
                node_type_name=NodeType.BONE.name, node_base_id=_slot_data.get("bone")
            )
            parent = graph.get_node(parent_id)
            if parent:
                graph.add_edge(parent.id, spine_slot_data.node_id)

        iks = json_data.get("ik", [])
        for idx, ik_data in enumerate(iks):
            spine_ik_data = SpineNodeData(
                node_data=ik_data,
                node_type=NodeType.IK,
                node_base_id=ik_data["name"],
                idx=idx,
            )
            graph.add_node(
                node_type=spine_ik_data.node_type,
                node_id=spine_ik_data.node_id,
                node_data=spine_ik_data.node_data,
            )

            # Getting optional parents for ik
            for child_bone_id in ik_data["bones"]:
                child_id = SpineGraphParser._to_graph_id(
                    node_type_name=NodeType.BONE.name, node_base_id=child_bone_id
                )
                child = graph.get_node(child_id)
                if child:
                    graph.add_edge(spine_ik_data.node_id, child.id)

            target_bone = ik_data.get("target")
            if target_bone:
                parent_bone_id = SpineGraphParser._to_graph_id(
                    node_type_name=NodeType.BONE.name, node_base_id=target_bone
                )
                parent_bone = graph.get_node(parent_bone_id)
                if parent_bone:
                    graph.add_edge(parent_bone.id, spine_ik_data.node_id)

        return graph

    @staticmethod
    def _to_graph_id(node_type_name: str, node_base_id: Optional[str]) -> str:
        """
        Convert to Graph Id to avoid cases like Slots and Bones with the same ids
        :return:
        """
        _suffix = NodeType[node_type_name].name
        return "{}_{}".format(node_base_id, _suffix)

    @staticmethod
    def _to_base_id(node_type_name, graph_id):
        _suffix = "_{}".format(NodeType[node_type_name].name)
        return graph_id.replace(_suffix, "")
