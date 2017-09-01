import unittest
from pypathway import PublicDatabase as Database, STRING, BioGRID, ColorectalCancer
from pypathway import GSEA, SPIA, Enrichnet, KEGG
from pypathway import MAGI, Hotnet2
from pypathway import GMTUtils, IdMapping
from pypathway.utils import load_hint_hi12012_network
import pandas as pd
import os


# class TestNetworkProcess(unittest.TestCase):
#     def test_kegg(self):
#         p = Database.search_kegg("jak")[0].load()
#         self.assertTrue(p is not None)
#
#     def test_reactome(self):
#         p = Database.search_reactome("jak")[0].load()
#         self.assertTrue(p is not None)
#
#     def test_wikipathway(self):
#         p = Database.search_wp("jak")[0].load()
#         self.assertTrue(p is not None)
#
#     def test_string(self):
#         G = STRING.search("CD22")[0].load()
#         self.assertTrue(hasattr(G, 'plot'))
#
#     def test_biogrid(self):
#         G = BioGRID.search("CD22")
#         self.assertTrue(hasattr(G, 'plot'))


class TestAnalysis(unittest.TestCase):
    def test_ora(self):
        c = ColorectalCancer()
        r = KEGG.run(c.deg_list, c.background, organism='hsa')
        self.assertTrue(r is not None)

    def test_gsea(self):
        path = os.path.dirname(os.path.realpath(__file__)) + "/pypathway/tests/gsea_data/"
        phenoA, phenoB, class_vector = GSEA.parse_class_vector(path + "/GSE4107.cls")
        gene_exp = pd.read_excel(path + "/GSE4107.xlsx")
        r = GSEA.run(data=gene_exp.iloc[:1000], gmt="KEGG_2016", cls=class_vector)
        self.assertTrue(r is not None)

    def test_spia(self):
        c = ColorectalCancer()
        s = SPIA.run(c.deg, c.background)
        self.assertTrue(hasattr(s, 'plot'))

    def test_enrichnet_api(self):
        c = ColorectalCancer()
        sym = IdMapping.convert(input_id=c.deg_list, source='ENTREZID', target="SYMBOL", organism='hsa')
        sym = [x[1][0] for x in sym if x[1]]
        sym = [x[1][0] for x in sym if x[1]]
        en = Enrichnet.run(genesets=sym, graph='string')
        self.assertTrue(hasattr(en, 'table'))


# class TestUtils(unittest.TestCase):
#     def test_id_mapping(self):
#         c = ColorectalCancer()
#         r = IdMapping.convert(input_id=c.deg_list[:2], organism='hsa', source="ENTREZID", target="SYMBOL")
#         self.assertTrue(r[0][1][0] == 'A2M')
#
#     def test_loading_remote_gmts(self):
#         g = GMTUtils.list_enrichr_gmt()
#         self.assertTrue(g is not None)
#
#     def test_load_enrichr_gmt(self):
#         g = GMTUtils.get_enrichr_gmt("Genome_Browser_PWMs")
#         self.assertTrue(g is not None)
#
#     def test_gmt_utils(self):
#         g = GMTUtils.parse_gmt_file(os.path.dirname(os.path.realpath(__file__)) + "/pypathway/tests/gmt_file/h.all.v6.0.entrez.gmt")
#         self.assertTrue(g is not None)
#
#     def test_load_sample_network(self):
#         G = load_hint_hi12012_network()
#         self.assertTrue(G is not None)


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


class TestPropagation(unittest.TestCase):
    pass
