import pytest

from spine_json_lib.graph.graph_validator import GraphErrorType
from spine_json_lib.graph.spamnode import (
    SpamNode,
    CIRCULAR_PARENTSHIP_NODE_ERROR,
    PARENTSHIP_TO_NO_NODE,
    CHILD_TYPE_FORBIDDEN,
)
from spine_json_lib.graph.factories import INodeFactory, IGraphParser
from spine_json_lib.graph.dagraph import (
    DAGraph,
    UNIQUE_ID_ERROR_MESSAGE,
    WRONG_NODE_ID_TYPE,
    ID_NODE_NOT_FOUND,
)
from typing import Any
from typing import Optional
from typing import Dict

DEFAULT_ID = "UNIQUE_ID"
NODE_TYPE_BLOND = "BLOND"
NODE_TYPE_BROWN = "BROWN"
NODE_TYPE_BLACK = "BLACK"


@pytest.fixture
def node_factory():
    return NodeFactoryTest()


@pytest.fixture
def test_graph(graph_data: Dict[str, Any]) -> DAGraph:
    graph = DAGraph()

    node_types = graph_data.get("types", {})

    for node_id in graph_data["nodes"]:
        graph.add_node(node_id=node_id, node_type=node_types.get(node_id))
    [
        graph.add_edge(parent_id=edge[0], child_id=edge[1])
        for edge in graph_data["edges"]
    ]

    return graph


class NodeFactoryTest(INodeFactory):
    def create_node(
        self,
        node_type: int,
        node_id: str,
        order: int,
        node_data: Optional[Any] = None,
        public_id: Optional[str] = None,
    ) -> SpamNode:
        if node_type == NODE_TYPE_BLOND:
            created_node = SpamNode(
                id_value=node_id,
                data=node_data,
                node_type=node_type,
                children_types_forbidden=[NODE_TYPE_BLACK],
                order=order,
            )
        elif node_type == NODE_TYPE_BROWN:
            created_node = SpamNode(
                id_value=node_id, data=node_data, node_type=node_type, order=order
            )
        elif node_type == NODE_TYPE_BLACK:
            created_node = SpamNode(
                id_value=node_id,
                data=node_data,
                node_type=node_type,
                children_types_forbidden=[NODE_TYPE_BLOND],
                order=order,
            )
        else:
            created_node = SpamNode(
                id_value=node_id, data=node_data, node_type=node_type, order=order
            )
        return created_node


class TestGraph:
    def test_graph_nodes_creation(self, node_factory):
        graph = DAGraph(node_factory)

        node1 = graph.add_node(node_id=DEFAULT_ID)
        assert node1 is not None
        assert graph.get_node(node_id=DEFAULT_ID) is node1

        with pytest.raises(ValueError) as excinfo:
            graph.add_node(node_id=DEFAULT_ID, node_data=None)
        assert UNIQUE_ID_ERROR_MESSAGE in str(excinfo.value)

        graph.add_node(node_id="1", node_data=None)
        NUM_NODES = 1000
        for _ in range(0, NUM_NODES):
            id_ = graph.generate_unique_id()
            tmp_node = graph.add_node(node_id=id_)
            assert id_ is not DEFAULT_ID
            assert tmp_node is not None
            assert graph.get_node(node_id=id_) is tmp_node

            with pytest.raises(ValueError) as excinfo:
                graph.add_node(node_id=id_, node_data=None)
            assert UNIQUE_ID_ERROR_MESSAGE in str(excinfo.value)

            with pytest.raises(TypeError) as excinfo:
                graph.add_node(node_id=0)
            assert WRONG_NODE_ID_TYPE in str(excinfo.value)

            with pytest.raises(TypeError) as excinfo:
                graph.get_node(node_id=0)
            assert WRONG_NODE_ID_TYPE in str(excinfo.value)

    def test_graph_edges(self):
        graph = DAGraph()
        graph.add_node(node_id="0")
        graph.add_node(node_id="1")
        graph.add_edge(parent_id="0", child_id="1")

        with pytest.raises(TypeError) as excinfo:
            graph.add_edge(parent_id="0", child_id="wrong_id")
        assert PARENTSHIP_TO_NO_NODE.format("child") in str(excinfo.value)

        with pytest.raises(TypeError) as excinfo:
            graph.add_edge(parent_id="wrong_id", child_id="1")
        assert PARENTSHIP_TO_NO_NODE.format("parent") in str(excinfo.value)

    def test_graph_forbidden_child_types(self, node_factory):
        graph = DAGraph(node_factory)
        graph.add_node(node_id=NODE_TYPE_BLOND, node_type=NODE_TYPE_BLOND)
        graph.add_node(node_id=NODE_TYPE_BROWN, node_type=NODE_TYPE_BROWN)
        graph.add_node(node_id=NODE_TYPE_BLACK, node_type=NODE_TYPE_BLACK)
        graph.add_edge(parent_id=NODE_TYPE_BLOND, child_id=NODE_TYPE_BROWN)
        graph.add_edge(parent_id=NODE_TYPE_BLACK, child_id=NODE_TYPE_BROWN)

        with pytest.raises(TypeError) as excinfo:
            graph.add_edge(parent_id=NODE_TYPE_BLACK, child_id=NODE_TYPE_BLOND)
        assert CHILD_TYPE_FORBIDDEN in str(excinfo.value)

        with pytest.raises(TypeError) as excinfo:
            graph.add_edge(parent_id=NODE_TYPE_BLOND, child_id=NODE_TYPE_BLACK)
        assert CHILD_TYPE_FORBIDDEN in str(excinfo.value)

    def test_graph_remove_node(self):
        graph = DAGraph()
        graph.add_node(node_id=DEFAULT_ID)
        graph.remove_node_by_id(node_id=DEFAULT_ID)

        # Trying to remove already removed
        with pytest.raises(ValueError) as excinfo:
            graph.remove_node_by_id(node_id=DEFAULT_ID)
        assert ID_NODE_NOT_FOUND.format(DEFAULT_ID) in str(excinfo.value)

    def test_graph_multi_graphs(self, node_factory):
        graph1 = DAGraph(node_factory)
        graph2 = DAGraph(node_factory)

        id_ = graph1.generate_unique_id()
        node1 = graph1.add_node(node_id=id_)
        assert node1 is not None
        assert graph1.get_node(node_id=id_) is node1

        # Checking if also in graph2
        assert graph2.get_node(node_id=id_) is None

        # Creating two nodes with the same id in different graphs
        node2 = graph2.add_node(node_id=id_)
        assert node2 is not node1

        with pytest.raises(ValueError) as excinfo:
            graph1.add_edge(parent_id=id_, child_id=id_)
        assert CIRCULAR_PARENTSHIP_NODE_ERROR.format("child") in str(excinfo.value)

    @pytest.mark.parametrize(
        "graph_data, number_of_circular",
        [
            (
                {
                    "nodes": ["0", "1", "2"],
                    "edges": [("0", "1"), ("1", "2"), ("2", "0")],
                },
                3,
            ),
            (
                {
                    "nodes": ["0", "1", "2"],
                    "edges": [("0", "1"), ("1", "2"), ("1", "0")],
                },
                2,
            ),
        ],
    )
    def test_graph_circular_references(self, test_graph, number_of_circular):
        # Checking circular references nodes
        validation_result = test_graph.validate()
        circular_nodes = validation_result.errors[0][GraphErrorType.CIRCULAR_REFS.name]
        assert len(validation_result.errors) == 1 and isinstance(circular_nodes, list)
        assert len(circular_nodes) == number_of_circular

    @pytest.mark.parametrize(
        "graph_data",
        [
            {
                "nodes": ["1", "2", "3", "4"],
                "edges": [("1", "2"), ("2", "3"), ("3", "4")],
            }
        ],
    )
    def test_graph_heads(self, test_graph):
        heads = test_graph.get_heads_id()
        assert heads
        for node_id in heads:
            head_node = test_graph.get_node(node_id=node_id)
            assert head_node
            assert not head_node.parents

    @pytest.mark.parametrize(
        "graph_data",
        [
            {
                "nodes": ["1", "2", "3", "4"],
                "edges": [("1", "2"), ("2", "3"), ("3", "4")],
            }
        ],
    )
    def test_graph_tails(self, test_graph):
        tails = test_graph.get_tails_id()
        assert tails
        for node_id in tails:
            tail_node = test_graph.get_node(node_id=node_id)
            assert tail_node
            assert not tail_node.children

    @pytest.mark.parametrize(
        "graph_data, result_paths",
        [
            (
                {
                    "nodes": ["1", "2", "3", "4"],
                    "edges": [("1", "2"), ("2", "3"), ("3", "4")],
                    "types": {"1": "INPUT_ROOT_NODE_TYPE"},
                },
                [["1", "2", "3", "4"]],
            ),
            (
                {
                    "nodes": ["1", "2", "3", "4"],
                    "edges": [("1", "2"), ("2", "3"), ("2", "4"), ("3", "4")],
                    "types": {"1": "INPUT_ROOT_NODE_TYPE"},
                },
                [["1", "2", "3", "4"], ["1", "2", "4"]],
            ),
            (
                {
                    "nodes": ["1", "2", "3", "4"],
                    "edges": [
                        ("1", "2"),
                        ("2", "3"),
                        ("2", "4"),
                        ("3", "4"),
                        ("1", "4"),
                    ],
                    "types": {"1": "INPUT_ROOT_NODE_TYPE"},
                },
                [["1", "2", "3", "4"], ["1", "2", "4"], ["1", "4"]],
            ),
        ],
    )
    def test_graph_all_paths(self, test_graph, graph_data, result_paths):
        paths_found = test_graph.get_all_paths(
            graph_data["nodes"][0], graph_data["nodes"][-1]
        )

        assert paths_found and len(paths_found) > 0
        assert sorted(paths_found) == sorted(result_paths)

    @pytest.mark.parametrize(
        "graph_data, sequential_order_result",
        [
            #    3 --> 4
            #   ^     ^
            #  /     /
            # 1 --> 2
            (
                {
                    "nodes": ["1", "2", "3", "4"],
                    "edges": [("1", "2"), ("1", "3"), ("2", "3"), ("3", "4")],
                },
                ["1", "2", "3", "4"],
            ),
            # 1 --> 2 ---> 5 --> 7
            #  \          ^     ^
            #   \        /     /
            #    3 ---> 4     /
            #     \          /
            #      6 -------/
            (
                {
                    "nodes": ["1", "2", "3", "4", "5", "6", "7"],
                    "edges": [
                        ("1", "3"),
                        ("3", "4"),
                        ("4", "5"),
                        ("1", "2"),
                        ("2", "5"),
                        ("5", "7"),
                        ("3", "6"),
                        ("5", "6"),
                        ("6", "7"),
                    ],
                },
                ["1", "3", "4", "2", "5", "6", "7"],
            ),
        ],
    )
    def test_graph_sequential_order_execution(
        self, test_graph, sequential_order_result
    ):
        paths_found = test_graph.sequential_order_of_execution()

        assert paths_found and len(paths_found) > 0
        assert paths_found == sequential_order_result

    def test_graph_create_from_json_data_not_implemented(self, node_factory):
        graph_parser = IGraphParser()
        with pytest.raises(NotImplementedError):
            graph_parser.create_from_json_data(None, node_factory)

        with pytest.raises(NotImplementedError):
            DAGraph.create_from_json_data(IGraphParser, {}, node_factory)

        with pytest.raises(TypeError):
            DAGraph.create_from_json_data(object, {}, node_factory)

    def test_graph_to_json_not_implemented(self):
        graph_parser = IGraphParser()
        with pytest.raises(NotImplementedError):
            graph_parser.to_json(None)

    def test_graph_create_from_json_file(self, node_factory):
        graph_parser = IGraphParser()
        with pytest.raises(NotImplementedError):
            DAGraph.create_from_json_file(IGraphParser, "PATH", node_factory)

        with pytest.raises(NotImplementedError):
            graph_parser.create_from_json_file(None, node_factory)

        with pytest.raises(TypeError):
            DAGraph.create_from_json_file(object, "PATH", node_factory)
