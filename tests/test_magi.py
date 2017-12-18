import unittest
import pickle
from itertools import combinations as cm
import os
from pypathway import MAGI


class MAGITest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(MAGITest, self).__init__(*args, **kwargs)
        if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/../pypathway/tests/magi_files/adj1.csv.Tab.BinaryFormat"):
            self.read_compressed_coExpression_network()

    def read_compressed_coExpression_network(self):
        path_compress = os.path.dirname(os.path.realpath(__file__)) + "/../pypathway/tests/magi_files/test.bin"
        path_id = os.path.dirname(os.path.realpath(__file__)) + "/../pypathway/tests/magi_files/GeneCoExpresion_ID.txt"
        # read the index
        indexs, out = {}, ""
        with open(path_id) as fp:
            for x in fp.read().split("\n"):
                if not x: continue
                i, _, v = x.split("\t")
                indexs[v] = int(i) - 1
        with open(path_compress, "rb") as fp:
            mat = pickle.load(fp)
        for x, y in cm(indexs.keys(), 2):
            value = max(mat[indexs[x]][indexs[y]], mat[indexs[y]][indexs[x]])
            out += "{}\t{}\t{}\n".format(x, y, value)
        with open(os.path.dirname(os.path.realpath(__file__)) + "/../pypathway/tests/magi_files/adj1.csv.Tab.BinaryFormat", "w") as fp:
            fp.write(out)

    def test_pathway_select(self):
        path = os.path.dirname(os.path.realpath(__file__)) + "/../pypathway/tests/magi_files/"
        MAGI.select_pathway(
            path + 'StringNew_HPRD.txt',
            path + 'ID_2_Autism_4_Severe_Missense.Clean_WithNew.txt',
            path + 'GeneCoExpresion_ID.txt', path + 'adj1.csv.Tab.BinaryFormat',
            path + 'New_ESP_Sereve.txt',
            path + 'Gene_Name_Length.txt'
        )

    def test_cluster(self):
        path = os.path.dirname(os.path.realpath(__file__)) + "/../pypathway/tests/magi_files/"
        r = MAGI.cluster(
            path + 'StringNew_HPRD.txt', path + 'GeneCoExpresion_ID.txt',
            path + 'adj1.csv.Tab.BinaryFormat', 10, 5, 200, 0.3
        )


if __name__ == '__main__':
    unittest.main()
