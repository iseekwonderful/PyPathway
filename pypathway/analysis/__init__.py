from ..utils import IdMapping
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests
import math
import pandas as pd
import os
from ..pathviz.utils import plot_json
from copy import deepcopy


class PreProcess:
    @staticmethod
    def deg_stat(data, classes, pos, neg, adjust='fdr_bh'):
        '''
        Basic t-test for certain normalized DataFrame
        If its a RNA SEQ data, use READemption for data process is a better option
        
        :param data: the pandas dataframe
        :param classes: the class vector
        :param pos: the positive class name
        :param neg: the negative class name
        :param adjust: the multipletest adjust method
        :return: a dataframe contains the result of the basic ttest.
        '''
        data = data.copy()
        PDF = data.groupby(classes, axis=1).get_group(pos)
        CDF = data.groupby(classes, axis=1).get_group(neg)
        ttests = [ttest_ind(PDF.iloc[i], CDF.iloc[i], equal_var=False)[1] for i in range(PDF.shape[0])]
        fc = PDF.mean(axis=1) - CDF.mean(axis=1)
        mul = multipletests(ttests, method=adjust)
        data['fold-change'] = pd.Series(fc, index=data.index)
        data['p-value'] = pd.Series(ttests, index=data.index)
        data['fdr'] = pd.Series(mul[1], index=data.index)
        return data


class EnrichmentResult:
    '''
    This class is the basic class of all enrichment class, contains the necessary result.
    
    '''
    def __init__(self, df, source_data, target, method, title_index, prop_index, xlabel='-lg(P-Value)'):
        self.df, self.source_data, self.target, self.method, self.xlabel = df, source_data, target, method, xlabel
        self.title_index, self.prop_index = title_index, prop_index
        self.basic_config = {
                        'title': {
                            'text': 'Enrichment result',
                            'subtext': 'Unknown'
                        },
                        'tooltip': {
                            'trigger': 'axis',
                            'axisPointer': {
                                'type': 'shadow'
                            }
                        },
                        'grid': {
                            'left': '3%',
                            'right': '12%',
                            'bottom': '3%',
                            'containLabel': True
                        },
                        'xAxis': {
                            'type': 'value',
                            'boundaryGap': [0, 0.01],
                            'name': self.xlabel
                        },
                        'yAxis': {
                            'type': 'category',
                            'data': []
                        },
                        'series': [
                            {
                                'name': xlabel,
                                'type': 'bar',
                                'data': []
                            },
                        ]
                    }

    def plot(self, count=15, data=False, func=lambda x: -math.log2(x)):
        '''
        Plot the chart in the output area, if it is in the CLI, this function only return an Ipython.display.HTML 
        instance
        
        :param count: the count displayed in the chart, default is 15
        :param data: if True, the config is returned
        :param func: the function to calculate the height of the bar, default is f(x) = -log2(x)
        :return: the Ipython.display.HTML object
        '''
        config = deepcopy(self.basic_config)
        config['yAxis']['data'] = []
        config['series'][0]['data'] = []
        config['title']['subtext'] = self.target
        config['title']['text'] = "{} Enrichment Analysis".format(self.method.upper())
        candidate = []
        for x in self.df.iterrows():
            candidate.append([x[1][self.title_index], func(x[1][self.prop_index])])
        candidate = sorted(candidate, key=lambda x: x[1], reverse=True)
        for x in candidate[:count]:
            config['yAxis']['data'].append(x[0])
            config['series'][0]['data'].append(x[1])
        if data:
            return config
        return plot_json(config)

    @property
    def table(self):
        '''
        get the table result of the analysis
        
        :return: the result DataFrame
        '''
        return self.df

    def overview(self):
        '''
        get the overview of the analysis, contains the method name, arguments and the result stats
        
        :return: a dict of overview
        '''
        raise NotImplementedError()

    def graph(self):
        '''
        If the result of the enrichment contains the graph relation ship, use this function
        
        :return: the graph plot
        '''
        raise NotImplementedError()

    def arguments(self):
        raise NotImplementedError()

    def snapshot(self, count=8, func=lambda x: -math.log2(x)):
        '''
        this function return the snapshot for a smaller plot area

        :param count: the count displayed in the chart, default is 15
        :param data: if True, the config is returned
        :param func: the function to calculate the height of the bar, default is f(x) = -log2(x)
        :return: the Ipython.display.HTML object
        '''
        config = deepcopy(self.basic_config)
        config['yAxis']['data'] = []
        config['series'][0]['data'] = []
        config['title']['subtext'] = self.target
        config['title']['text'] = "{} Enrichment Analysis".format(self.method.upper())
        config['color'] = ['#F2F2F2']
        config['xAxis']['lineColor'] = 'transparent'
        config['grid']['top'] = '5%'
        config['xAxis']['splitLine'] = {"show": False}
        config['yAxis']['splitLine'] = {"show": False}
        del config['title']
        candidate = []
        for x in self.df.iterrows():
            candidate.append([x[1][self.title_index], func(x[1][self.prop_index])])
        candidate = sorted(candidate, key=lambda x: x[1], reverse=True)
        for x in candidate[:count]:
            config['yAxis']['data'].append(x[0])
            config['series'][0]['data'].append(x[1])
        return config

    def table_display(self):
        return self.table.to_html()


# may not support yet
class Enrichment:
    SUPPORT_METHODS = ['ora', 'gsea', 'enrichnet', 'spia']
    SUPPORT_TARGETS = ['KEGG', "GO", "Reactome"]

    @staticmethod
    def run(method, target, study=None, pop=None, assoc=None, table=None, columns=None, cut_off=None,
            adjust='fdr_bh', organism='human', nB=2000, graph_db='string', FC_columns=None):
        '''
        Interface for the Enrichment analysis, more methods will be added to the Enrichment.SUPPORT_METHODS

        :param method: the enrichment method, should list in Enrichment.SUPPORT_METHODS
        :param target: the target database, should list in the SUPPORT_TARGETS
        :param study: a list of the study group (significant group). if input is a DataFrame (table), should be empty
        :param pop: a list of population group (background) if input is a DataFrame (table), should be empty
        :param assoc: the association between the identifier in study / pop / table
        :param table: if input is a table (typical output of a differential expression analysis) should be the
            pandas's DataFrame
        :param columns: the column name to identify certain gene is significant. e.g. p-value
        :param cut_off: the cut_off value if the input is a table
        :param adjust: the adjust method for multipletests,
            detail: http://www.statsmodels.org/dev/generated/statsmodels.sandbox.stats.multicomp.multipletests.html
        :param organism: the target organism, default is human
        :param nB: for spia only, the bootstrap simulate counts
        :param graph_db: for enrichnet only. the interactive network database for distance calculation
        :param FC_columns: for SPIA analysis, the columns name in the table, if input using a study, it should be a
        dict contain the ENTREZID and the fold change of genes
        :return: a Enrichment object.
        '''
        from .ora import KEGG, Reactome, GO
        from .gsea import Enrichr
        from .network import SPIA, Enrichnet

        # check method and study
        if method not in Enrichment.SUPPORT_METHODS:
            raise Exception('Input method not supported')
        if target not in Enrichment.SUPPORT_TARGETS:
            raise Exception('Target not supported')
        if study is None and table is None:
            raise Exception('Please input at lease a dataframe or a list')
        # derive study, pop from dataframe if necessary
        if table is not None:
            study, pop = {}, []
            for i, x in table.iterrows():
                if x[columns] < cut_off:
                    study[i] = x
                pop.append(i)
            if not study:
                    raise Exception("No significant group from table with cutoff={}".format(cut_off))
        if method == 'ora':
            if target == 'KEGG':
                return KEGG.run(list(study.keys()), pop, organism=organism, adjust=adjust)
            elif target == 'Reactome':
                symbol = IdMapping.convert(list(study.keys()), organism, 'ENTREZID', 'ENSEMBL')
                return Reactome.run([x[1][0] for x in symbol if x[1]], organism)
            elif target == 'GO':
                if not assoc:
                    # generate assoc
                    id2go = IdMapping.convert(pop, organism, 'ENTREZID', 'GO')
                    assoc = ''
                    for x in id2go:
                        if not x[1][0]:
                            continue
                        assoc += "{}\t{}\n".format(x[0], ";".join(x[1]))
                    with open(os.path.dirname(os.path.realpath(__file__)) + "/ora/obo/assoc", 'w') as fp:
                        fp.write(assoc)
                return GO.run([str(x) for x in study.keys()], [str(x) for x in pop], os.path.dirname(os.path.realpath(__file__)) + "/ora/obo/assoc")
        elif method == 'gsea':
            # translate the ENTREZID to symbol
            symbol = IdMapping.convert(list(study.keys()), organism, 'ENTREZID', 'SYMBOL')
            sy_study = {}
            for x in symbol:
                if x[1][0]:
                    sy_study[x[1][0]] = study[x[0]][columns]
            return Enrichr.run(sy_study, target)
        elif method == 'spia':
            return SPIA.run({k: v[FC_columns] for k, v in study.items()}, pop, organism=organism, nB=nB)
        elif method == 'enrichnet':
            return Enrichnet.run([x[1][0] for x in IdMapping.convert(list(study.keys()), organism, 'ENTREZID', 'ENSEMBL') if x[1][0]],
                                 pathdb=target.lower(), graph=graph_db, idtype='ensembl')


if __name__ == '__main__':
    pass
