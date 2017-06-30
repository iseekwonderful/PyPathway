# HOTNET, KeyPathwayMiner and MAGI
from multiprocessing import Pool
import subprocess
import networkx as nx
import re
from collections import namedtuple


MAGI_OUT = namedtuple('MAGI', ['num', 'genes', 'args'])


class MAGI:
    '''
    The parallel warper of MAGI (Merge Affected Genes into Integrated networks)
    site: https://eichlerlab.gs.washington.edu/MAGI/

    ToDO lists: 1. fill the output result in the parser
                2. try to add information to the node
                3. add the overview of the graph

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
        'PPI Network': ['-p', '/Volumes/Data\ 1/magi/StringNew_HPRD.txt'],
        'scores': ['-c', 'RandomGeneList.0'],
        'Gene CoExpression Id': ['-h', '/Volumes/Data\ 1/magi/GeneCoExpresion_ID.txt'],
        'CoExpression Matrix': ['-e', '/Volumes/Data\ 1/magi/adj1.csv.Tab.BinaryFormat'],
        'Seed File': ['-s', 'seeds'],
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
    def make_pathway(*args):
        '''
        the warper of generate pathway seed, the test args is listed in the MAGI.TEST_ARGS

        :param args:
        :return:
        '''
        colors, mutations = [8, 7, 6, 5], [4, 3, 2, 1]
        pool = Pool(processes=1)
        for i in colors:
            for j in mutations:
                pool.apply_async(MAGI._run_color_and_mut, args=(args, i, j))
        pool.close()
        pool.join()

    @staticmethod
    def _run_color_and_mut(args, color, mutation):
        execute = MAGI.EXECUTABLE_PATH + " " + " ".join(
            ["{} {}".format(x[0], x[1]) for _, x in args.items()]) + " -nc {} -nm {}".format(color, mutation)
        r = subprocess.call(execute, shell=True)
        print(r)

    @staticmethod
    def cluster(*args):
        print(args)
        execute = MAGI.CLUSTER_PATH + ' ' + ' '.join(
            ['{} {}'.format(x[0], x[1]) for x in args]
        )
        print(execute)
        r = subprocess.check_output(execute, shell=True)
        print(r)
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
        pass

    @staticmethod
    def generate_seeds():
        pass

    @staticmethod
    def parse_result(G, res):
        '''
        This function parse the output by the MAGI

        :param G: The PPI network, we return the subnet from the PPI network
        :param res: the output of MAGI
        :return: a list of networkx Graph of the subnet
        '''
        results = re.findall("\d+.+?\d+ \d+ \d+ \d+ [\.\d]+ [\.\d]+ [\.\d]+", res, re.DOTALL)
        res = []
        for x in results:
            m = MAGI_OUT(x.split('\n')[0], x.split('\n')[1: -1], x.split('\n')[-1].split(' '))
            res.append(nx.subgraph(G, m.genes))
        return res


if __name__ == '__main__':
    # MAGI._run_color_and_mut(MAGI.TEST_ARGS, 5, 1)
    MAGI.cluster(*list(MAGI.CLUSTER_ARGS.values()))


class Hotnet2:
    '''
    optimized Warper for algorithm hotnet2
    site: https://github.com/raphael-group/hotnet2
    original paper: M.D.M. Leiserson*, F. Vandin*, H.T. Wu, J.R. Dobson, J.V. Eldridge, J.L. Thomas, A. Papoutsaki,
     Y. Kim, B. Niu, M. McLellan, M.S. Lawrence, A.G. Perez, D. Tamborero, Y. Cheng, G.A. Ryslik, N. Lopez-Bigas,
      G. Getz, L. Ding, and B.J. Raphael. (2014) Pan-Cancer Network Analysis Identifies Combinations of Rare Somatic
       Mutations across Pathways and Protein Complexes. Nature Genetics 47, 106–114 (2015).

    '''
    pass
