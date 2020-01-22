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

    def get_leaf_slots(self) -> List[str]:
        tail_nodes = self.graph.get_tails_id()

        leaf_slots = list(
            filter(
                lambda n: self.graph.get_node(n).node_type == NodeType.SLOT.name,
                tail_nodes,
            )
        )

        return leaf_slots

    def remove_empty_slots(self) -> Tuple[List[str], List[str]]:
        """
        Removing from graph every slot leaves of graph and return it
        """
        slots_removed = []
        empty_slots = self.get_leaf_slots()
        while empty_slots:
            slots_removed += [
                SpineGraphParser._to_base_id(
                    node_type_name=NodeType.SLOT.name,
                    graph_id=self.graph.remove_node_by_id(s_id).id,
                )
                for s_id in empty_slots
            ]

            empty_slots = self.get_leaf_slots()
        return slots_removed

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
