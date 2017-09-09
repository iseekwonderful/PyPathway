# HOTNET and MAGI

from multiprocessing import Pool
import multiprocessing as mp
import subprocess
import networkx as nx
import re
import os
from collections import namedtuple
from ...utils import _select
from ...utils import _cluster
from ...netviz import FromNetworkX
import sys
import inspect


MAGI_RESULT = namedtuple('MAGI', ['num', 'genes', 'args', 'coExp'])


class MAGIResult:
    def __init__(self, graph, num, genes, args, coExp):
        self.graph, self.num, self.genes, self.args, self.coExp = graph, num, genes, args, coExp

    def plot(self):
        return FromNetworkX(self.graph).plot()

    def __repr__(self):
        return str(self.genes)


class MAGI:
    '''
    The parallel wrapper of MAGI (Merge Affected Genes into Integrated networks)
    site: https://eichlerlab.gs.washington.edu/MAGI/


    Interfaces: 1. select_pathway
                2. cluster

    Note: All the input file are the str like file path.

    '''
    EXECUTABLE_PATH = '/Users/yangxu/Library/Developer/Xcode/DerivedData/MAGI-cmkybopnjlqlcidnrzkxmmycmuop/Build/Products/Debug/MAGI'
    CLUSTER_PATH = '/Users/yangxu/Library/Developer/Xcode/DerivedData/MAGI-cmkybopnjlqlcidnrzkxmmycmuop/Build/Products/Debug/Cluster'
    TEST_ARGS = {
        'PPI Network': ['-p', '/Volumes/Data/magi/StringNew_HPRD.txt'],
        'cases mutation list': ['-c', '/Volumes/Data/magi/ID_2_Autism_4_Severe_Missense.Clean_WithNew.txt'],
        'Gene CoExpression Id': ['-h', '/Volumes/Data/magi/GeneCoExpresion_ID.txt'],
        'CoExpression Matrix': ['-e', '/Volumes/Data/magi/adj1.csv.Tab.BinaryFormat'],
        'control mutation list': ['-d', '/Volumes/Data/magi/New_ESP_Sereve.txt'],
        'Length of genes': ['-l', '/Volumes/Data/magi/Gene_Name_Length.txt'],
        'run id': ['-i', 'test_run']
    }
    CLUSTER_ARGS = {
        'PPI Network': ['-p', '/Volumes/Data/magi/StringNew_HPRD.txt'],
        'scores': ['-c', '/Users/yangxu/PyPathway/pypathway/analysis/modelling/RandomGeneList.0'],
        'Gene CoExpression Id': ['-h', '/Volumes/Data/magi/GeneCoExpresion_ID.txt'],
        'CoExpression Matrix': ['-e', '/Volumes/Data/magi/adj1.csv.Tab.BinaryFormat'],
        'Seed File': ['-s', '/Users/yangxu/PyPathway/pypathway/analysis/modelling/seeds'],
        'upper bound on control mutations': ['-m', '1'],
        'lower bound on the size of the module': ['-l', '5'],
        'upper bound on the size of the module': ['-u', '100'],
        'minimum ratio of seed score allowed': ['-a', '0.5'],
        'run id': ['-i', 'cluster'],
        'minimum pair-wise coexpression value': ['-minCoExpr', '0.01'],   # optional
        'minimum average coexpression of the module': ['-avgCoExpr', '0.415'],   # optional
        'minimum density of PPI': ['-avgDensity', '0.08']
    }
    additional = "-nc 5 -nt 1"

    @staticmethod
    def make_pathway(args):
        '''
        the warper of generate pathway seed, the test args is listed in the MAGI.TEST_ARGS

        :param args:
        :return:
        '''
        colors, mutations = [8, 7, 6, 5], [4, 3, 2, 1]
        pool = Pool(processes=8)
        for i in colors:
            for j in mutations:
                pool.apply_async(MAGI._run_color_and_mut, args=(args, i, j))
        pool.close()
        pool.join()

    @staticmethod
    def select_pathway(ppi, case, coExpId, coExpMat, ctrl, length, filter=None, process=mp.cpu_count()):
        '''
        This function is the wrapper of the pathway_select wrapper, implement parallel programming using
         multiprocessing.Pool.

        :param ppi: the protein-protein network
        :param case: the mutation list in the case
        :param coExpId: the coExpression id list
        :param coExpMat: the coExpression matrix
        :param ctrl: the control mutation list
        :param length: the length of genes
        :param filter: the list of gene should not including in the network
        :param process: the process count, default is the threading number.
        :return: None, with the generated seed file in the ./cache folder
        '''
        for x in [ppi, case, coExpId, coExpMat, ctrl, length]:
            try:
                open(x, 'r')
            except:
                raise Exception("File not found")
        colors, mutations, run_id = [8, 7, 6, 5], [4, 3, 2, 1], '0'
        # colors, mutations, run_id = [5], [1], '0'
        cache_dir = os.path.dirname(os.path.realpath(__file__)) + '/cache'
        pool = Pool(processes=process)
        seed = []
        for i in colors:
            for j in mutations:
                seed.append([cache_dir, "BestPaths.Length{}.Control{}.Run0".format(i, j), i, j])
                if not filter:
                    args = (cache_dir, ppi, case, coExpId, coExpMat, ctrl, length, run_id, i, j)
                else:
                    args = (cache_dir, ppi, case, coExpId, coExpMat, ctrl, length, run_id, i, j, filter)
                pool.apply_async(_select.select, args=args)
        pool.close()
        pool.join()
        sf = ""
        # generate seed file
        for x in seed:
            if not x[1] in os.listdir(cache_dir):
                raise Exception("Cannot find output file")
            sf += '{}/{}\t{}\t{}\n'.format(*x)
        with open(cache_dir + "/seeds", 'w') as fp:
            fp.write(sf)

    @staticmethod
    def cluster(ppi, coExpId, coExpMat, upper_mutation_on_control,
                min_size_of_module, max_size_of_module, min_ratio_of_seed,
                minCoExpr=None, avgCoExpr=None, avgDensity=None, seed=None, score=None):

        '''
        Please make sure seed pathways have been created via select_pathway method

        '/Volumes/Data/magi/StringNew_HPRD.txt', '/Users/yangxu/PyPathway/pypathway/analysis/modelling/RandomGeneList.0', '/Volumes/Data/magi/GeneCoExpresion_ID.txt', '/Volumes/Data/magi/adj1.csv.Tab.BinaryFormat', '/Users/yangxu/PyPathway/pypathway/analysis/modelling/seeds', 2, 5, 100, '0.5', '2'
        :param ppi: the ppi network
        :param coExpId: the coExpression id list
        :param coExpMat: the coExpression matrix
        :param upper_mutation_on_control: the max mutation allowed in the control
        :param min_size_of_module: min size of module
        :param max_size_of_module: max size of module
        :param min_ratio_of_seed: For each seed type the top percentage of the score from maximum score of the seed allowed (in the paper 0.5 was used)
        :param minCoExpr: The minimum pair-wise coexpression value per gene allowed
        :param avgCoExpr: The minimum average coexpression of the modules allowed
        :param avgDensity: The minimum avergae PPI density of the modules allowed
        :param seed: if this step is followed by select_pathway, seed is auto generated, else input the seed file path
        :param score: if this step is followed by select_pathway, score is auto generated, else input the score file path

        :return: a list of modules.
        '''
        cache_dir = os.path.dirname(os.path.realpath(__file__)) + '/cache'
        seed = seed or cache_dir + '/seeds'
        score = score or cache_dir + '/RandomGeneList.0'
        minCoExpr = minCoExpr or 'none'
        avgCoExpr = avgCoExpr or 'none'
        avgDensity = avgDensity or 'none'
        _cluster.cluster(ppi, score, coExpId, coExpMat, seed, upper_mutation_on_control, min_size_of_module,
                         max_size_of_module, str(min_ratio_of_seed), '0', minCoExpr,
                         avgCoExpr, avgDensity, cache_dir + '/magi.res')
        # read the result and return the result object.
        return MAGI.parse_result(cache_dir + '/magi.res', ppi)
        # return [MAGIResult(x[0], x[1].num, x[1].genes, x[1].args, x[1].coExp) for x in res]

    @staticmethod
    def _run_color_and_mut(args, color, mutation):
        execute = MAGI.EXECUTABLE_PATH + " " + " ".join(
            ["{} {}".format(x[0], x[1]) for _, x in args.items()]) + " -nc {} -nm {}".format(color, mutation)
        r = subprocess.call(execute, shell=True)
        print(r)

    @staticmethod
    def cluster_wrap(*args):
        print(args)
        execute = MAGI.CLUSTER_PATH + ' ' + ' '.join(
            ['{} {}'.format(x[0], x[1]) for x in args]
        )
        r = subprocess.check_output(execute, shell=True)
        # open the ppi network
        for x in args:
            if x[0] == '-p':
                with open(x[1]) as fp:
                    con = fp.read()
                    G = nx.Graph()
                    for x in con.split('\n'):
                        if not x:
                            continue
                        G.add_edge(x.split('\t')[0], x.split('\t')[1])
                    break
        else:
            raise Exception("No PPI network find")
        return MAGI.parse_result(G, r.decode('utf8'))

    @staticmethod
    def run_test():
        '''
        Call the official example.

        :return:
        '''
        MAGI.select_pathway('/Volumes/Data/magi/StringNew_HPRD.txt', '/Volumes/Data/magi/ID_2_Autism_4_Severe_Missense.Clean_WithNew.txt',
                            '/Volumes/Data/magi/GeneCoExpresion_ID.txt', '/Volumes/Data/magi/adj1.csv.Tab.BinaryFormat',
                            '/Volumes/Data/magi/New_ESP_Sereve.txt', '/Volumes/Data/magi/Gene_Name_Length.txt')

    @staticmethod
    def generate_seeds():
        pass

    @staticmethod
    def parse_result(result_file, ppi):
        G = MAGI.load_background_graph(ppi)
        with open(result_file) as fp:
            mg = fp.read()
        results = re.findall("\d+.+?\d+ \d+ \d+ \d+ [\.\d]+ [\.\d]+ [\.\d]+", mg, re.DOTALL)
        res = [MAGI._parse_single_result(x, G) for x in results]
        return [MAGIResult(x[0], x[1].num, x[1].genes, x[1].args, x[1].coExp) for x in res]

    @staticmethod
    def _parse_single_result(out, G):
        res = []
        coExp = {}
        genes = {}
        length = int(out.split('\n')[0])
        for l in out.split('\n')[1:-1]:
            sp = l.split(', ')
            if len(sp) == 3:
                if not sp[0] in coExp:
                    coExp[sp[0]] = {}
                coExp[sp[0]][sp[1]] = float(sp[2])
            elif len(sp) == 7:
                genes[sp[0]] = {'numSevereMutInCases': sp[1], 'numMissenseMutInCases': sp[2],
                                'numSevereMutInControl': sp[3], 'prob': sp[4], 'weightCases': sp[5],
                                'weightControl': sp[6]}
            else:
                print(sp)
                if not sp[0] in coExp:
                    coExp[sp[0]] = {}
                coExp[sp[0]][sp[1]] = float(sp[3])

        arg_list = out.split("\n")[-1].split(' ')
        m = MAGI_RESULT(length, genes, arg_list, coExp)
        new_graph = nx.subgraph(G, m.genes.keys())
        # generate the config
        config = {}
        for k, v in m.genes.items():
            config[k] = {
                'tooltip': {
                    'numSevereMutInCases': v['numSevereMutInCases'],
                    'numMissenseMutInCases': v['numMissenseMutInCases'],
                    'numSevereMutInControl': v['numSevereMutInControl'],
                    'weightCases': v['weightCases']
                },
                'style': {
                    'width': (float(v['weightCases']) + 2) * 4,
                    'height': (float(v['weightCases']) + 2) * 4,
                },
                'snapshot': {
                    'width': (float(v['weightCases']) + 30) * 2,
                    'height': (float(v['weightCases']) + 30) * 2,
                    'font-size': '3em',
                }
            }
        for x in new_graph.node:
            new_graph.node[x] = config[x]
        for k, v in new_graph.edge.items():
            for ano, v in v.items():
                new_graph.edge[k][ano] = {'style': {'width': float(m.coExp[k][ano]) * 5}}
        return new_graph, m

    @staticmethod
    def load_background_graph(path):
        with open(path) as fp:
            con = fp.read()
        G = nx.Graph()

        for x in con.split('\n'):
            if not x:
                continue
            G.add_edge(x.split('\t')[0], x.split('\t')[1])
        return G


class Hotnet2:
    '''
    optimized Warper for algorithm hotnet2
    Github: https://github.com/raphael-group/hotnet2
    original paper: M.D.M. Leiserson*, F. Vandin*, H.T. Wu, J.R. Dobson, J.V. Eldridge, J.L. Thomas, A. Papoutsaki,
     Y. Kim, B. Niu, M. McLellan, M.S. Lawrence, A.G. Perez, D. Tamborero, Y. Cheng, G.A. Ryslik, N. Lopez-Bigas,
      G. Getz, L. Ding, and B.J. Raphael. (2014) Pan-Cancer Network Analysis Identifies Combinations of Rare Somatic
       Mutations across Pathways and Protein Complexes. Nature Genetics 47, 106–114 (2015).

    '''
    @staticmethod
    def make_network(edgelist_file, gene_index_file, network_name, prefix,
                     beta, output_dir, only_permutations=False, Q=115, permutation_start_index=1, num_permutations=100,
                     index_file_start_index=1, cores=-1):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/third_party/hotnet2")
        from makeNetworkFiles import run
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        arg = Hotnet2()
        for a in args:
            setattr(arg, a, values[a])
        print(arg.__dict__)
        run(arg)

    @staticmethod
    def make_heat(**kwargs):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/third_party/hotnet2")
        import makeHeatFile as m
        type = kwargs.get('type')
        if not type:
            raise Exception('heat type is necessary')
        type2hf = {'scores': m.load_direct_heat,
                        'mutation': m.load_mutation_heat,
                        'oncodrive': m.load_oncodrive_heat,
                        'mutsig': m.load_mutsig_heat,
                        'music': m.load_music_heat}
        if not type in type2hf:
            raise Exception("Unknown args")
        arg = Hotnet2()
        setattr(arg, 'heat_fn', type2hf[type])
        for k, v in kwargs.items():
            setattr(arg, k, v)
        for k, v in {'min_heat_score': 0, "gene_filter_file": None,
                     'min_freq': 1, 'fm_threshold': 0.2, 'cis_threshold': 0.2,
                     'cis': False, 'threshold': 1.0, 'max_heat': 15}.items():
            setattr(arg, k, v)
        m.run(arg)

    @staticmethod
    def run_hotnet2(network_files, permuted_network_paths, heat_files, deltas=None,
                    display_score_fil=None, display_name_file=None, output_hierarchy=False,
                    network_permutations=100, consensus_permutations=0, heat_permutations=100,
                    output_directory='.', num_cores=-1, min_cc_size=2, verbose=1,
                    display_score_file=None):
        sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/third_party/hotnet2")
        from HotNet2 import run
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        arg = Hotnet2()
        for a in args:
            setattr(arg, a, values[a])
        print(arg.__dict__)
        run(arg)


if __name__ == '__main__':
    path = "/Volumes/Data/hotnet2/paper/"
    Hotnet2.run_hotnet2(network_files=[path + 'data/networks/hint+hi2012/hint+hi2012_ppr_0.4.h5',
                                       path + 'data/networks/irefindex9/irefindex9_ppr_0.45.h5',
                                       path + 'data/networks/multinet/multinet_ppr_0.5.h5'],
                        permuted_network_paths=[
                            path + 'data/networks/hint+hi2012/permuted/hint+hi2012_ppr_0.4_##NUM##.h5',
                            path + 'data/networks/irefindex9/permuted/irefindex9_ppr_0.45_##NUM##.h5',
                            path + 'data/networks/multinet/permuted/multinet_ppr_0.5_##NUM##.h5'],
                        heat_files=[path + 'data/heats/pan12.gene2freq.json',
                                    path + 'data/heats/pan12.gene2mutsig.json'],
                        output_directory='result')


