from typing import Union, Any, TypeVar

DEFAULT_NODE_TYPE = 0
CIRCULAR_PARENTSHIP_NODE_ERROR = "A node cannot be its own {}"
PARENTSHIP_TO_NO_NODE = "{} needs to be a node"
CHILD_TYPE_FORBIDDEN = "The type of the child is forbidden for this node"

EXECUTED = "EXECUTED"
PENDING = "PENDING"


SpamNodeType = TypeVar("SpamNodeType", bound="SpamNode")


class SpamNode(object):
    """
    This is a node base class to be used in the Graph as the main data container
    By default a node can have N number of children and M number of parents (N>=0, M>=0)
    """

    def __init__(
        self,
        id_value,
        order,
        data=None,
        node_type=None,
        children_types_forbidden=None,
        public_id=None,
    ):
        self._id = id_value
        self._data = data
        self._node_type = DEFAULT_NODE_TYPE if node_type is None else node_type
        self.public_id = id_value if public_id is None else public_id

        self.order = order
        self.state = EXECUTED

        if children_types_forbidden is None:
            children_types_forbidden = []
        self._child_types_forbidden = children_types_forbidden[:]

        self.children = {}
        self.parents = {}

    def __eq__(self, other):
        """Do this and other represent the same node? Comparing only by the id"""
        return self._id == other.id

    def __hash__(self):
        """ Used for finding the collision chain for this node."""
        return self._id

    @property
    def id(self) -> str:
        return self._id

    @property
    def node_type(self) -> Union[int, str]:
        return self._node_type

    @property
    def num_parents(self) -> int:
        return len(self.parents.keys())

    @property
    def num_children(self) -> int:
        return len(self.children.keys())

    @property
    def data(self) -> Any:
        return self._data

    def _add_parent(self, parent: SpamNodeType) -> None:
        """
        Adding a parent to this node

        You SHOULD NOT call this method directly. Instead call @add_edge to create relations between nodes.
        :param parent: A new parent for this node
        """
        if not issubclass(type(parent), SpamNode):
            raise TypeError(PARENTSHIP_TO_NO_NODE.format("parent"))

        if parent is self:
            raise ValueError(CIRCULAR_PARENTSHIP_NODE_ERROR.format("parent"))

        if parent.id not in self.parents:
            self.parents[parent.id] = parent

    def _add_child(self, child: SpamNodeType) -> None:
        """
        Adding a child to this node

        You SHOULD NOT call this method directly. Instead call @add_edge to create relations between nodes.
        :param child: 1 - Needs to be an instance with Node as "base class",
                      2 - The child type can't be in the list of forbidden child types.
        """
        if not issubclass(type(child), SpamNode):
            raise TypeError(PARENTSHIP_TO_NO_NODE.format("child"))

        if child.node_type in self._child_types_forbidden:
            raise TypeError(CHILD_TYPE_FORBIDDEN)

        if child is self:
            raise ValueError(CIRCULAR_PARENTSHIP_NODE_ERROR.format("child"))

        if child.id not in self.children:
            self.children[child.id] = child
