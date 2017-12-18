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
import numpy as np
import pkgutil
import logging
import sys


class GSEA(EnrichmentResult):
    @staticmethod
    def parse_class_vector(path):
        return gp.parser.gsea_cls_parser(path)

    @staticmethod
    def run(data, gmt, cls, permutation_type='phenotype', method='signal_to_noise', permution_num=1000):
        prefix = gp.__name__ + "."
        for importer, modname, ispkg in pkgutil.iter_modules(gp.__path__, prefix):
            if modname == "gseapy.gsea":
                module = __import__(modname, fromlist="dummy")
        vs = gp.__version__.split(".")
        if int(vs[0]) == 0 and int(vs[1]) < 9:
            module.ranking_metric = GSEA._ranking_metric
        else:
            module.ranking_metric = GSEA._ranking_metric2
        gp.algorithm.ranking_metric = GSEA._ranking_metric
        res = gp.gsea(data, gmt, cls, permutation_type=permutation_type, permutation_num=permution_num,
                      outdir=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images'), method=method)
        return GSEA(res.res2d, data, gmt, cls)

    def __init__(self, df, data, gmt, cls):
        EnrichmentResult.__init__(self, df, data, gmt, 'GSEA', -1, 3, '-lg(fdr)')
        self.df, self.data, self.gmt, self.cls = df, data, gmt, cls


    @staticmethod
    def _ranking_metric2(df, method, pos, neg, classes, ascending):
        '''
        Original implementation

        '''
        A = pos
        B = neg

        # exclude any zero stds.
        df_mean = df.groupby(by=classes, axis=1).mean()
        df_std = df.groupby(by=classes, axis=1).std()

        min_allowed = df_mean.abs() * 0.2
        min_allowed = min_allowed.where(min_allowed > 0, 0.2)
        df_std = df_std.where(df_std > min_allowed, min_allowed)

        if method == 'signal_to_noise':
                ser = (df_mean[pos] - df_mean[neg])/(df_std[pos] + df_std[neg])
        elif method == 't_test':
                ser = (df_mean[pos] - df_mean[neg])/ np.sqrt(df_std[pos]**2/len(df_std)+df_std[neg]**2/len(df_std) )
        elif method == 'ratio_of_classes':
                ser = df_mean[pos] / df_mean[neg]
        elif method == 'diff_of_classes':
                ser  = df_mean[pos] - df_mean[neg]
        elif method == 'log2_ratio_of_classes':
                ser  =  np.log2(df_mean[pos] / df_mean[neg])
        else:
                logging.error("Please provide correct method name!!!")
                sys.exit()
        ser = ser.sort_values(ascending=ascending)

        return ser



    @staticmethod
    def _ranking_metric(df, method, phenoPos, phenoNeg, classes, ascending):
        '''
        Original implementation

        '''
        A = phenoPos
        B = phenoNeg

        # exclude any zero stds.
        df_mean = df.groupby(by=classes, axis=1).mean()
        df_std = df.groupby(by=classes, axis=1).std()

        min_allowed = df_mean.abs() * 0.2
        min_allowed = min_allowed.where(min_allowed > 0, 0.2)
        df_std = df_std.where(df_std > min_allowed, min_allowed)

        if method == 'signal_to_noise':
            sr = (df_mean[A] - df_mean[B]) / (df_std[A] + df_std[B])
        elif method == 't_test':
            sr = (df_mean[A] - df_mean[B]) / np.sqrt(df_std[A] ** 2 / len(df_std) + df_std[B] ** 2 / len(df_std))
        elif method == 'ratio_of_classes':
            sr = df_mean[A] / df_mean[B]
        elif method == 'diff_of_classes':
            sr = df_mean[A] - df_mean[B]
        elif method == 'log2_ratio_of_classes':
            sr = np.log2(df_mean[A] / df_mean[B])
        else:
            logging.error("Please provide correct method name!!!")
            sys.exit()
        sr.sort_values(ascending=ascending, inplace=True)
        df3 = sr.to_frame().reset_index()
        df3.columns = ['gene_name', 'rank']
        df3['rank2'] = df3['rank']
        return df3

