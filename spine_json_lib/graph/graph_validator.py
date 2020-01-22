from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Set

from spine_json_lib.graph.spamnode import DEFAULT_NODE_TYPE
from spine_json_lib.graph.spamnode import SpamNode


class UCNodeType(Enum):
    """
    If you want to iterate this as if were an array just add this:
    __order__ = 'DEFAULT BONE SLOT ....'
    """

    DEFAULT = DEFAULT_NODE_TYPE
    ACTION_NODE_TYPE = 1
    PATH_PARAMETER_NODE_TYPE = 2
    INPUT_ROOT_NODE_TYPE = 3


class GraphErrorType(Enum):
    CIRCULAR_REFS = 0
    UNCONNECTED_NODES = 1


class GraphValidationErrors(object):
    def __init__(self) -> None:
        self.errors: List[Dict[str, List[str]]] = []

    def add_error(self, error: List[str], error_type: GraphErrorType) -> None:
        """
        :param error: The error data
        :param error_type: Needs to be of GraphErrorType
        :return:
        """
        if not isinstance(error_type, GraphErrorType):
            raise TypeError("The error type needs to be of type GraphErrorType")

        self.errors.append({error_type.name: error})


class GraphValidator(object):
    """
    This class is in charge of validating graphs following certain rules:
    like CIRCULAR_REFERENCES
    """

    def __init__(self) -> None:
        self.errors: GraphValidationErrors = None

    def validate(self, graph) -> GraphValidationErrors:
        """Execute the necessary validations over the graph and return an GraphValidationError"""
        self.errors = GraphValidationErrors()

        cycling_refs = self.get_circular_dependencies(graph=graph)
        if cycling_refs:
            self.errors.add_error(cycling_refs, GraphErrorType.CIRCULAR_REFS)

        unconnected_nodes = self.get_unconnected_nodes(graph=graph)
        if unconnected_nodes:
            self.errors.add_error(unconnected_nodes, GraphErrorType.UNCONNECTED_NODES)

        return self.errors

    @classmethod
    def get_unconnected_nodes(cls, graph) -> List:
        unconnected_nodes = []
        heads = graph.get_heads_id()
        for head_id in heads:
            # Check if there are any head and it is not a root of the UCGraph
            if (
                graph.get_node(head_id).node_type
                is not UCNodeType.INPUT_ROOT_NODE_TYPE.name
            ):
                unconnected_nodes.append(head_id)
                continue

        return unconnected_nodes

    @classmethod
    def get_circular_dependencies(cls, graph) -> List[Any]:
        """
        Check over every node if there are any cycling dependency
        :return: Return n lists of cycling references otherwise return a []
        """
        path = list()
        visited_nodes: Set = set()

        def visit(node: SpamNode) -> List:
            if node.id in visited_nodes:
                return []

            visited_nodes.add(node.id)
            path.append(node.id)

            for children_id, children in node.children.items():
                path_to_visit = visit(children)
                if children_id in path or path_to_visit:
                    path_to_visit += [children_id]
                    return path_to_visit
            path.pop()
            return []

        circle_references: List[Any] = []
        for node_id, node_data in graph._nodes.items():
            circle_references += visit(node_data)

        return list(reversed(circle_references))
