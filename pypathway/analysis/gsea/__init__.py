from ...pathviz.query.network import NetworkMethod, NetworkRequest
import pandas
import math
from .. import EnrichmentResult
import json
import pandas as pd
from ...pathviz.utils import plot_json
try:
    from io import StringIO
except:
    from StringIO import StringIO


class EnrichrResult(EnrichmentResult):
    def __init__(self, df: pandas.DataFrame, source_data, target):
        EnrichmentResult.__init__(self, df, source_data, target, 'gsea')
        self.define = {
            'KEGG':
                lambda x: {'name': x.split('_')[0], 'species': x.split('_')[1], 'id': x.split('_')[2]},
            'Reactome':
                lambda x: {'name': x.split('_')[0], 'species': x.split('_')[1], 'id': x.split('_')[2]},
            'GO': lambda x: x
        }

    @property
    def table(self):
        return self.df

    @property
    def plot(self, count=15):
        self.basic_config['yAxis']['data'] = []
        self.basic_config['series'][0]['data'] = []
        self.basic_config['title']['subtext'] = self.target
        self.basic_config['title']['text'] = "{} Enrichment Analysis".format(self.method.upper())
        candidate = []
        for x in self.df.iterrows():
            candidate.append([x[1][0].split('_')[0], -math.log2(x[1][2])])
        candidate = sorted(candidate, key=lambda x: x[1], reverse=True)
        for x in candidate[:15]:
            self.basic_config['yAxis']['data'].append(x[0])
            self.basic_config['series'][0]['data'].append(x[1])
        # print(self.basic_config)
        return plot_json(self.basic_config)

    def detail(self, index):
        if 'KEGG' in self.target.upper():
            return {
                'info': self.define['KEGG'](self.table.iloc[index][0]),
                'stat': self.table.iloc[index],
                'source': self.source_data
            }
        elif 'REACTOME' in self.target.upper():
            ds = {
                'info': self.define['KEGG'](self.table.iloc[index][0]),
                'stat': self.table.iloc[index],
                'source': self.source_data
            }
            from ...pathviz.query.common import ReactomePathwayData
            rp = ReactomePathwayData(
                ds['info']['id'], ds['info']['name'], ds['info']['id'], None, None, None, ds['info']['species'])
            return rp
        elif 'GENE' in self.target.upper():
            return {
                'info': self.define['KEGG'](self.table.iloc[index][0]),
                'stat': self.table.iloc[index],
                'source': self.source_data
            }
        else:
            return "Detail visualization is not implemented yet"

    @property
    def overview(self):
        '''
        If KEGG or Reactome, return the enrichment in a overview plot
        If GO: return the enrichment in a DAG containing the path to the root.

        :return:
        '''
        return None


class Enrichr:
    @staticmethod
    def run(gene_set, database="KEGG"):
        url = 'http://amp.pharm.mssm.edu/Enrichr/addList'
        gene_list = '\n'.join([str(x) for x in gene_set])
        res = NetworkRequest(url, NetworkMethod.POST, post_arg={'files': {
            'list': (None, gene_list),
            'description': (None, 'a enrichment')
        }})
        json_data = json.loads(res.text)
        return Enrichr(json_data['userListId'], json_data['shortId'], gene_set).list('{}_2016'.format(database))

    def __init__(self, userListId, shortId, source_data):
        self.userListId = userListId
        self.shortId = shortId
        self.source_data = source_data

    def list(self, library):
        url = 'http://amp.pharm.mssm.edu/Enrichr/export?userListId={}&filename={}&backgroundType={}'.format(
            self.userListId, 'test', library)
        res = NetworkRequest(url, NetworkMethod.GET)
        return EnrichrResult(pd.read_table(StringIO(res.text)), self.source_data, library)
