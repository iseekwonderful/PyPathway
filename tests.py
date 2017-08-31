import unittest
from pypathway import PublicDatabase as Database, STRING, BioGRID, ColorectalCancer
from pypathway import GSEA, SPIA, Enrichnet, KEGG
from pypathway import MAGI, Hotnet2
from pypathway import GMTUtils, IdMapping


class TestNetworkProcess(unittest.TestCase):
    def test_kegg(self):
        p = Database.search_kegg("jak")[0].load()
        self.assertTrue(p is not None)

    def test_reactome(self):
        p = Database.search_reactome("jak")[0].load()
        self.assertTrue(p is not None)

    def test_wikipathway(self):
        p = Database.search_wp("jak")[0].load()
        self.assertTrue(p is not None)

    def test_string(self):
        G = STRING.search("CD22")[0].load()
        self.assertTrue(hasattr(G, 'plot'))

    def test_biogrid(self):
        G = BioGRID.search("CD22")
        self.assertTrue(hasattr(G, 'plot'))


class TestAnalysis(unittest.TestCase):
    def test_ora(self):
        c = ColorectalCancer()
        r = KEGG.run(c.deg_list, c.background, organism='hsa')
        self.assertTrue(r is not None)

    def test_gsea(self):
        pass

    def test_spia(self):
        pass


class TestUtils(unittest.TestCase):
    def test_id_mapping(self):
        pass

    def test_gmt_utils(self):
        pass

    def test_load_sample_network(self):
        pass


class ModellingTest(unittest.TestCase):
    def test_pathway_select(self):
        pass

    def test_cluster(self):
        pass

    def test_make_network_file(self):
        pass

    def test_make_heat_file(self):
        pass

    def test_run_hotnet2(self):
        pass


