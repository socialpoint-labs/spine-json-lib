from typing import List, Dict, Any, Tuple

from spine_json_lib.deserializer.spine_nodes import (
    SpineGraphParser,
    SpineNodeFactory,
    NodeType,
)

from spine_json_lib.graph.spamnode import SpamNode


class SpineGraphContainer(object):
    def __init__(self, spine_json_data: Dict[str, Any]) -> None:
        self.graph = SpineGraphParser.create_from_json_data(
            json_data=spine_json_data, node_factory=SpineNodeFactory()
        )

    def get_heads_with_type(self, node_type):
        heads_nodes = self.graph.get_heads_id()

        return list(
            filter(
                lambda n: self.graph.get_node(n).node_type == node_type,
                heads_nodes,
            )
        )

    def remove_heads_of_type(self, type_name) -> List[str]:
        """
        Remove from graph every node that is a head of type @type_name recursively
        and return the list of ids
        """
        nodes_removed = []
        root_node = self.get_heads_with_type(node_type=type_name)
        while root_node:
            nodes_removed += [
                SpineGraphParser._to_base_id(
                    node_type_name=type_name,
                    graph_id=self.graph.remove_node_by_id(s_id).id,
                )
                for s_id in root_node
            ]

            root_node = self.get_heads_with_type(node_type=type_name)
        return nodes_removed

    def get_leafs_of_type(self, node_type) -> List[str]:
        tail_nodes = self.graph.get_tails_id()

        leaf_slots = list(
            filter(
                lambda n: self.graph.get_node(n).node_type == node_type,
                tail_nodes,
            )
        )

        return leaf_slots

    def remove_leafs_of_type(self, type_name) -> List[str]:
        """
        Removing from graph every node leaves of type @type_name recursively
        and return the list of ids
        """
        nodes_removed = []
        leaf_nodes = self.get_leafs_of_type(node_type=type_name)
        while leaf_nodes:
            nodes_removed += [
                SpineGraphParser._to_base_id(
                    node_type_name=type_name,
                    graph_id=self.graph.remove_node_by_id(s_id).id,
                )
                for s_id in leaf_nodes
            ]

            leaf_nodes = self.get_leafs_of_type(node_type=type_name)
        return nodes_removed

    def remove_attachment(self, attachment_id: str) -> SpamNode:
        attachment_node = self.graph.get_node(attachment_id)

        self.graph.remove_node_by_id(attachment_id)
        return attachment_node

    def remove_attachments(self, attachment_ids: List[str]) -> List[SpamNode]:
        removed_nodes = []
        for attachment_id in attachment_ids:
            graph_attachment_id = SpineGraphParser._to_graph_id(
                NodeType.ATTACHMENT.name, attachment_id
            )
            removed_node = self.remove_attachment(graph_attachment_id)
            removed_nodes.append(removed_node)
        return removed_nodes

    def remove_slots(self, slots_ids: List[str]) -> List[SpamNode]:
        removed_slots = []
        for slot_id in slots_ids:
            slot_graph_id = SpineGraphParser._to_graph_id(
                node_type_name=NodeType.SLOT.name, node_base_id=slot_id
            )
            slot = self.graph.remove_node_by_id(slot_graph_id)
            removed_slots.append(slot)
        return removed_slots
