import unittest
from pypathway import *
import json
import traceback


class FullNetworkTests(unittest.TestCase):
    # def test_query_all_hsa_keyword_in_KEGG(self):
    #     with open("local_file/KEGG_tc.json") as fp:
    #         con = json.load(fp)
    #     for i, x in enumerate(con):
    #         res = PublicDatabase.search_kegg(x.replace("/", ""))
    #         if res:
    #             res[0].load(query_entity_data=False)
    #         print(i, len(res), x)
    #

    # def test_query_all_hsa_keyword_in_WP(self):
    #     with open("local_file/WP_tc.json") as fp:
    #         con = json.load(fp)
    #     for i, x in enumerate(con):
    #         try:
    #             res = PublicDatabase.search_wp(x.replace("/", ""))
    #             if res:
    #                 res[0].retrieve()
    #                 res[0].load().draw()
    #             print(i, len(res), x)
    #         except:
    #             print(traceback.format_exc())
    #             print("Error: {}".format(x))

    # debug
    def test_WP(self):
        res = PublicDatabase.search_wp("Adipogenesis")
        if res:
            res[0].load().draw()
