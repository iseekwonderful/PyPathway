import networkx as nx
import numpy as np
import scipy.linalg as la
import copy


def random_walk(G: nx.Graph, heat: list, n: int = -1, threshold: float = 1e-6) -> nx.Graph:
    '''
    Perform the random walk algorithm in a Graph object G and heat for n repeats

    :param G: the undirected graph G
    :param heat: the heat vector, should have same length with G
    :param n: the repeat time
    :param threshold: the threshold to check the convergence of the heat, if not n == -1, the loop will stop when the
    threshold is reached
    :return: the graph with heat property in the node's property
    '''
    mat = nx.to_numpy_matrix(G)
    A = _l1_norm(mat)
    r = A
    last_but_one = heat.copy()
    n = 1e6 if n == -1 else n
    for i in range(int(n)):
        heat = np.dot(heat, A)
        if np.linalg.norm(np.subtract(last_but_one, heat), 1) < threshold:
            break
        last_but_one = heat.copy()
        # r = np.dot(r, A)
    h = np.dot(heat, r)
    GG = copy.deepcopy(G)
    for n, v in zip(list(GG.node.keys()), h):
        GG.node[n]['heat'] = v
    return GG


def random_walk_with_restart(G: nx.Graph, heat: list, rp: float, n: int = -1, threshold: float = 1e-6) -> nx.Graph:
    '''
    Perform the random walk with restart algorithm in a Graph object G and heat toward stable state

    :param G: the undirected graph G
    :param heat: the heat vector, should have same length with G
    :param rp: restart probability.
    :param n: the repeat times, if n is -1, it will seek the steady state
    :param threshold: the threshold to check the convergence of the heat, if not n == -1, the loop will stop when the
    threshold is reached
    :return: the graph with heat property in the node's property
    '''
    mat = nx.to_numpy_matrix(G)
    A = _l1_norm(mat)
    if n == -1:
        I = np.eye(len(G.node))
        sim = rp * np.linalg.inv(I - (1 - rp) * A)
        h = np.dot(heat, sim)
    else:
        h_zero = copy.deepcopy(heat)
        last_but_one = heat.copy()
        for i in range(n):
            heat = h_zero * rp + (1 - rp) * np.dot(heat, A)
            if np.linalg.norm(np.subtract(last_but_one, heat), 1) < threshold:
                break
            last_but_one = heat.copy()
        h = heat
    GG = copy.deepcopy(G)
    for n, v in zip(list(GG.node.keys()), h):
        GG.node[n]['heat'] = v
    return GG


def diffusion_kernel(G: nx.Graph, heat: list, rp: float, n: int) -> nx.Graph:
    '''
    Perform the diffusion kernel algorithm in a Graph object G and heat toward stable state

    :param G: the undirected graph G
    :param heat: the heat vector, should have same length with G
    :param n: the repeat times
    :param rp: restart probability.
    :param threshold: the threshold to check the convergence of the heat, if not n == -1, the loop will stop when the
    threshold is reached
    :return: the graph with heat property in the node's property
    '''
    A = nx.to_numpy_matrix(G)
    D = np.diag(list(G.degree().values()))
    L = D - A
    I = np.eye(len(G))
    sim = (I - rp * L / n) ** n
    h = np.dot(heat, np.array(sim))
    GG = copy.deepcopy(G)
    for n, v in zip(list(GG.node.keys()), h):
        GG.node[n]['heat'] = v
    return GG


def _l1_norm(array):
    array = np.copy(array)
    array = np.transpose(array)
    for i in range(array.shape[0]):
        array[i] = array[i] / np.sum(array[i])
    return array

