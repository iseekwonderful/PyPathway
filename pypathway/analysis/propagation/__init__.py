import networkx as nx
import numpy as np
import copy


def random_walk(G: nx.Graph, heat: dict, n: int = -1, threshold: float = 1e-6) -> nx.Graph:
    '''
    Perform the random walk algorithm in a Graph object G and heat for n repeats

    :param G: the undirected graph G
    :param heat: the heat dict, should have same length with G, contain the node name and the heat value
    :param n: the repeat time
    :param threshold: the threshold to check the convergence of the heat, if not n == -1, the loop will stop when the
    threshold is reached
    :return: the graph with heat property in the node's property
    '''
    mat = nx.to_numpy_matrix(G)
    A = _l1_norm(mat)
    r = A
    heat_vector = np.array([heat[x] for x in G.nodes])
    last_but_one = heat_vector.copy()
    n = 1e6 if n == -1 else n
    for i in range(int(n)):
        heat_vector = np.dot(heat_vector, A)
        if np.linalg.norm(np.subtract(last_but_one, heat_vector), 1) < threshold:
            break
        last_but_one = heat_vector.copy()
        # r = np.dot(r, A)
    h = np.dot(heat_vector, r)
    GG = copy.deepcopy(G)
    for n, v in zip(list(GG.nodes), h):
        GG.nodes[n]['heat'] = v
    return GG


def random_walk_with_restart(G: nx.Graph, heat: dict, rp: float, n: int = -1, threshold: float = 1e-6) -> nx.Graph:
    '''
    Perform the random walk with restart algorithm in a Graph object G and heat toward stable state

    :param G: the undirected graph G
    :param heat: the heat dict, should have same length with G, contain the node name and the heat value
    :param rp: restart probability.
    :param n: the repeat times, if n is -1, it will seek the steady state
    :param threshold: the threshold to check the convergence of the heat, if not n == -1, the loop will stop when the
    threshold is reached
    :return: the graph with heat property in the node's property
    '''
    mat = nx.to_numpy_matrix(G)
    A = _l1_norm(mat)
    heat_vector = np.array([heat[x] for x in G.nodes])
    if n == -1:
        I = np.eye(len(G.nodes))
        sim = rp * np.linalg.inv(I - (1 - rp) * A)
        h = np.dot(heat_vector, sim)
    else:
        h_zero = copy.deepcopy(heat_vector)
        last_but_one = heat_vector.copy()
        for i in range(n):
            heat_vector = h_zero * rp + (1 - rp) * np.dot(heat_vector, A)
            if np.linalg.norm(np.subtract(last_but_one, heat_vector), 1) < threshold:
                break
            last_but_one = heat_vector.copy()
        h = heat_vector
    GG = copy.deepcopy(G)
    for n, v in zip(list(GG.nodes), h):
        GG.nodes[n]['heat'] = v
    return GG


def diffusion_kernel(G: nx.Graph, heat: dict, rp: float, n: int) -> nx.Graph:
    '''
    Perform the diffusion kernel algorithm in a Graph object G and heat toward stable state

    :param G: the undirected graph G
    :param heat: the heat dict, should have same length with G, contain the node name and the heat value
    :param n: the repeat times
    :param rp: restart probability.
    :param threshold: the threshold to check the convergence of the heat, if not n == -1, the loop will stop when the
    threshold is reached
    :return: the graph with heat property in the node's property
    '''
    heat_vector = np.array([heat[x] for x in G.nodes])
    A = nx.to_numpy_matrix(G)
    D = np.diag(list(dict(G.degree()).values()))
    L = D - A
    I = np.eye(len(G))
    sim = (I - rp * L / n) ** n
    h = np.dot(heat_vector, np.array(sim))
    GG = copy.deepcopy(G)
    for n, v in zip(list(GG.nodes), h):
        GG.nodes[n]['heat'] = v
    return GG


def _l1_norm(array):
    array = np.copy(array)
    array = np.transpose(array)
    for i in range(array.shape[0]):
        array[i] = array[i] / np.sum(array[i])
    return array

