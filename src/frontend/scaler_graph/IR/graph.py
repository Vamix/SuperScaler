'''
Use graph as intermediate representation for parallelizer.
You can utilize adapters to convert tensorflow graph, nnfusion graph, etc.
to our graphs, then take modifications for parallelisms.
'''
import json

from frontend.scaler_graph.IR.node import Node
from frontend.scaler_graph.IR.edge import Edge
from frontend.scaler_graph.IR.util import graph_util, serialization


class Graph:
    '''
    The intermediate graph
    '''
    _ID = 0

    def __init__(self):
        self.id = self._ID
        self.__class__._ID += 1
        self._nodes = []
        self._edges = []  # including data edges and control edges
        self._attrs = {}
        # the following data need to be updated when nodes adding/removing.
        self._name_to_node = {}
        self._STALE_COLLECTIONS = False
        self._collections = {}  # collections of nodes, e.g. apply, parameters
        self._STALE_ORDERED_NODES = False
        self._ordered_nodes = None

    @property
    def nodes(self):
        '''Return an unsorted list of nodes
        '''
        return self._nodes

    @property
    def ordered_nodes(self):
        '''Return a topologically sorted list of nodes.
        '''
        if not self._STALE_ORDERED_NODES:
            return self._ordered_nodes
        self._ordered_nodes = graph_util.reverse_DFS(self)
        self._STALE_ORDERED_NODES = False
        return self._ordered_nodes

    @property
    def edges(self):
        return self.edges

    def set_attr(self, name, value):
        self._attrs[name] = value

    @property
    def attrs(self):
        return self._attrs

    def get_node_by_name(self, name):
        return self._name_to_node.get(name, None)

    def add_node_and_edge(self, node_name, op, input_node_idxes, output_size,
                          attrs):
        '''Add a node into this graph, including all edges to it.
        '''
        if self.get_node_by_name(node_name) is not None:
            raise Exception("node %s is exising." % (node_name))
        self._STALE_COLLECTIONS = True
        self._STALE_ORDERED_NODES = True
        node = Node(node_name, op, input_node_idxes, output_size, attrs)
        for i, input_node_idx in enumerate(input_node_idxes):
            (input_node, idx) = input_node_idx
            edge = Edge(input_node, idx, node, i)
            self._edges.append(edge)
            node.add_in_edge(edge)
            input_node.add_out_edge(edge)
        self._nodes.append(node)
        self._name_to_node[node_name] = node
        return node

    def remove_node_and_edge(self, node):
        '''Remove a node from this graph, including all edges from or to it.
        '''
        self._STALE_COLLECTIONS = True
        self._STALE_ORDERED_NODES = True
        for edge in node.in_edges:
            edge.src_node.out_edges.remove(edge)
            node.in_edges.remove(edge)
            self._edges.remove(edge)
        for edge in node.out_edges:
            edge.dest_node.in_edges.remove(edge)
            node.out_edges.remove(edge)
            self._edges.remove(edge)
        self._name_to_node.pop(node.name)
        self._nodes.remove(node)

    def get_collection(self, collection_name):
        if not self._STALE_COLLECTIONS:
            return self._collections[collection_name]
        else:
            # TODO(gbxu): update collections
            self._STALE_COLLECTIONS = False
            pass

    def infer_shape(self):
        for node in self.ordered_nodes:
            node.infer_shape()

    def dict(self):
        nodes = [node.dict() for node in self.nodes]
        return dict(
            nodes=sorted(nodes, key=lambda node: node["name"]),
            attrs=dict(self._attrs),
        )

    def json(self):
        return json.dumps(self.dict(),
                          indent=4,
                          cls=serialization.AttrEnconding,
                          sort_keys=True)