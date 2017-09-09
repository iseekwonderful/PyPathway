from ......utils import _node
from ctypes import *
import networkx as nx
import sys
import numpy as np
import struct

sys.path.append('/Users/yangxu/PyPathway')


class Node(Structure):
    _fields_ = [("node_id", c_int),
                ('neighbours', POINTER(c_int)),
                ("neighbour_count", c_int)]

    def __repr__(self):
        return "id: {} nei_c {}, neis: {}".format(self.node_id, self.neighbour_count, self.neighbours)


def nx2c(G):
    res = []
    for k, v in G.edge.items():
        nei = (c_int * len(v))(*[x for x in v])
        n = Node(node_id=k, neighbours=nei, neighbour_count=len(v))
        res.append(n)
    return (Node * len(G.edge))(*res)


def c2nx(r):
    G = nx.Graph()
    for x in r.contents:
        for i in range(x.neighbour_count):
            G.add_edge(x.node_id, x.neighbours[i])
    return G


def translate(Graph):
    '''
    From networkx graph to adjacency matrix

    :param Graph: the input graph
    :return the id2node dict and the adjancency matrix
    '''
    length = len(Graph.node)
    id2_node = {}
    adjacency = np.zeros((length, length), dtype=np.int8)
    for i, n in enumerate(Graph.node):
        id2_node[int(n)] = i
    for x in Graph.edges():
        i1, i2 = id2_node[int(x[0])], id2_node[int(x[1])]
        adjacency[i1][i2] = 1
        adjacency[i2][i1] = 1
    ids = list(id2_node.keys())
    id_list = (c_int * len(ids))(*ids)
    return id_list, adjacency, length


def parse_adjacency_matrix(id2name, matrix, count):
    ids = struct.unpack('i' * count, id2name)
    id2node = {i: x for i, x in enumerate(ids)}
    rG = nx.Graph()
    for i, j in zip(*np.where(matrix > 0)):
        rG.add_edge(str(id2node[i]), str(id2node[j]))
    return rG


def node_swap(G, nswap, windows_threshold=3):
    id2node, matrix, count = translate(G)
    ids, mat, count = _node.swap(id2node, matrix, count, int(nswap), windows_threshold)
    NG = parse_adjacency_matrix(ids, mat, count)
    return NG