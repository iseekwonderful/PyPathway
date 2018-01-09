import unittest
import pickle
from itertools import combinations as cm
import os

import sys
sys.path.insert(0, "/Users/yangxu/PyPathway")

import pypathway as pt
from pypathway import MAGI


class MAGITest(unittest.TestCase):
    def test_a_pathway_select(self):
        path = os.path.dirname(os.path.realpath(__file__)) + "/assets/smaller_magi/"
        MAGI.select_pathway(
            path + 'StringNew_HPRD.txt',
            path + 'ID_2_Autism_4_Severe_Missense.Clean_WithNew.txt',
            path + 'GeneCoExpresion_ID.txt', path + 'adj1.csv.Tab.BinaryFormat',
            path + 'New_ESP_Sereve.txt',
            path + 'Gene_Name_Length.txt',
            rand_seed=10
        )
        # check if we ge right result
        cache_dir = os.path.dirname(pt.__file__) + "/analysis/modelling/cache/"
        with open(cache_dir + "RandomGeneList.0") as fp:
            self.assertTrue(fp.read().split("\n")[1] == "RUVBL1 3.761159 0 1 0 1768")


    def test_b_cluster(self):
        print(pt.__file__)
        print("we now test clustering")
        path = os.path.dirname(os.path.realpath(__file__)) + "/assets/smaller_magi/"
        r = MAGI.cluster(
            path + 'StringNew_HPRD.txt', path + 'GeneCoExpresion_ID.txt',
            path + 'adj1.csv.Tab.BinaryFormat', 10, 5, 20, 0.3
        )
        print(set(r[0].genes.keys()))
        self.assertAlmostEqual(float(r[0].genes['CTNNB1']['weightCases']), 6.503305)


if __name__ == '__main__':
    unittest.main()
