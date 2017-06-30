import subprocess
from io import StringIO
from ...analysis import Analysis, EnrichmentResult
import re
from ...pathviz.utils import plot_json
import requests
import json

import numpy as np
import os
import pandas as pd
from scipy import stats
import random
import time
import math
from statsmodels.sandbox.stats import multicomp
import pickle
from scipy.stats import norm


class Enrichnet(Analysis, EnrichmentResult):
    '''
    The adaptor of enrichnet network enrichment analysis service.

    '''
    @staticmethod
    def run(genesets, idtype='hgnc_symbol', pathdb='kegg', graph='string'):
        # init requests query session ID
        r = requests.get('http://www.enrichnet.org/index.php')
        sessions = re.findall('index.php\?SESSION_NAME=(.+)\"', r.text)
        if not sessions:
            raise Exception("Cant acquire session from site")
        session = sessions[0]
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
        mission_id = mission[0]
        df = Enrichnet.check_for_job_done(mission_id)
        return Enrichnet(mission_id, df, genesets, idtype, pathdb, graph)

    @staticmethod
    def check_for_job_done(mission_id):
        while True:
            print('http://www.enrichnet.org/pages/tmp/{}/result.php'.format(mission_id))
            r = requests.get('http://www.enrichnet.org/pages/tmp/{}/result.php'.format(mission_id))
            print(r.status_code)
            if r.status_code == 404:
                time.sleep(10)
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

    def __init__(self, mission_id, df, geneset, idtype, pathdb, graph):
        self.mission_id, self.df, self.geneset, self.idtype, self.pathdb, self.graph = mission_id, df, geneset, idtype, pathdb, graph
        EnrichmentResult.__init__(self, self.df, geneset, pathdb, 'Enrichnet')

    @property
    def plot(self):
        self.basic_config['yAxis']['data'] = []
        self.basic_config['series'][0]['data'] = []
        self.basic_config['title']['subtext'] = self.target
        self.basic_config['title']['text'] = "{} Enrichment Analysis".format(self.method.upper())
        candidate = []
        for x in self.df.iterrows():
            candidate.append([x[1][0], -math.log2(x[1][2])])
        candidate = sorted(candidate, key=lambda x: x[1], reverse=True)
        for x in candidate[:15]:
            self.basic_config['yAxis']['data'].append(x[0])
            self.basic_config['series'][0]['data'].append(x[1])
        # print(self.basic_config)
        return plot_json(self.basic_config)

    def overview(self):
        raise NotImplementedError()

    def detail(self, index):
        raise NotImplementedError()

    @property
    def table(self):
        return self.df

    @property
    def main_property(self):
        return 'Fisher q-value'

    @property
    def network_data(self):
        raise NotImplementedError()


class SPIA(Analysis, EnrichmentResult):
    '''
    The migration of SPIA from R to py

    > res=spia(de=DE_Colorectal,all=ALL_Colorectal,organism="hsa",nB=2000,plots=FALSE,beta=NULL,combine="fisher",verbose=FALSE)

    '''
    @staticmethod
    def _load_data(path):
        datpT, id2name = {}, {}
        for d in os.listdir(path):
            if not '_' in d or d == '.DS_Store':
                continue
            id, name = d.split('_')[0], d.split('_')[1]
            id2name[id] = name
            datpT[id] = {}
            for x in os.listdir(path + d):
                fn = x[1:].replace('*', '/')
                tb = pd.read_table(path + d + '/' + x, sep=' ')
                datpT[id][fn + 'table'] = tb
                datpT[id][fn] = tb.as_matrix()
        return datpT, id2name

    @staticmethod
    def _load_de(de_path, all_path):
        with open(de_path) as fp:
            con = fp.read()
        de = {}
        for x in con.split("\n")[1:]:
            if not x:
                continue
            de[int(x.split(' ')[0].replace('"', ''))] = float(x.split(' ')[1])
        with open(all_path) as fp:
            con = fp.read()
        all = [int(x.split(' ')[1].replace('"', '')) for x in con.split('\n')[1:] if x]
        return de, all

    @staticmethod
    def save_data(dataT_all, id2name):
        with open(os.path.dirname(os.path.realpath(__file__)) + "/spia_data/hsa", 'wb') as fp:
            pickle.dump([dataT_all, id2name], fp)

    @staticmethod
    def load_dumped_data(organism):
        with open(os.path.dirname(os.path.realpath(__file__)) + "/spia_data/{}".format(organism), 'rb') as fp:
            return pickle.load(fp)

    @staticmethod
    def load_json_data(organism):
        '''
        load json data from certain organism.

        :param organism:  the organism, this method will load the cor data
        :return: the loaded data
        '''
        with open(os.path.dirname(os.path.realpath(__file__)) + "/spia_data/{}.json".format(organism)) as fp:
            data = json.load(fp)
        datpT = {}
        id2name = data['id2name']
        for pid, v in data.items():
            if pid == 'id2name':
                continue
            datpT[pid] = {}
            for key, d in v.items():
                if key == 'row_names':
                    datpT[pid][key] = d
                else:
                    m = np.zeros((len(v['row_names']), len(v['row_names'])))
                    for x in d:
                        m[x[0]][x[1]] = 1
                    datpT[pid][key] = m
        return datpT, id2name

    @staticmethod
    def run(de, all, organism='hsa', nB=2000, beta=None, combine='fisher'):
        if organism not in ['hsa', 'mmu']:
            raise Exception("The organism not contained in the prepared data")
        de, all = SPIA._load_de(de, all)
        datpT_ALL, id2name = SPIA.load_json_data(organism)
        rel = ["activation", "compound", "binding/association", "expression", "inhibition",
               "activation_phosphorylation", "phosphorylation", "inhibition_phosphorylation",
               "inhibition_dephosphorylation", "dissociation", "dephosphorylation",
               "activation_dephosphorylation", "state change", "activation_indirect effect",
               "inhibition_ubiquination", "ubiquination", "expression_indirect effect",
               "inhibition_indirect effect", "repression", "dissociation_phosphorylation",
               "indirect effect_phosphorylation", "activation_binding/association",
               "indirect effect", "activation_compound", "activation_ubiquination"]
        inter_value = [1, 0, 0, 1, -1, 1, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0, 1, -1, -1, 0, 0, 1, 0, 1,
                       1] or beta
        rel_dict = {rel[i]: inter_value[i] for i in range(len(rel))}
        datp_ALL = {}
        for k, v in datpT_ALL.items():
            sizem = len(v[rel[0]][0])
            s, con = np.zeros((sizem, sizem)), np.zeros((sizem, sizem))
            for kk, vv in rel_dict.items():
                con += v[kk] * abs(vv)
                s += v[kk] * vv
            zz = np.reshape(np.repeat(con.sum(axis=0), sizem), (sizem, sizem))
            z = np.transpose(zz)
            z[z == 0] = -1
            r = np.divide(s, z)
            datp_ALL[k] = r
        smPFS, tAraw, tA, pNDE, pb, pG, status = {}, {}, {}, {}, {}, {}, {}
        # calculate the Ac
        for k, v in datp_ALL.items():
            row_names = datpT_ALL[k]['row_names']
            # let first calculate the pNDE
            noMy = len(set(row_names) & set(de.keys()))
            pNDE[k] = stats.hypergeom.sf(noMy - 1, len(all), len(set(row_names) & set(all)), len(de))
            # then calculate the Ac and pPERT
            M = np.eye(v.shape[0]) * -1 + v
            if np.linalg.det(M) == 0:
                smPFS[k], tAraw[k], tA[k], pb[k] = np.nan, np.nan, np.nan, np.nan
                continue
            X = []
            for x in row_names:
                if x in de:
                    X.append(de[x])
                else:
                    X.append(0)
            pfs = np.linalg.solve(M, -np.array(X))
            smPFS[k] = sum(pfs - X)
            tAraw[k] = smPFS[k]
            pfstmp = []
            de_sample = list(de.values())
            all_sample = [i for i, x in enumerate(row_names) if x in all]
            length = len(X)
            for i in range(2000):  # nB
                x = np.zeros(length)
                sp = random.sample(de_sample, noMy)
                idx = random.sample(all_sample, noMy)
                x[idx] = sp
                tt = np.linalg.solve(M, -x)
                pfstmp.append(sum(tt - x))
            tA[k] = tAraw[k] - np.median(np.array(pfstmp))
            if tA[k] > 0:
                status[k] = "Activated"
            else:
                status[k] = "Inhibited"
            ob = tA[k]
            pfstmp = np.array(pfstmp) - np.median(np.array(pfstmp))
            if ob > 0:
                pb[k] = sum([1 for pf in pfstmp if pf >= ob]) / len(pfstmp) * 2
                if pb[k] <= 0:
                    pb[k] = 1 / nB / 100
                elif pb[k] >= 1:
                    pb[k] = 1
            elif ob < 0:
                pb[k] = sum([1 for pf in pfstmp if pf <= ob]) / len(pfstmp) * 2
                if pb[k] <= 0:
                    pb[k] = 1 / nB / 100
                elif pb[k] >= 1:
                    pb[k] = 1
            else:
                pb[k] = 1
            if combine == 'fisher':
                c = pNDE[k] * pb[k]
                pG[k] = c - c * math.log(c)
            else:
                # comb = pnorm((qnorm(p1) + qnorm(p2)) / sqrt(2))
                pG[k] = norm.cdf(norm.ppf(pNDE[k]) + norm.ppf(pb[k]) / math.sqrt(2))
            # print('id: ', k, '\ttA:', tA[k], '\tpNDE: ', pNDE[k], '\t pPERT: ', pb[k], '\tPG: ', pG[k])
        _, o, _, _ = multicomp.multipletests(list(pG.values()), method='fdr_bh')
        pGfdr = {list(pG.keys())[i]: o[i] for i in range(len(list(pG.keys())))}
        _, o, _, _ = multicomp.multipletests(list(pNDE.values()), method='fdr_bh')
        pNDEfdr = {list(pNDE.keys())[i]: o[i] for i in range(len(list(pNDE.keys())))}
        _, o, _, _ = multicomp.multipletests(list(pG.values()), method='bonferroni')
        pGbf = {list(pG.keys())[i]: o[i] for i in range(len(list(pG.keys())))}
        df = pd.DataFrame([id2name, pNDE, pb, pG, pGfdr, pNDEfdr, pGbf, status]).T
        df.columns = ['name', 'pNDE', 'pPERT', 'pG', 'pGfdr', 'pNDEfdr', 'pGbf', 'status']
        df = df.sort_values(by='pGfdr')
        return SPIA(df, de, all, organism, nB, beta, combine)

    def __init__(self, df, de, all, organism, nB, beta, combine):
        EnrichmentResult.__init__(self, df, de, 'KEGG', 'SPIA', 'pGfdr')
        self.df, self.de, self.all, self.organism, self.nB, self.beta, self.combine = df, de, all, organism, nB, beta, combine

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
            candidate.append([x[1][0], -math.log2(x[1][4])])
        candidate = sorted(candidate, key=lambda x: x[1], reverse=True)
        for x in candidate[:15]:
            self.basic_config['yAxis']['data'].append(x[0])
            self.basic_config['series'][0]['data'].append(x[1])
        # print(self.basic_config)
        return plot_json(self.basic_config)




class SPIA_C(Analysis):
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
