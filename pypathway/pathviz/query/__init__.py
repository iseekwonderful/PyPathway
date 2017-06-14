from ..query.common import KEGGPathwayData, SupportedDatabase, ReactomePathwayData, WiKiPathwayData, KEGGPathwayDataList
from ..query.network import NetworkRequest, NetworkMethod, NetworkException
import json
import sys
import requests
from collections import namedtuple
sys.path.append('/Users/yangxu/PyPathway/')
from pypathway.netviz import FromCYConfig


if sys.version[0] == "2":
    from Queue import Queue
else:
    from queue import Queue


class SearchResult:
    def __init__(self, comment, providers, numhits, results, empty):
        self.comment = comment
        self.providers = providers
        self.numhits = numhits
        self.results = results
        self.empty = empty

    '''
    This class store the total results of a public pathway database (Pathway Common, KEGG will not return this) search,
     this class should only used for the return value of PublicDatabase.search(), should not init singly

    Attributes:
        comment: the comment of a pathway search from Pathway Common
        providers: the total source of the providers
        numhits: the total results
        results: the lists of the result objects
        empty: if returns a empty rearch result
    '''

    def visualize(self):
        '''
        This function provide a quick view of the search result, it provide the the summary and the quick view of
        the pathway map

        Notes: Please do not call this method without ipython notebook, it will pop up a series of matplotlib
        plot windows.

        We recommend you do search operation in a ipython notebook, while get proper pathway file, the write the
         data integrating applications
        '''
        raise NotImplementedError()
        pass

    def __repr__(self):
        return "Get {} result\n{}".format(self.numhits, str(self.results))


# Abstract Class
class Database:
    '''
    This is a abstract class for all the database class.

    we here care about the database about pathway and interactome

    '''
    def __init__(self, name):
        self.name = name

    def search(self, name, organism):
        '''
        This is a commend line method, start with 2 args

        :param name: the target name
        :param organism: the organism
        :return: search result
        '''
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()

    def load(self):
        pass


class BioGRID(Database):
    ACCESS_KEY = '416cb97cff808a451eb54c2a885134b4'

    @staticmethod
    def search(name, organism=9606, proxies=None):
        return BioGRID.search_by_symbol(name, organism, proxies)

    @staticmethod
    def search_by_symbol(name_list, organism=9606, proxies=None):
        url = 'http://webservice.thebiogrid.org/interactions?searchNames=true&geneList={}&includeInteractors=true&includeInteractorInteractions=false&taxId={}&accesskey=416cb97cff808a451eb54c2a885134b4&format=json'
        # print(url.format('|'.join([str(x) for x in name_list]), organism))
        res = NetworkRequest(url.format('|'.join([str(x) for x in name_list]), organism),
                             NetworkMethod.GET, proxy=proxies)
        json_data = json.loads(res.text)
        config = BioGRID.plot(json_data)
        cy = FromCYConfig(config)
        return cy.plot()

    @staticmethod
    def search_by_EntreZ(id_list, proxies=None):
        url = 'http://webservice.thebiogrid.org/interactions/?geneList={}&searchids=true&includeInteractors=true&accessKey=416cb97cff808a451eb54c2a885134b4&format=json'
        res = NetworkRequest(url.format('|'.join([str(x) for x in id_list])),
                             NetworkMethod.GET, proxy=proxies)
        # print(url.format('|'.join([str(x) for x in id_list])))
        # print(res.text)
        json_data = json.loads(res.text)
        # print(json_data)
        config = BioGRID.plot(json_data)
        cy = FromCYConfig(config)
        return cy.plot()

    @staticmethod
    def search_by_pubmed_id(id_list, proxies=None):
        url = 'http://webservice.thebiogrid.org/interactions/?pubmedList={}&accesskey=416cb97cff808a451eb54c2a885134b4&format=json'
        res = NetworkRequest(url.format('|'.join([str(x) for x in id_list])),
                             NetworkMethod.GET, proxy=proxies)
        # print(res.text)
        json_data = json.loads(res.text)
        config = BioGRID.plot(json_data)
        cy = FromCYConfig(config)
        return cy.plot()


    @staticmethod
    def plot(data):
        config = {
            "type": "cy",
            "options": {
                "elements": [
                ],

                "layout": {
                    'name': 'cose-bilkent',
                    'animate': False,
                    'idealEdgeLength': 200,
                },
                "style": [
                    {
                        "selector": "node",
                        "style": {'label': 'data(label)',
                                  'width': 18,
                                  'height': 18,
                                  'font-size': '-1em',
                                  'font-weight': 1,
                                  'background-color': '#91c7ae',
                                  'border-width': 2,
                                  'border-color': '#2f4554'
                                  }
                    },
                    {
                        "selector": "edge",
                        'style': {
                            "curve-style": "haystack",
                            'width': 1,
                            'line-color': '#b4bcc3'
                        }
                    }
                ]

            }
        }
        exist_node = []
        for k, v in data.items():
            if not v['OFFICIAL_SYMBOL_A'] in exist_node:
                config['options']['elements'].append(
                    {'group': 'nodes',
                     'data': {'id': v['BIOGRID_ID_A'],
                              'label': v['OFFICIAL_SYMBOL_A'],
                              },
                     },
                )
            if not v['OFFICIAL_SYMBOL_B'] in exist_node:
                config['options']['elements'].append(
                    {'group': 'nodes',
                     'data': {'id': v['BIOGRID_ID_B'],
                              'label': v['OFFICIAL_SYMBOL_B'],
                              },
                     },
                )
            if v['BIOGRID_ID_A'] == v['BIOGRID_ID_B']:
                continue
            config['options']['elements'].append({
                'group': 'edges',
                'data': {
                    'id': v['BIOGRID_INTERACTION_ID'],
                    'source': v['BIOGRID_ID_A'],
                    'target': v['BIOGRID_ID_B'],
                },
                "classes": "haystack"
            })
        return config

    def start(self):
        pass

    def load(self):
        pass


class IntAct(Database):
    pass


class STRINGSearchResults:
    def __init__(self, results):
        self.results = results

    def __repr__(self):
        return ('-' * 20 + '\n').join(["ResultIndex: {}\n{}\n".format(i, x) for i, x in enumerate(self.results)])

    def __getitem__(self, item):
        if type(item) == int and item < len(self.results):
            return self.results[item]
        else:
            raise IndexError("Item should be a int and small than length")


class STRINGSearchResult:
    def __init__(self, data):
        self.data = data

    def load(self):
        return STRING.load(self.data['stringId'])

    '''
    {'annotation': 'Chemokine (C-C motif) receptor 9; Receptor for chemokine SCYA25/TECK. Subsequently transduces a signal by increasing the intracellular calcium ions level. Alternative coreceptor with CD4 for HIV-1 infection',
        'ncbiTaxonId': 9606,
        'preferredName': 'CCR9',
        'queryIndex': 0,
        'stringId': '9606.ENSP00000350256',
        'taxonName': 'Homo sapiens'}
    '''
    def __repr__(self):
        return "{}".format('\n'.join(['{}: {}'.format(k, v) for k, v in self.data.items() if not k == 'queryIndex']))

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        else:
            pass


class STRING(Database):
    '''
    ToDo:

    1. load method for search result Done
    1.5 search and load a list of genes
    2. convert to networkx object
    3. multiple edge and confidence edge
    4. delete / expand node
    5. tips on node / edge include information: score structure, molecular information

    '''
    def __init__(self):
        Database.__init__(self, 'STRING')

    @staticmethod
    def search(name, organism=9606, proxies=None):
        '''
        Search a protein in database, return a list of result

        :param name: the query name
        :param organism: the organism, default, it is human (9606).
        :return: the search result
        '''
        url = 'http://string-db.org/api/json/resolve?identifier={}&species={}'.format(name, organism)
        res = NetworkRequest(url, NetworkMethod.GET, proxy=proxies)
        json_data = json.loads(res.text)
        return STRINGSearchResults([STRINGSearchResult(x) for x in json_data])

    def start(self):
        pass

    @staticmethod
    def load(id_list, proxies=None):
        '''
        load the network for specific protein

        :param id: protein's id, plz search id first
        :return:
        '''
        Node = namedtuple('Node', ['taxonName', 'stringId', 'annotation', 'preferredName', 'queryIndex', 'ncbiTaxonId'])
        Edge = namedtuple('Edge', ['first', 'second', 'first_name', 'second_name', 'score_list'])
        url = 'http://string-db.org/api/psi-mi-tab/interactionsList?identifiers={}&limit=120'.format(
            '%0D'.join(['{}'.format(x) for x in id_list]))
        # resolve the interactive list
        # print(url)
        res = NetworkRequest(url, NetworkMethod.GET, proxy=proxies)
        iters = []
        for x in res.text.split('\n'):
            if not x: continue
            e = x.split('\t')
            iters.append(Edge(first=e[0], second=e[1], first_name=e[2], second_name=e[3], score_list=e[-1].split('|')))
        # print(iters)
        node_set = set([x.first for x in iters]) & set([x.second for x in iters])
        config = STRING._config_generate(iters)
        # print(config)
        node_count = len([x for x in config['options']['elements'] if x['group'] == 'nodes'])
        print(node_count)
        if node_count > 100:
            # raise Exception("Too many nodes to render: {}".format(node_count))
            config['type'] = 'viva'
        cy = FromCYConfig(config)
        return cy.plot()

    @staticmethod
    def _config_generate(iters):
        exist_node = []
        config = {
            "type": "cy",
            "options": {
                "elements": [
                    # {
                    #     'group': 'nodes',
                    #     'data': {
                    #         'id': self
                    #     }
                    # }
                ],

                "layout": {
                    # 'name': 'cose',
                    # 'idealEdgeLength': 100,
                    # 'nodeOverlap': 20

                    # 'name': 'circle'
                    'name': 'cose-bilkent',
                    'animate': False,
                    'idealEdgeLength': 200,
                    # 'padding': 30,
                },
                "style": [
                    {
                        "selector": "node",
                        "style": {'label': 'data(label)',
                                  'width': 18,
                                  'height': 18,
                                  'font-size': '-1em',
                                  'font-weight': 1,
                                  'background-color': '#91c7ae',
                                  'border-width': 2,
                                  'border-color': '#2f4554'
                                  }
                    },
                    {
                        "selector": "edge",
                        'style': {
                            "curve-style": "haystack",
                            'width': 1,
                            'line-color': '#b4bcc3'
                        }
                    }
                ]

            }
        }
        for x in iters:
            if x.first not in exist_node:
                config['options']['elements'].append(
                    {'group': 'nodes',
                     'data': {'id': x.first,
                              'label': x.first_name,
                              },
                     "position": {
                         "x": 481.0169597039117,
                         "y": 384.8210888234145
                            },
                     },
                )
                exist_node.append(x.first)
            if x.second not in exist_node:
                config['options']['elements'].append(
                    {'group': 'nodes',
                     'data': {'id': x.second,
                              'label': x.second_name,
                              },
                     }
                )
                exist_node.append(x.second)
        for x in iters:
            for e in x.score_list:
                config['options']['elements'].append({
                    'group': 'edges',
                    'data': {
                            'id': e,
                            'source': x.first,
                             'target': x.second,
                             },
                    "classes": "haystack"
                })
        return config

    def export(self):
        pass


# Abstract Class
class FunctionSet:
    '''
    Stand for a smilier function group, like interactome database or pathway database.

    '''
    def start(self, *args, **kwargs):
        '''
        Generally, start a job on certain category, like search or load info

        :param args:
        :param kwargs:
        :return:
        '''
        raise NotImplementedError()


class Interactome(FunctionSet):
    '''
    Manager of 3 database, BioGIRD, IntAct and BioGIRD.
    Contain 3 possible object, may be empty or not
    all network are base on networkx

    '''
    def __init__(self, st=None, gi=None, act=None):
        self.st = st
        self.gi = gi
        self.act = act

    def start(self, *args, **kwargs):
        '''
        Use the graphic user interface to fill the information of this node. May from a set of symbol or a saved session

        :param args:
        :param kwargs:
        :return:
        '''
        pass

    @staticmethod
    def symbol_set(self, set, organism=9606):
        '''
        Generate a map from a set

        :param set: a set of gene symbol, find all the connection and extra one step interact network.
        :return: a Interactome instance.
        '''

    def enrichment(self):
        pass


class Pathway(FunctionSet):
    '''
    Manager of 3 database, KEGG, Reactome and WikiPathway

    '''
    def start(self, *args, **kwargs):
        pass


class PublicDatabase:
    '''
    This class Provide the methods for pathway search, including KEGG and PathwayCommon.

    Args:
        database: member in common.SupportedDatabase, if you want to search all database, using SupportedDatabase.ALL

    Attributes:
        name: database

    Methods:
        kegg_search: search KEGG using KEGG's rest api
        common_search: search other database using Pathway Common's api
    '''
    def __init__(self, database=None):
        self.name = database

    @staticmethod
    def search_wp(keyword, species=None, proxies=None):
        '''
        Search WikiPathway database using WikiPathway's rest api

        note if you want more function use webservice.
        :param keyword: The search keyword
        :param species: The target species
        :param proxies: proxies used by while requesting data.
        :return: a list of search result
        '''
        if species:
            url = "http://webservice.wikipathways.org/findPathwaysByText?query={}&species={}&format=json".format(
                keyword, species
            )
        else:
            url = "http://webservice.wikipathways.org/findPathwaysByText?query={}&format=json".format(
                keyword
            )
        res = NetworkRequest(url, NetworkMethod.GET, proxy=proxies)
        try:
            if len(res.text) == 0:
                return []
            data = json.loads(res.text)
        except:
            raise Exception("Json parse exception")
        results = []
        for x in data["result"]:
            pw = WiKiPathwayData(x["id"], x["name"], x["species"], x["score"], x["revision"])
            results.append(pw)
        return results

    @staticmethod
    def search_kegg(keyword, organism="ko", proxies=None):
        '''
        Search KEGG database using KEGG's rest api.

        :param keyword: The search keyword
        :param organism: the organism
        :param proxies: proxies used by while requesting data.
        :return: a list of search result(instance of KEGGPathwayData)
        '''
        url = "http://rest.kegg.jp/find/pathway/{}".format(keyword)
        try:
            res = NetworkRequest(url, NetworkMethod.GET, proxy=proxies)
        except NetworkException as e:
            raise e
        if len(res.text) <= 1:
            return []
        else:
            results = [KEGGPathwayData(x.split("\t")[0][8:], x.split("\t")[1], organism)
                         for x in res.text.split("\n") if len(x) > 0]
            pathways = KEGGPathwayDataList(results=results)
            # Fill the png and KGML data use a multi-thread module
            error = Queue()
            [p.retrieve(organism) for p in pathways]
            [p._join_active_thread() for p in pathways]
            if not error.empty():
                e = error.get()
                raise NetworkException(e[0], e[1])
            return [p for p in pathways if hasattr(p, "data") and p.data and len(p.data) > 0]

    @staticmethod
    def search_reactome(keyword, organism=None, proxies=None):
        '''
        Search Reactome database

        :param keyword: The keyword using while searching.
        :param proxies: if not None, the proxies use while searching.
        :param organism: the target organism
        :return: a list of search result
        '''
        if not organism:
            url = "http://www.reactome.org/ContentService/search/query?query={}&types=Pathway&cluster=true".format(
                keyword
            )
        else:
            url = "http://www.reactome.org/ContentService/search/query?query={}&species={}&types=Pathway&cluster=true".format(
                keyword, organism
            )
        try:
            req = requests.get(url=url, proxies=proxies)
            if not req.status_code == 200:
                return []
            else:
                res = req.text
        except Exception as e:
            raise NetworkException(url, e)
        # parse
        if len(res) == 0:
            return []
        # for k, v in json.loads(res)['results'][0]['entries'][0].items():
        #     print(k, v)
        try:
            result = []
            if json.loads(res)["results"]:
                for x in json.loads(res)["results"][0]["entries"]:
                    for sp in ReactomePathwayData.list_species():
                        if sp.name == x['species'][0]:
                        # print(x['species'])
                            result.append(
                                ReactomePathwayData(x["dbId"], x["name"], x["id"], None, None, None, species=sp)
                            )
            return result
        except:
            raise

    @staticmethod
    def _check_list_arg(arg):
        '''
        Private function, check if args is a list or None
        :param arg:
        :return:
        '''
        for x in arg:
            if x is not None and not isinstance(x, list):
                return False
        else:
            return True


DB = PublicDatabase


# if __name__ == '__main__':
#     BioGIRD.search('CD4', 9606)