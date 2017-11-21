import unittest
import networkx as nx
import numpy as np
from pypathway import random_walk, random_walk_with_restart, diffusion_kernel


class TestPropagation(unittest.TestCase):
    def test_random_walk(self):
        '''
        Test random walk

        :return:
        '''
        G = nx.Graph([[1, 2], [2, 3], [3, 5], [2, 5], [1, 4], [4, 5]])
        h = np.array([0, 1, 0, 1, 0])
        r = random_walk(G, h)
        self.assertAlmostEqual(r.node[1]['heat'], 0.3333, 4)

    def test_RWR(self):
        '''
        Test random walk with restart

        :return:
        '''
        G = nx.Graph([[1, 2], [2, 3], [3, 5], [2, 5], [1, 4], [4, 5]])
        h = np.array([0, 1, 0, 1, 0])
        r = random_walk_with_restart(G, h, rp=0.7)
        self.assertAlmostEqual(r.node[1]['heat'], 0.1886, 4)

    def test_heat_kernel(self):
        '''
        Test diffusion kernel

        :return:
        '''
        G = nx.Graph([[1, 2], [2, 3], [3, 5], [2, 5], [1, 4], [4, 5]])
        h = np.array([0, 1, 0, 1, 0])
        r = diffusion_kernel(G, h, rp=0.7, n=100)
        self.assertAlmostEqual(r.node[1]['heat'], 0.4172, 4)

if __name__ == '__main__':
    unittest.main()