# HOTNET, KeyPathwayMiner and MAGI
from multiprocessing import Pool
import subprocess

class MAGI:
    '''
    The parallel warper of MAGI (Merge Affected Genes into Integrated networks)
    site: https://eichlerlab.gs.washington.edu/MAGI/

    '''
    EXECUTABLE_PATH = '/Users/yangxu/Library/Developer/Xcode/DerivedData/MAGI-cmkybopnjlqlcidnrzkxmmycmuop/Build/Products/Debug/MAGI'
    TEST_ARGS = {
        'PPI Network': ['-p', '/Volumes/Data/magi/StringNew_HPRD.txt'],
        'cases mutation list': ['-c', '/Volumes/Data/magi/ID_2_Autism_4_Severe_Missense.Clean_WithNew.txt'],
        'Gene CoExpression Id': ['-h', '/Volumes/Data/magi/GeneCoExpresion_ID.txt'],
        'CoExpression Matrix': ['-e', '/Volumes/Data/magi/adj1.csv.Tab.BinaryFormat'],
        'control mutation list': ['-d', '/Volumes/Data/magi/New_ESP_Sereve.txt'],
        'Length of genes': ['-l', '/Volumes/Data/magi/Gene_Name_Length.txt'],
        'run id': ['-i', 'test_run']
    }
    additional = "-nc 5 -nt 1"

    @staticmethod
    def make_pathway(args):
        colors, mutations = [8, 7, 6, 5], [4, 3, 2, 1]
        # colors, mutations = [5, 6], [1, 2]
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
        print(execute)
        r = subprocess.call(execute, shell=True)
        print(r)

    @staticmethod
    def cluster():
        pass

    @staticmethod
    def run_test():
        pass


if __name__ == '__main__':
    # MAGI._run_color_and_mut(MAGI.TEST_ARGS, 5, 1)
    MAGI.make_pathway(MAGI.TEST_ARGS)


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
