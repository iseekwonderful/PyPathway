import unittest
import sys
sys.path.append("/Users/yangxu/PyPathway")

from pypathway.utils import IdMapping, ColorectalCancer


class IDMappingTest(unittest.TestCase):
    '''
    This class test the pypathway.utils.IDMapping class

    '''
    def test_load_database(self):
        for x in IdMapping.SPECIES:
            IdMapping.check_db_available(x[0])


    def test_convert(self):
        ds = ColorectalCancer().deg_list
        IdMapping.convert(ds, 'human', 'ENTREZID', 'SYMBOL')


if __name__ == '__main__':
    unittest.main()