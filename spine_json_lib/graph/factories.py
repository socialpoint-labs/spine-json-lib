import abc

from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from spine_json_lib.graph.spamnode import SpamNode


class INodeFactory(object):
    """
    This is an ABSTRACT class
    You need to extend this for de/serializing Graphs
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create_node(self, node_type, node_id, order, node_data=None, public_id=None):
        raise NotImplementedError


class IGraphParser(object):
    """
    This is an ABSTRACT class
    You need to extend this for de/serializing Graphs
    """

    __metaclass__ = abc.ABCMeta

    @classmethod
    def create_from_json_data(
        cls, json_data: Optional[Dict], node_factory: INodeFactory
    ) -> None:
        raise NotImplementedError

    @classmethod
    def create_from_json_file(
        cls, json_file: Optional[str], node_factory: INodeFactory
    ) -> None:
        raise NotImplementedError

    @classmethod
    def to_json(cls, graph: Optional[Any]) -> None:
        raise NotImplementedError

    @classmethod
    def to_json_data(cls, graph):
        raise NotImplementedError


class DefaultNodeFactory(INodeFactory):
    """ Simple Node Factory in charge of creating nodes. """

    def create_node(
        self,
        node_type: Union[None, int, str],
        node_id: str,
        order: int,
        node_data: Any = None,
        public_id: Optional[str] = None,
    ) -> SpamNode:
        return SpamNode(
            id_value=node_id, data=node_data, node_type=node_type, order=order
        )
