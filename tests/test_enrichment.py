import sys
sys.path.insert(0, "/Users/yangxu/PyPathway")

import unittest
import os
import pandas as pd
from pypathway import ORA, KEGG, GO, GSEA, GMTUtils, SPIA, ColorectalCancer, IdMapping, Enrichnet


class TestEnrichment(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestEnrichment, self).__init__(*args, **kwargs)
        self.c = ColorectalCancer()

    # def test_general_ora(self):
    #     '''
    #     Test ora using gene sets from gmt file
    #
    #     :return: None
    #     '''
    #     # load gmt file
    #     gmt_path = os.path.dirname(os.path.realpath(__file__)) + "/../pypathway/tests/gmt_file/h.all.v6.0.entrez.gmt"
    #     gmt = GMTUtils.parse_gmt_file(gmt_path)
    #     # load test data set
    #     res = ORA.run(self.c.deg_list, self.c.background, gmt)
    #     # check result
    #     self.assertEqual(res.table.sort_values("fdr").iloc[0][0], "HALLMARK_ADIPOGENESIS")
    #     self.assertAlmostEqual(res.table.sort_values("fdr").iloc[0][-1], 7.38e-24)

    # def test_kegg_ora(self):
    #     '''
    #     Test ora implementation using geneset from KEGG
    #
    #     :return: None
    #     '''
    #     # run test
    #     r = KEGG.run(self.c.deg_list, self.c.background, organism='hsa')
    #     # check result
    #     self.assertEqual(r.table.sort_values("fdr").iloc[0][0], "hsa01100")
    #     self.assertAlmostEqual(r.table.sort_values("fdr").iloc[0][-1], 2.81e-18)

    # def test_go_ora(self):
    #     '''
    #     Test ora using GO DAG
    #
    #     :return: None
    #     '''
    #     # if obo file not found, will be auto downloaded
    #     r = IdMapping.convert_to_dict(input_id=self.c.background, source='ENTREZID', target="GO", species='hsa')
    #     rg = GO.run([str(x) for x in self.c.deg_list], [str(x) for x in self.c.background], r, obo="go-basic.obo")
    #     # check result
    #     self.assertEqual(rg.table.sort_values("p_bonferroni").iloc[0][0], "GO:0044444")
    #     self.assertAlmostEqual(rg.table.sort_values("p_bonferroni").iloc[0][-2], 4.73e-102)

    def test_gsea(self):
        '''
        Test gsea enrichment

        :return:
        '''
        dir = os.path.dirname(os.path.realpath(__file__)) + "/../examples/analysis/data/"
        phenoA, phenoB, class_vector = GSEA.parse_class_vector(dir + "GSE4107.cls")
        gene_exp = pd.read_excel(dir + "GSE4107.xlsx")
        r = GSEA.run(data=gene_exp.iloc[:1000], gmt="KEGG_2016", cls=class_vector)
        # check result
        print(r.table)
        self.assertEqual(r.table.sort_values("es").iloc[0].name,
                         'Valine, leucine and isoleucine degradation_Homo sapiens_hsa00280')
        self.assertAlmostEqual(r.table.sort_values("es").iloc[0].es, -0.8363, places=3)

    # def test_spia(self):
    #     r = SPIA.run(all=self.c.background, de=self.c.deg, organism='hsa')
    #     # check
    #     self.assertEqual(r.table.sort_values("pPERT").iloc[0].name, "04510")
    #     self.assertAlmostEqual(r.table.sort_values("pPERT").iloc[0].pPERT, 5e-6)

    # def test_enrichnet(self):
    #     sym = IdMapping.convert(input_id=self.c.deg_list, source='ENTREZID', target="SYMBOL", species='hsa')
    #     sym = [x[1][0] for x in sym if x[1]]
    #     en = Enrichnet.run(genesets=sym, graph='string')
    #     # check
    #     self.assertEqual(en.table.sort_values("Fisher q-value").iloc[0]["Annotation (pathway/process)"],
    #                      "hsa00280:Valine, leucine and isoleucine degradation")
    #     self.assertAlmostEqual(en.table.sort_values("Fisher q-value").iloc[0]["XD-score"], 4.33, 2)


if __name__ == '__main__':
    unittest.main()
