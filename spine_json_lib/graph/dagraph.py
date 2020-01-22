from typing import Any, TypeVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from spine_json_lib.graph.factories import (
    INodeFactory,
    IGraphParser,
    DefaultNodeFactory,
)
from spine_json_lib.graph.graph_validator import GraphValidationErrors
from spine_json_lib.graph.graph_validator import GraphValidator
from spine_json_lib.graph.spamnode import DEFAULT_NODE_TYPE
from spine_json_lib.graph.spamnode import SpamNode

UNIQUE_ID_ERROR_MESSAGE = "The id of the node needs to be unique"
GRAPH_PARSER_WRONG_TYPE = "graph_parser param needs to implement IGraphFactory"
WRONG_NODE_ID_TYPE = "Only string type allowed for node_id param"
ID_NODE_NOT_FOUND = "Node with ID = {} was not found in the graph"
NODE_FACTORY_WRONG_TYPE = (
    "node_factory needs to be of a type that implements INodeFactory"
)

# Create a generic variable that can be 'DAGraph', or any subclass.
DAGraphType = TypeVar("DAGraphType", bound="DAGraph")


class DAGraph(object):
    """
    With this class you can do the following actions with Graphs:
     - Add or modify nodes.
     - Modify relation between nodes.
     - Construct a Graph from a JSON (You need an implementation of IGraphParser for this)
     - Generate a JSON from a Graph instance (You need an implementation of IGraphParser for this)

    INodeFactory:
     - You can use a "node_factory" to be able to customize the way your nodes are created.
     - The node_factory instance MUST be an instance derived from INodeFactory abstract class.
     - By default will use an DefaultNodeFactory

    IGraphParser:
     - If you want to serialize of deserialize (JSONs <-> Graphs) a graph you will need to use
     a graph_parser an instance of an implementation of IGraphParser

    """

    def __init__(self, node_factory=None):
        self.nodes_id_generator = 0
        self.nodes_counter = 0
        self._nodes = {}

        if node_factory is None:
            node_factory = DefaultNodeFactory()

        if (
            not issubclass(type(node_factory), INodeFactory)
            or type(node_factory) is INodeFactory
        ):
            raise TypeError(NODE_FACTORY_WRONG_TYPE)

        self.nodes_factory = node_factory

    def add_node(
        self,
        node_id: Union[None, int, str] = None,
        node_data: Union[Dict[str, Any], None] = None,
        node_type: Union[int, str] = DEFAULT_NODE_TYPE,
        public_id: Union[int, str, None] = None,
    ) -> SpamNode:
        """ Adding a new node to the graph """
        unique_id = self.generate_unique_id()
        if node_id is None:
            _id_node = unique_id
        else:
            if not isinstance(node_id, str):
                raise TypeError(WRONG_NODE_ID_TYPE)
            if node_id in self._nodes.keys():
                raise ValueError(UNIQUE_ID_ERROR_MESSAGE)
            _id_node = node_id

        new_node = self.nodes_factory.create_node(
            node_type=node_type,
            node_id=_id_node,
            node_data=node_data,
            public_id=public_id,
            order=unique_id,
        )

        self.nodes_counter += 1
        self._nodes[_id_node] = new_node
        return new_node

    def get_node(self, node_id: Union[int, str]) -> Optional[SpamNode]:
        """
        Find a node with certain id
        :param node_id:
        :return: the node instance
        """
        if not isinstance(node_id, str):
            raise TypeError(WRONG_NODE_ID_TYPE)

        return self._nodes.get(node_id)

    def add_edge(self, parent_id: str, child_id: str) -> None:
        """
        Add connection between two nodes
        :param parent_id:
        :param child_id:
        """
        node1 = self.get_node(parent_id)
        node2 = self.get_node(child_id)
        if node1:
            node1._add_child(node2)
        node2._add_parent(node1)

    def remove_edge(self, parent_id: str, child_id: str) -> None:
        node1 = self.get_node(parent_id)
        node2 = self.get_node(child_id)
        if node1:
            del node1.children[child_id]
        del node2.parents[parent_id]

    def remove_node_by_id(self, node_id: str) -> SpamNode:
        """Remove node with id == node_id from the graph"""

        node = self.get_node(node_id)
        if node is None:
            raise ValueError(ID_NODE_NOT_FOUND.format(node_id))

        for _, child in node.children.items():
            del child.parents[node_id]

        for _, parent in node.parents.items():
            del parent.children[node_id]

        del self._nodes[node_id]
        return node

    def generate_unique_id(self) -> str:
        """This generates an unique id for this Graph"""

        self.nodes_id_generator += 1
        while str(self.nodes_id_generator) in self._nodes.keys():
            self.nodes_id_generator += 1
        return str(self.nodes_id_generator)

    def get_all_paths(
        self, node_start: str, node_end: str, maximum_depth: int = 20
    ) -> List[List[str]]:
        """
        :param maximum_depth: how deep we want to go looking for possible paths
        :return: All the possible paths from node_start to node_end
                in the following format [[path1], [path2], ...]
        """
        errors = self.validate()

        if errors.errors:
            raise ValueError(
                "The current graph is invalid with the following errors {}".format(
                    errors.errors
                )
            )

        if node_start not in self._nodes.keys():
            raise ValueError(
                "Could not find the node with id: {} inside the graph".format(
                    node_start
                )
            )

        if node_end not in self._nodes.keys():
            raise ValueError(
                "Could not find the node with id: {} inside the graph".format(node_end)
            )

        paths = list()
        visited = set()

        def _look_for_paths(
            start: str, end: str, path: List[str], depth: int, graph: DAGraphType
        ) -> None:
            if depth > maximum_depth:
                return

            if start == end:
                paths.append(path + [start])
                return

            visited.add(start)
            path.append(start)

            for child_id in graph._nodes[start].children:
                if child_id not in visited:
                    _look_for_paths(
                        start=child_id, end=end, path=path, depth=depth + 1, graph=graph
                    )

            visited.remove(start)
            path.remove(start)

        _look_for_paths(
            start=node_start, end=node_end, path=list(), depth=1, graph=self
        )
        return paths

    def sequential_order_of_execution(self) -> List[str]:
        """
        :return: A list of nodes with a certain order of execution taking into account
                dependency between nodes to be able to execute them in this order
        """
        visited = set()

        result_nodes = []

        def visit(node: SpamNode) -> None:
            visited.add(node.id)

            for parent in node.parents:
                if parent not in visited:
                    visit(self.get_node(parent))

            result_nodes.append(node.id)
            for child in node.children:
                if child not in visited:
                    visit(self.get_node(child))

        for head_id in self.get_heads_id():
            visit(self.get_node(head_id))

        return result_nodes

    def get_heads_id(self) -> List[str]:
        """Iterate over every node and return the 'heads'(the ones with no parents)"""
        return self.__get_nodes("parents")

    def get_tails_id(self) -> List[str]:
        """Iterate over every node and return the 'tails'(the ones with no children)"""
        return self.__get_nodes("children")

    def __get_nodes(self, look_for):
        result_nodes = []
        visited = set()

        def visit(node: SpamNode) -> None:
            if node.id in visited:
                return

            visited.add(node.id)
            related_nodes = getattr(node, look_for)

            if not related_nodes:
                result_nodes.append(node.id)
                return

            for n_id, n in related_nodes.items():
                visit(n)

        for node_id, node_data in self._nodes.items():
            visit(node_data)

        return result_nodes

    def validate(self) -> GraphValidationErrors:
        """Execute the necessary validations over the graph and return the GraphValidationErrors"""
        return GraphValidator().validate(self)

    def to_json(self, graph_parser_cls):
        """
        Call this if you want to serialize a Graph object.
        :param graph_parser_cls: Class in charge of serializing graph objects.
        :return: graph object serialized
        """

        if (
            not issubclass(graph_parser_cls, IGraphParser)
            or graph_parser_cls is IGraphParser
        ):
            raise TypeError(GRAPH_PARSER_WRONG_TYPE)

        return graph_parser_cls.to_json(graph=self)

    def to_json_data(self, graph_parser_cls: IGraphParser) -> Dict[str, Any]:
        if (
            not issubclass(graph_parser_cls, IGraphParser)
            or graph_parser_cls is IGraphParser
        ):
            raise TypeError(GRAPH_PARSER_WRONG_TYPE)

        return graph_parser_cls.to_json_data(graph=self)

    @staticmethod
    def create_from_json_file(
        graph_parser_cls: IGraphParser, json_file: str, node_factory: INodeFactory
    ) -> DAGraphType:
        """
        - Call this static method to create a Graph from a json_file
        :param graph_parser_cls: The class deserializer -> Needs to implement IGraphParser
        :param json_file: path to json to deserialize
        :param node_factory: factory used to build the nodes in the graph
        :return: a new Graph instance
        """

        if not issubclass(graph_parser_cls, IGraphParser):
            raise TypeError(GRAPH_PARSER_WRONG_TYPE)

        return graph_parser_cls.create_from_json_file(
            json_file=json_file, node_factory=node_factory
        )

    @staticmethod
    def create_from_json_data(
        graph_parser_cls: IGraphParser, json_data: Dict, node_factory: INodeFactory
    ) -> DAGraphType:
        """
        - Call this static method to create a Graph from a json_data object
        :param graph_parser_cls: The class deserializer -> Needs to implement IGraphParser
        :param json_data: json data object
        :param node_factory: factory used to build the nodes in the graph

        :return: a new Graph instance
        """

        if not issubclass(graph_parser_cls, IGraphParser):
            raise TypeError(GRAPH_PARSER_WRONG_TYPE)

        return graph_parser_cls.create_from_json_data(
            json_data=json_data, node_factory=node_factory
        )
