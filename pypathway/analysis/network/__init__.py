import pandas as pd
import subprocess
from io import StringIO
from ...pathviz.query.common import NetworkMethod, NetworkRequest
import re
from ...pathviz.utils import plot_json
import math
import requests
import time


class Enrichnet:
    '''
    The adaptor of enrichnet network enrichment analysis service.

    '''
    def __init__(self, genesets, idtype='ensembl', pathdb='biocarta', graph='string'):
        # init requests query session ID
        r = requests.get('http://www.enrichnet.org/index.php')
        sessions = re.findall('index.php\?SESSION_NAME=(.+)\"', r.text)
        if not sessions:
            raise Exception("Cant acquire session from site")
        session = sessions[0]
        self.status = 'idle'
        if idtype not in ['ensembl', 'hgnc_symbol', 'refseq_dna', 'uniprot_swissprot']:
            raise Exception("Unknown idtypes")
        if pathdb not in ['kegg', 'biocarta', 'reactome', 'wiki', 'nci', 'interpro', 'gobp', 'gomf', 'gocc']:
            raise Exception("Unknown pathdb")
        if graph not in ['bossi', 'string']:
            raise Exception("Unknown graph")
        data = {
            'SESSION_NAME': session,
            'pathway': 'reactome',
            'cweighted': 'string',
            'identifier': 'hgnc_symbol',
            'geneset': ','.join([x for x in genesets])
        }
        url = 'http://www.enrichnet.org/index.php?tmpdat=result'
        res = requests.post(url, data=data)
        mission = re.findall("http://www.enrichnet.org/reload.php\?temp=([\d\w_]+)", res.text)
        if not mission:
            raise Exception("Cant not retrieve mission id")
        self.mission_id = mission[0]
        self.status = 'processing'

    def check_for_job_done(self):
        while True:
            print('http://www.enrichnet.org/pages/tmp/{}/result.php'.format(self.mission_id))
            r = requests.get('http://www.enrichnet.org/pages/tmp/{}/result.php'.format(self.mission_id))
            print(r.status_code)
            if r.status_code == 404:
                time.sleep(5)
                continue
            elif r.status_code == 200:
                break
            else:
                raise Exception("Unclear status code while query the server")
        table_url = re.findall(
            "file2.php\?filen=C:/xampp/htdocs/enrichnet/pages/tmp/.+?/enrichnet_ranking_table.txt", r.text)
        if not table_url:
            raise Exception("Cant retrieve data")
        r = requests.get("http://www.enrichnet.org/" + table_url[0])
        return pd.read_table(StringIO(r.text))

    @property
    def result(self):
        return None




class SPIA:
    '''
    The adaptor of C implement of Signaling Pathway Impact Analysis (SPIA)

    '''
    def __init__(self, de, all, organism, nB=2000):
        '''
        Apply a SPIA analysis, the de and all could be a pandas dataframe or a file, result is returned in the SPIA
        class.

        :param de: a two columns table with entraz ID and fold changes
        :param all: a data series of genes or a file contain genes in the fromat of entraz ID
        :param organism: the organism
        :param nB: number of bootstraps default=2000
        '''
        path_de, path_all = None, None
        if type(all) == pd.Series:
            contents = ""
            for i, x in all.iteritems():
                contents += '{}\t{}\n'.format(i, x)
            with open('all.tab', 'w') as fp:
                fp.write(contents)
            path_all = 'all.tab'
        else:
            path_all = all
        if type(de) == pd.DataFrame:
            contents = ""
            for _, x in de.iterrows():
                contents += '{}\t{}\n'.format(x[0], x[1])
            with open('de.tab', 'w') as fp:
                fp.write(contents)
            path_de = 'de.tab'
            self.de_total = de
        else:
            path_de = de
            self.de_total = pd.read_table(de)
        path = '/Users/yangxu/spia_c/test/'
        binary = '/Users/yangxu/spia_c/bin/spia'
        argv = ['spia', '--dir', '{}pathways/'.format(path),
                '--de', path_de, '--array',
                path_all, '--nBoots', '2000']
        r = subprocess.check_output([binary] + argv)
        self.de_dict = {}
        self.r = r
        self._parse_result(r)
        # fix me: organism, pandas test

    def _parse_result(self, out):
        out = out.decode('utf8')
        self.detail_raw = out.split('Path\tpSize')[0].split('####################')[1:]
        self.detail = {}
        self.de = {}
        for x in self.detail_raw:
            path_id = re.findall('(\d+.?)\.tab', x)[0]
            self.detail[path_id] = {}
            self.de[path_id] = {}
            self.detail[path_id]['Acc'] = {k: v for (k, v) in re.findall('(\d+):  ([\d\.]+)',
                                                                         re.findall('Acc = (.+)', x)[0])}
            self.detail[path_id]['PF'] = {k: v for (k, v) in re.findall('(\d+):  ([\d\.]+)',
                                                                         re.findall('PF = (.+)', x)[0])}
            for i, r in self.de_total.iterrows():
                self.de_dict[int(r[0])] = r[1]
            for k in self.detail[path_id]['Acc']:
                if int(k) in self.de_dict:
                    self.de[path_id][int(k)] = self.de_dict[int(k)]
                else:
                    self.de[path_id][int(k)] = 0
            args = ['pSize', 'NDE', 't_A', 'pNDE', 't_Ac', 'pPERT', 'pG']
            for a in args:
                str = '{} = ([\d\.]+)'.format(a)
                self.detail[path_id]['PF'][a] = re.findall(str, x)[0]

        table = 'Path\tpSize' + out.split('Path\tpSize')[1]
        self.tb = pd.read_table(StringIO(table))

    def plot(self):
        pass

    def pathway(self, pathway_id):
        if pathway_id not in self.detail:
            raise Exception("Pathway not found")
        config = self._single_plot_config()
        zero_x, zero_y, none_zero = [], [], []
        for k, v in self.detail[pathway_id]['Acc'].items():
            k = int(k)
            if v == 0:
                zero_y.append([float(self.de[pathway_id][k]),float(v)])
            elif self.de[pathway_id][k] == 0:
                zero_x.append([float(self.de[pathway_id][k]), float(v)])
            else:
                none_zero.append([float(self.de[pathway_id][k]), float(v)])
        config['series'][0]['data'] = zero_x
        config['series'][1]['data'] = zero_y
        config['series'][2]['data'] = none_zero
        matrix = zero_x + zero_y + none_zero
        max_x, min_x, max_y, min_y = max([x for x, y in matrix]), min([x for x, y in matrix]),\
                                     max([y for x, y in matrix]), min([y for x, y in matrix])
        config['xAxis'][0]['min'] = math.floor(min_x) - 2,
        config['xAxis'][0]['max'] = math.ceil(max_x) + 2,
        config['yAxis'][0]['min'] = math.floor(min_y) - 2,
        config['yAxis'][0]['max'] = math.ceil(max_y) + 2,
        config['title']['text'] = 'Pathway: {}'.format(pathway_id)
        # print(config)
        return plot_json(config)

    def _single_plot_config(self):
        option = {
            'title': {
                'text': 'Anscombe\'s quartet',
                'x': 'center',
                'y': 0
            },
            'grid': [
                {'x': '2%', 'y': '7%', 'width': '46%', 'height': '83%'},
                {'x2': '2%', 'y': '7%', 'width': '46%', 'height': '83%'},
            ],
            'tooltip': {
                'formatter': 'Group {a}: ({c})'
            },
            'xAxis': [
                {'gridIndex': 0, 'min': 0, 'max': 20},
                {'gridIndex': 1, 'min': 0, 'max': 20},
            ],
            'yAxis': [
                {'gridIndex': 0, 'min': 0, 'max': 15},
                {'gridIndex': 1, 'min': 0, 'max': 15},
            ],
            'series': [
                {
                    'name': 'I',
                    'type': 'scatter',
                    'xAxisIndex': 0,
                    'yAxisIndex': 0,
                    'data': 'dataAll[0]',
                    # 'markLine': 'markLineOpt'
                },
                {
                    'name': 'III',
                    'type': 'scatter',
                    'xAxisIndex': 0,
                    'yAxisIndex': 0,
                    'data': 'dataAll[2]',
                    # 'markLine': 'markLineOpt'

                },
                {
                    'name': 'II',
                    'type': 'scatter',
                    'xAxisIndex': 0,
                    'yAxisIndex': 0,
                    'data': 'dataAll[1]',
                    # 'markLine': 'markLineOpt'
                }
            ]
        }
        return option

    @property
    def result(self):
        return self.tb

if __name__ == '__main__':
    # s = SPIA('/Users/yangxu/spiA_c/test/data/DE_Colorectal.tab',
    #          '/Users/yangxu/spiA_c/test/data/ALL_Colorectal.tab', organism='hsa')
    # print(s.r)
    e = Enrichnet(['ENSG00000113916', 'ENSG00000068024', 'ENSG00000108840', 'ENSG00000061273', 'ENSG00000005339'])
