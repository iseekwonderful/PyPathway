#
# We use the implement of GSEApy
#
# github: https://github.com/BioNinja/GSEApy
#
# author: BioNinja (Zhuoqing Fang)
#

from .. import EnrichmentResult
import gseapy as gp
import os


class GSEA(EnrichmentResult):
    @staticmethod
    def run(data, gmt, cls, permutation_type='phenotype', method='signal_to_noise', permution_num=1000):
        res = gp.gsea(data, gmt, cls, permutation_type=permutation_type, permutation_num=permution_num,
                      outdir=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images'), method=method)
        return GSEA(res.res2d, data, gmt, cls)

    def __init__(self, df, data, gmt, cls):
        EnrichmentResult.__init__(self, df, data, gmt, 'GSEA', 0, 4, '-lg(fdr)')
        self.df, self.data, self.gmt, self.cls = df, data, gmt, cls

