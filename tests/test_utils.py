import unittest
import os
import sys

sys.path.append("/Users/yangxu/PyPathway")

import networkx as nx
import numpy as np

from pypathway import IdMapping, FromNetworkX, ColorectalCancer, GMTUtils
from pypathway.utils import load_hint_hi12012_network
from pypathway.pathviz.utils import plot
from IPython.core.display import HTML
from echarts import *


class TestIdMapping(unittest.TestCase):
    def test_download_database(self):
        '''
        Test download database from www.bioconductor.org

        :return: None
        '''
        # clear the database cache
        IdMapping.clear()
        # check and download
        IdMapping.check_db_available('hsa')
        # check file exist
        self.assertTrue(os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/../pypathway/utils/caches/org.Hs.eg.sqlite"))

    def test_convert(self):
        '''
        Test convert ENTREZID to SYMBOL in human

        :return:
        '''
        test_case = [2, 8195, 6274, 147463]
        result = IdMapping.convert(test_case, source="ENTREZID", target="SYMBOL", species='hsa')
        result_should_be = [[2, ['A2M']], [8195, ['MKKS']], [6274, ['S100A3']], [147463, ['ANKRD29']]]
        for x in result:
            for s in result_should_be:
                if x[0] == s[0]:
                    self.assertTrue(x[1][0] == s[1][0])


class TestGraphPlot(unittest.TestCase):
    def test_networkx_Graph(self):
        '''
        test plot in a networkx object in a notebook

        :return: None
        '''
        G = nx.complete_graph(5)
        plot_object = FromNetworkX(G)
        # check if its a IPython.core.display.HTML object
        self.assertTrue(isinstance(plot_object.plot(), HTML))


class TestChartPlot(unittest.TestCase):
    def test_line_plot(self):
        '''
        Test plot a chart in a notebook

        :return: None
        '''
        data = [[round(t, 4) for t in np.random.uniform(15 * x, 25 * (x + 1), 7).tolist()]
                for x in range(4)]
        chart = Echart("Line", "random data")
        organism = ["Spleen", "Skin", "HK", "Jill"]
        for x in range(4):
            chart.use(Line(organism[x], data[x]))
        chart.use(Axis('category', 'bottom', data=["0H", "6H", "12H", "2Day", "3Day", "5Day", "7Day"],
                       boundaryGap=False))
        chart.use(Axis('value', 'left'))
        chart.use(Legend(data=["Spleen", "Skin", "HK", "Jill"], position=('center', 'bottom')))
        chart.use(Tooltip())
        result = plot(chart)
        self.assertTrue(isinstance(result, HTML))


class TestLoadDatasets(unittest.TestCase):
    def test_load_cancer_dataset(self):
        '''
        Test load cancer dataset

        :return: None
        '''
        c = ColorectalCancer()
        self.assertTrue(len(c.deg_list) == 5320)

    def test_load_test_network(self):
        '''
        Test load STRING network

        :return: None
        '''
        G = load_hint_hi12012_network()
        self.assertTrue(len(G) == 9859)

    def test_load_gmt_file(self):
        '''
        Test load GMT files

        :return: None
        '''
        gmt = GMTUtils.parse_gmt_file("../pypathway/tests/gmt_file/h.all.v6.0.entrez.gmt")
        self.assertTrue("HALLMARK_ADIPOGENESIS" in gmt)


if __name__ == "__main__":
    unittest.main()
