import unittest
from pypathway import PublicDatabase as Database, STRING, BioGRID, ColorectalCancer
from pypathway import GSEA, SPIA, Enrichnet, KEGG
from pypathway import MAGI, Hotnet2
from pypathway import GMTUtils, IdMapping
from pypathway.utils import load_hint_hi12012_network
from pypathway import random_walk_with_restart, random_walk, diffusion_kernel
import pandas as pd
import os
import networkx as nx


class TestNetworkProcess(unittest.TestCase):
    def test_kegg(self):
        print("test kegg")
        p = Database.search_kegg("jak")[0].load()
        self.assertTrue(p is not None)

    def test_reactome(self):
        print("test reactome")
        p = Database.search_reactome("jak")[0].load()
        self.assertTrue(p is not None)

    def test_wikipathway(self):
        print("test wp")
        p = Database.search_wp("jak")[0].load()
        self.assertTrue(p is not None)

    def test_string(self):
        print("test string")
        G = STRING.search("CD22")[0].load()
        self.assertTrue(hasattr(G, 'plot'))

    def test_biogrid(self):
        print("test biogrid")
        G = BioGRID.search("CD22")
        self.assertTrue(hasattr(G, 'plot'))


class TestAnalysis(unittest.TestCase):
    def test_ora(self):
        print("test ora")
        c = ColorectalCancer()
        r = KEGG.run(c.deg_list, c.background, organism='hsa')
        self.assertTrue(r is not None)

    def test_gsea(self):
        print("test gsea")
        path = os.path.dirname(os.path.realpath(__file__)) + "/pypathway/tests/gsea_data/"
        phenoA, phenoB, class_vector = GSEA.parse_class_vector(path + "/GSE4107.cls")
        gene_exp = pd.read_excel(path + "/GSE4107.xlsx")
        r = GSEA.run(data=gene_exp.iloc[:100], gmt="KEGG_2016", cls=class_vector)
        self.assertTrue(r is not None)

    def test_spia(self):
        print("test spia")
        c = ColorectalCancer()
        deg = {k: c.deg[k] for k in list(c.deg.keys())[:100]}
        s = SPIA.run(deg, c.background)
        self.assertTrue(hasattr(s, 'plot'))

    def test_enrichnet_api(self):
        print("test enrichnet")
        c = ColorectalCancer()
        sym = IdMapping.convert(input_id=c.deg_list, source='ENTREZID', target="SYMBOL", organism='hsa')
        sym = [x[1][0] for x in sym if x[1]]
        sym = [x[1][0] for x in sym if x[1]]
        en = Enrichnet.run(genesets=sym, graph='string')
        self.assertTrue(hasattr(en, 'table'))


class TestUtils(unittest.TestCase):
    def test_id_mapping(self):
        print("test idmapping")
        c = ColorectalCancer()
        r = IdMapping.convert(input_id=c.deg_list[:2], organism='hsa', source="ENTREZID", target="SYMBOL")
        self.assertTrue(r[0][1][0] == 'A2M')

    def test_loading_remote_gmts(self):
        print("test gmts")
        g = GMTUtils.list_enrichr_gmt()
        self.assertTrue(g is not None)

    def test_load_enrichr_gmt(self):
        print("test enrichr gmt")
        g = GMTUtils.get_enrichr_gmt("Genome_Browser_PWMs")
        self.assertTrue(g is not None)

    def test_gmt_utils(self):
        print("test gmt utils")
        g = GMTUtils.parse_gmt_file(os.path.dirname(os.path.realpath(__file__)) + "/pypathway/tests/gmt_file/h.all.v6.0.entrez.gmt")
        self.assertTrue(g is not None)

    def test_load_sample_network(self):
        print("test network")
        G = load_hint_hi12012_network()
        self.assertTrue(G is not None)


# class ModellingTest(unittest.TestCase):
#     # uncomment this while local test, this is time wasting for travis-ci
#     def test_make_network_file(self):
#         path = os.path.dirname(os.path.realpath(__file__)) + "/pypathway/analysis/modelling/third_party/hotnet2/paper/"
#         Hotnet2.make_network(edgelist_file=path + "data/networks/hint+hi2012/hint+hi2012_edge_list",
#                              gene_index_file=path + "data/networks/hint+hi2012/hint+hi2012_index_gene",
#                              network_name='hint+hi2012', prefix='hint+hi2012', beta=0.4,
#                              output_dir='data/networks/hint+hi2012_2', num_permutations=8)
#
#     def test_make_heat_file(self):
#         print("test heat")
#         path = os.path.dirname(os.path.realpath(__file__)) + "/pypathway/analysis/modelling/third_party/hotnet2/paper/"
#         Hotnet2.make_heat(type='scores', heat_file=path + 'data/heats/pan12.gene2freq.txt',
#                           output_file='former/pan12.gene2freq.json', name='pan12.freq')
#
#     def test_run_hotnet2(self):
#         '''
#         This test make take ~30 minuates
#
#         :return:
#         '''
#         path = os.path.dirname(os.path.realpath(__file__)) + "/pypathway/analysis/modelling/third_party/hotnet2/paper/"
#         Hotnet2.run_hotnet2(network_files=[path + 'data/networks/hint+hi2012/hint+hi2012_ppr_0.4.h5'],
#                             permuted_network_paths=[
#                                 path + 'data/networks/hint+hi2012/permuted/hint+hi2012_ppr_0.4_##NUM##.h5'],
#                             heat_files=[path + 'data/heats/pan12.gene2freq.json'],
#                             output_directory='result', num_cores=-1, heat_permutations=1)


class TestPropagation(unittest.TestCase):
    def test_random_walk(self):
        print("test random walk")
        G = nx.Graph([[1, 2], [2, 3], [3, 5], [2, 5], [1, 4], [4, 5]])
        h = [1 if i % 3 == 0 else 0 for i in range(len(G))]
        r = random_walk(G, h)
        self.assertTrue(r is not None)

    def test_RWR(self):
        print("test rwr")
        G = nx.Graph([[1, 2], [2, 3], [3, 5], [2, 5], [1, 4], [4, 5]])
        h = [1 if i % 3 == 0 else 0 for i in range(len(G))]
        r = random_walk_with_restart(G, h, rp=0.7)
        self.assertTrue(r is not None)

    def test_heat_kernel(self):
        print("test heat kernel")
        G = nx.Graph([[1, 2], [2, 3], [3, 5], [2, 5], [1, 4], [4, 5]])
        h = [1 if i % 3 == 0 else 0 for i in range(len(G))]
        r = diffusion_kernel(G, h, rp=0.7, n=200)
        self.assertTrue(r is not None)