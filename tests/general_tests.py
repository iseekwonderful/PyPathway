import unittest
from pypathway import *
from pypathway.query.network import NetworkRequest, NetworkMethod, MultiThreadNetworkRequest
import sys
import os
if sys.version[0] == "2":
    from Queue import Queue
else:
    from queue import Queue
from map_tests import MappingAPITest
from pypathway.visualize.options import *


class NetworkTest(unittest.TestCase):
    #basic test
    def test_network_class(self):
        self.assertTrue(NetworkRequest("http://github.com", NetworkMethod.GET).text is not None)

    def test_network_exception(self):
        '''
        Use a fake proxy to trigger the Network Exception.
        '''
        try:
            NetworkRequest("http://github.com", NetworkMethod.GET, proxy=dict(http="sock5://127.0.0.1:80"))
        except Exception as e:
            self.assertTrue(isinstance(e, NetworkException))

    def test_multiple_thread_networking_requests(self):
        '''
        Test the Multi-thread module.
        '''
        threads = [MultiThreadNetworkRequest(
            "http://github.com", NetworkMethod.GET)
                   for _ in range(5)]
        [x.start() for x in threads]
        [x.join() for x in threads]

    def test_multiple_thread_networking_requests_exception(self):
        '''
        Test multi-thread requests exception.
        '''
        q = Queue()
        threads = [MultiThreadNetworkRequest(
            "http://github.com", NetworkMethod.GET, proxy=dict(http="sock5://127.0.0.1:80"), error_queue=q)
                   for _ in range(5)]
        [x.start() for x in threads]
        [x.join() for x in threads]
        self.assertTrue(isinstance(q.get()[1], NetworkException))

    # KEGG area
    def test_search_jak_in_kegg(self):
        self.assertEqual(1, len(PublicDatabase.search_kegg("jak")))

    def test_search_jak_and_hsa_in_kegg(self):
        jak_hsa = PublicDatabase.search_kegg("jak", organism="hsa")[0].load()
        ids = [x.id for x in jak_hsa.genes]
        ko = [x.ko for x in jak_hsa.genes]
        hsa = [x.hsa for x in jak_hsa.genes]
        self.assertTrue(ids is not None and ko is not None and hsa is not None)

    def test_search_b_cell_in_rno_in_kegg(self):
        bc_rno = PublicDatabase.search_kegg("jak", organism="rno")[0].load()
        ids = [x.id for x in bc_rno.genes]
        ko = [x.ko for x in bc_rno.genes]
        hsa = [x.rno for x in bc_rno.genes]
        self.assertTrue(ids is not None and ko is not None and hsa is not None)


    def test_retrieve_jak_in_kegg(self):
        self.assertTrue(PublicDatabase.search_kegg("jak")[0].load() is not None)

    def test_search_b_cell_in_kegg(self):
        self.assertEquals(5, len(PublicDatabase.search_kegg("b cell")))

    def test_retrieve_b_cell_in_kegg(self):
        self.assertTrue(PublicDatabase.search_kegg("b cell")[0].load() is not None)

    def test_search_g_protein_in_kegg(self):
        self.assertEquals(2, len(PublicDatabase.search_kegg("g protein")))

    def test_retrieve_g_protein_in_kegg(self):
        self.assertTrue(PublicDatabase.search_kegg("g protein")[0].load() is not None)

    def test_network_exception_kegg(self):
        try:
            PublicDatabase.search_kegg("jak",proxies=dict(http="sock5://localhost:80"))
        except Exception as e:
            self.assertTrue(isinstance(e, NetworkException))

    # WikiPathway area
    def test_search_jak_in_wp(self):
        self.assertTrue(PublicDatabase.search_wp("jak") is not None)

    def test_retrieve_jak_in_wp(self):
        from pypathway.core.GPMLImpl import GPMLParser
        self.assertTrue(isinstance(PublicDatabase.search_wp("jak")[0].load(), GPMLParser))

    def test_search_b_cell_in_wp(self):
        self.assertTrue(PublicDatabase.search_kegg("b cell") is not None)

    def test_retrieve_b_cell_in_wp(self):
        from pypathway.core.GPMLImpl import GPMLParser
        res = PublicDatabase.search_wp("b cell")[0]
        if not res.hasData:
            res.retrieve()
        self.assertTrue(isinstance(res.load(), GPMLParser))

    def test_search_g_protein_in_wp(self):
        self.assertTrue(PublicDatabase.search_kegg("g protein") is not None)

    def test_retrieve_g_protein_in_wp(self):
        from pypathway.core.GPMLImpl import GPMLParser
        res = PublicDatabase.search_wp("protein")[0]
        if not res.hasData:
            res.retrieve()
        self.assertTrue(isinstance(res.load(), GPMLParser))

    def test_network_exception_wp(self):
        try:
            PublicDatabase.search_wp("jak", proxies=dict(http="sock5://localhost:80"))
        except Exception as e:
            self.assertTrue(isinstance(e, NetworkException))

    def test_search_jak_in_reactome(self):
        self.assertTrue(PublicDatabase.search_reactome("jak") is not None)

    def test_retrieve_jak_in_reactome(self):
        res = PublicDatabase.search_reactome("jak", organism="Homo sapiens")[0]
        res.retrieve()
        self.assertTrue(res.load() is not None)

    def test_search_insulin_in_reactome(self):
        self.assertTrue(PublicDatabase.search_reactome("insulin") is not None)

    def test_retrieve_insulin_in_reactome(self):
        res = PublicDatabase.search_reactome("insulin")[0]
        res.retrieve()
        self.assertTrue(res.load() is not None)

    def test_search_exception_in_reactome(self):
        try:
            PublicDatabase.search_reactome("insulin", proxies=dict(http="sock5://localhost:80"))
        except Exception as e:
            self.assertTrue(isinstance(e, NetworkException))

    def test_retrieve_exception_in_reactome(self):
        res = PublicDatabase.search_reactome("insulin")[0]
        try:
            res.retrieve(proxies=dict(http="sock5://localhost:80"))
        except Exception as e:
            self.assertTrue(isinstance(e, NetworkException))


class LocalFilesAndAPITes(unittest.TestCase):
    def test_load_kgml_from_local_file(self):
        '''
        Test ALL/PART hsa pathway in KEGG, is FULL test takes long times, we choose few as default.
        :return:
        '''
        FULL = False
        count = 0
        for x in os.listdir("local_file/kegg/kgml"):
            if "kgml" not in x:
                continue
            png = x.replace("kgml", "png")
            ph = KEGGParser.parseFromFile("local_file/kegg/kgml/{}".format(x), "local_file/kegg/img/{}".format(png))
            self.assertTrue(ph is not None)
            count += 1
            if not FULL and count == 20:
                return

    def test_load_GPML_from_local_file(self):
        '''
        The dir local_file/wiki_hsa list all wikipathway's GPML of Homo sapiens, we test all these file to avoid
        potential error while parsing.
        notice export method may takes some times.
        '''
        res = []
        for dr in os.listdir("local_file/wp"):
            for fm in os.listdir("local_file/wp/{}".format(dr)):
                # if you are in mac, run into .DS_Store will cause the exception, interesting!
                if "gpml" in fm:
                    res.append(GPMLParser.parseFromFile("local_file/wp/{}/{}".format(dr, fm)))
        for x in res:
            x.export()
        for x in res:
            self.assertTrue(isinstance(x, GPMLParser))

    def test_load_bioPAX_from_local_file(self):
        # This Will call the external paxtools, so takes some time.
        FULL = False
        target = "owl_full" if FULL else "owl_lite"
        res = []
        for i, x in enumerate(os.listdir("local_file/{}".format(target))):
            if "owl" not in x or i < 7:
                continue
            print(x, i)
            res.append(BioPAXParser.parseFromFile("local_file/{}/{}".format(target, x)))
        for x in res:
            self.assertTrue(x is not None)

    def test_local_SBGN_from_local_file(self):
        FULL = False
        target = "sbgn_full" if FULL else "sbgn_lite"
        res = []
        for x in os.listdir("local_file/{}".format(target)):
            res.append(SBGNParser.parseFromFile("local_file/{}/{}".format(target, x)))
        for x in res:
            self.assertTrue(x is not None)

    def test_operate_a_KGML_pathway_object(self):
        FULL = False
        count = 0
        for x in os.listdir("local_file/kegg/kgml"):
            if "kgml" not in x:
                continue
            png = x.replace("kgml", "png")
            ph = KEGGParser.parseFromFile("local_file/kegg/kgml/{}".format(x), "local_file/kegg/img/{}".format(png))
            self.assertTrue(ph is not None)
            count += 1
            if not FULL and count == 20:
                return
            # father, children, root, is_root
            ph.summary()
            child = ph.children[0]
            if child.children:
                grandchild = child.children[0]
                self.assertEqual(grandchild.is_root, False)
                root = grandchild.root
            else:
                root = child.root
            self.assertEqual(root, ph)
            print(ph, child)
            # get genes, entites, reactions
            self.assertTrue(isinstance(ph.genes, list))
            self.assertTrue(isinstance(ph.entities, list))
            self.assertTrue(isinstance(ph.reactions, list))
            # get_x_by_x
            self.assertTrue(isinstance(ph.get_element_by_class("relation"), list))
            self.assertTrue(isinstance(ph.get_element_by_id("31"), list))
            self.assertTrue(isinstance(ph.get_element_by_name("activation"), list))
            self.assertTrue(isinstance(ph.get_element_by_type("gene"), list))
            print(count)

    def test_operate_a_pathway_from_internet(self):
        # while a pathway is from kegg database and with organism and ko_id we need to check more
        path = PublicDatabase.search_kegg("insulin", organism="hsa")[0].load()
        self.assertTrue(path is not None)
        self.assertTrue(path.is_root)
        self.assertTrue(path.children[0].father == path)
        self.assertTrue(path.children[0].root == path)
        # labels
        l = path.genes[0].display_name
        path.get_element_by_label(l)
        print(path.TSC1)
        e = path.genes[1]
        e.color = "red"
        path.set_color({e.id: "tea"})

    def test_operate_a_pathway_from_wp(self):
        path = PublicDatabase.search_wp("jak")[0].load()
        self.assertTrue(path is not None)
        self.assertTrue(path.is_root)
        self.assertTrue(path.children[0].father == path)
        self.assertTrue(path.children[0].root == path)
        # labels
        print(path.nodes)
        l = path.nodes[0].display_name
        path.get_element_by_label(l)
        print(path.TSC1)
        e = path.nodes[1]
        e.color = "red"

    def test_operate_a_GPML_pathway_object(self):
        '''
        Test pathway operate function at all pathway of hsa and rat.
        '''
        for dr in os.listdir("local_file/wp"):
            for fm in os.listdir("local_file/wp/{}".format(dr)):
                if "gpml" not in fm:
                    continue
                ph = GPMLParser.parseFromFile("local_file/wp/{}/{}".format(dr, fm))
                ph.summary()
                child = ph.children[10]
                root = child.root
                print(root, ph)
                # self.assertEqual(root, ph)
                self.assertEqual(child.is_root, False)
                # get genes, entites, reactions
                self.assertTrue(isinstance(ph.nodes, list))
                self.assertTrue(isinstance(ph.entities, list))
                self.assertTrue(isinstance(ph.reactions, list))
                self.assertTrue(isinstance(ph.find_by_class("Graphics"), list))
                self.assertTrue(isinstance(ph.get_child("Graphics"), GPMLParser))

    def test_operate_a_SBGN_pathway_object(self):
        target = "sbgn_lite"
        for x in os.listdir("local_file/{}".format(target)):
            ph = SBGNParser.parseFromFile("local_file/{}/{}".format(target, x))
            ph.summary()
            child = ph.children[0]
            root = child.root
            print(ph, child)
            # self.assertEqual(root, ph)
            self.assertEqual(child.is_root, False)
            self.assertTrue(isinstance(ph.nodes, list))
            self.assertTrue(isinstance(ph.entities, list))
            self.assertTrue(isinstance(ph.reactions, list))
            # get genes, entites, reactions
            self.assertTrue(isinstance(ph.get_element_by_id("edge10717445"), list))
            self.assertTrue(isinstance(ph.get_element_by_type("compartment"), list))
            self.assertTrue(isinstance(ph.get_element_by_class("glyph"), list))

    def test_reactome_sbgn_combine_with_BioPAX(self):
        fl = os.listdir("local_file/REACTOME_tc")
        for i, x in enumerate(fl):
            if "sbgn" in x and x.replace("sbgn", "xml") in fl:
                if i == 10:
                    return
                try:
                    sb = SBGNParser.parseFromFile("local_file/REACTOME_tc/{}".format(x),
                                                  "local_file/REACTOME_tc/{}".format(x.replace("sbgn", "xml")))
                    sb.fix_reactome()
                    sb.draw()
                except:
                    import traceback
                    print(traceback.format_exc())


class MappingAndPlottingTests(unittest.TestCase):
    def test_vc_kegg(self):
        MappingAPITest.test_value_change("KEGG")

    def test_vc_wp(self):
        MappingAPITest.test_value_change("WP")

    def test_vc_Reactome(self):
        MappingAPITest.test_value_change("Reactome")

    def test_connection_kegg(self):
        MappingAPITest.test_connection("KEGG")

    def test_connection_wp(self):
        MappingAPITest.test_connection("WP")

    def test_connection_Reactome(self):
        MappingAPITest.test_connection("Reactome")

    def test_popup_kegg(self):
        MappingAPITest.test_popup_windows("KEGG")

    def test_popup_wp(self):
        MappingAPITest.test_popup_windows("WP")

    def test_popup_Reactome(self):
        MappingAPITest.test_popup_windows("Reactome")


class VisualizeOptionTest(unittest.TestCase):
    def test_color_rgb_function(self):
        self.assertEqual(rgb(255, 255, 255), "#FFFFFF")

    def test_value_change_init(self):
        vc = ValueChanged({NP.COLOR: rgb(255, 255, 255), NP.SCALE: 2, NP.OPACITY: 0.8})
        vc2 = Prop(color="red", scale=2, opacity=0.5)
        self.assertTrue(vc2.json is not None)
        self.assertEqual(vc.json["value_changed"]["opacity"], 0.8)

    def test_connection_init(self):
        cn = Connection([Edge(0), Edge(1, 2), Edge(1, 3, "dotted"),
                         Edge(1, target_style=ValueChanged({NP.OPACITY: 0.5}))])
        self.assertEqual(cn.json["connection"][3][1]["target-style"]["value_changed"]["opacity"], 0.5)

    def test_hyper_link(self):
        hl = HyperLink(name="Google", url="http://www.google.com")
        self.assertEqual(hl.json["link"]["url"], "http://www.google.com")

    def test_popup_windows(self):
        img = ImageTab(name="Image", image_path="www.a.img")
        crt = ChartTab(name="chart", setting="HI")
        table = TableTab(name="Detailed", table=[[1, 2], [3, 4]])
        pp = PopUp([img, crt, table])
        self.assertEqual(pp.json["popup"]["tab"][0][1]["url"], "www.a.img")


if __name__ == '__main__':
    unittest.main()
