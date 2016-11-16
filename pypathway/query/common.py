# Here we implement the pathway data objects of the pathway we support
# including the KEGG, Reactome, Pathway Common
from .network import MultiThreadNetworkRequest, NetworkMethod, NetworkException, NetworkRequest
import json
import re
import sys
import traceback
from ..utils import environment as env


if sys.version[0] == "2":
    from Queue import Queue
else:
    from queue import Queue


class PathwayFileFormatNotSupportException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message
    '''
    This class handle the unsupported file format of custome pathway file
    '''
    def __str__(self):
        return self.message


class PathwayFileReadException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message
    '''
    This class handle the exception while opening the custom pathway file
    '''
    def __str__(self):
        return self.message


# class SupportedOrganism:
#     def __init__(self):
#         pass
#     '''
#     This class represent the organism supported by Pathway Common, not KEGG
#     Currently, the integrate pathway data supported is only the Homo sapiens (9606)
#
#     Attributes:
#         Homo_Sapiens: 9606
#     '''
#     Homo_Sapiens = 9606


class SupportedDatabase:
    def __init__(self):
        pass
    '''
    This class lists the databases we support currently and the databases we wanna support in the feature.
    '''
    KEGG = 'kegg'
    REACTOME = 'reactome'
    PANTHER_Pathway = 'panther'
    WikiPathways = 'wikipathways'


# definition of the current support data format
class PathwayFormat:
    def __init__(self):
        self.des = "This is the class include the current support data format"
    '''
    This class list the format we support currently, and the format we wanna to support in the feature
    '''
    BioPAX = "BIOPAX"
    KGML = "KGML"
    SBGN = "SBGN"
    GPML = "GPML"


class PathwayData:
    def __init__(self, source, id, description, format, data):
        self.source = source
        self.description = description
        # formats is a list, of PathwayFormat
        self.formats = format
        self.data = data
        self.id = id

    '''
    This class is the super class of all class store raw pathway data(a search result contains 1 pathway), generally
     they contain the identifier(id), descriptions, source(database), format, data

    Args:
        source: the public database it comes from
        id: the unique identifier in the source database, if source is pathway common, its uri
        formats: member of PathwayFormat, we currently support BioPAX, SBGN-PD, KGML
        data: the raw pathway file data
        description: the description provide by source database

    Methods:
        summary: provide the information containing in this class
    '''

    def summary(self):
        '''
        Every subclass of PathwayData should have a summary method to tell the user what is in the instances

        :return:
        '''
        raise NotImplementedError


class ReactomePathwayData(PathwayData):
    def __init__(self, db_id, description, id, format, bioPAX, SBGN):
        PathwayData.__init__(self, "Reactome", id, description, format, bioPAX)
        self.SBGN = SBGN
        self.BioPAX = self.data
        self.db_id = db_id
        self.threads = []

    '''
    This class represent the pathway data query from Pathway Common, it provide the interface of many
    public database like:
        1. Reactome, 2. NCI Pathway Interaction Database: Pathway, 3. PhosphoSitePlus, 4. HumanCyc
        5. PANTHER Pathway, 6. Database of Interacting Proteins, 7. BioGRID, 8. IntAct, 9. WikiPathways

    Attributes:
        data: now it contains BioPAX format data of pathway
        SBGN: it contains the SBGN-PD graphic format of pathway
        BioPax: return data
    '''

    def summary(self):
        '''
        Get the summary for a pathway data.
        :return:
        '''
        return "source: {}\n id: {}\nBioPAX: {} \nSBGN-PD: {} \ndescription:{}\n".format(
            self.source, self.id, self.data is not None, self.SBGN is not None, self.description.encode("utf-8"),
            # Temp:
            "http://www.pathwaycommons.org/pc2/get?uri={}".format(self.id),
            "http://www.pathwaycommons.org/pc2/get?uri={}&format=sbgn".format(self.id)
        )

    def __repr__(self):
        return self.summary()

    def retrieve(self, proxies=None):
        '''
        Trying to fill the BioPAX and SBGN-PD data for certain pathway.

        :param proxies: if not None, proxies used by while requesting data.
        :return: None, but fill self's BioPAX and SBGN if it is empty
        '''
        query = []
        error = Queue()
        query.append(MultiThreadNetworkRequest(
            "http://www.reactome.org/ReactomeRESTfulAPI/RESTfulWS/biopaxExporter/Level3/{}".format(
                self.db_id # re.findall(r"\d+", self.id.split("/")[-1])[0]
            ),
            NetworkMethod.GET, self, "data", proxy=proxies, error_queue=error))
        query.append(MultiThreadNetworkRequest(
            "http://www.reactome.org/ReactomeRESTfulAPI/RESTfulWS/sbgnExporter/{}".format(
                # re.findall(r"\d+", self.id.split("/")[-1])[0]
                self.db_id
            ),
            NetworkMethod.GET, self, "SBGN", proxy=proxies, error_queue=error))
        self.threads.extend(query)
        try:
            [x.start() for x in self.threads]
            [x.join() for x in self.threads]
        except Exception as e:
            print("catched!")
            self.threads = []
            raise e
        finally:
            self.threads = []
            if self.data:
                self.data = self.data.encode("utf-8")
        while not error.empty():
            er = error.get()
            if er:
                raise NetworkException(er[0], er[1])

    def load(self, ratio=2):
        '''
        Load the pathway data instance to pathway object in the memory. By using SBGNParser with BioPAX file, later
        data provides the content in complex and database identifier information. Also fix_reactome will be called to
        fix the reactome layout issue. The ratio, is used for adjust the scale issue in the graphic.

        :param ratio: scale down to certain ratio, see the user-guide/format discuss, where introduce the issue we face
         and the solutions
        :return: a SBGN pathway object.
        '''
        if not self.SBGN or not self.data:
            # let load it
            self.retrieve()
            # raise Exception("load a reactome need the SBGN and BioPAX data, try retrieve first")
        try:
            from ..core.SBGNImpl import SBGNParser
            sb = SBGNParser.parse(self.SBGN, self.data)
            sb.fix()
            sb.fix_reactome(ratio)
            return sb
        except:
            print(traceback.format_exc())
            raise Exception("Error while parse SBGN file")


class WiKiPathwayData(PathwayData):
    def __init__(self, id, description, species, score, revision):
        PathwayData.__init__(self, SupportedDatabase.WikiPathways, id, description, [PathwayFormat.GPML], None)
        self.GPML = self.data
        self.species = species
        self.score = score
        self.revision = revision
        self.threads = []

    '''
    This class is used for storage the raw wiki pathway data, including the id, name, organism, reversion, score,
    field?
    '''

    def load(self):
        '''
        Quick method for load GMPL pathway data to the memory, GPMLParser is used in this function. You can use
        GPMLParser.parse(self.data) to load the pathway to the memory

        :return: A GPML pathway object
        '''
        from ..core.GPMLImpl import GPMLParser
        if not self.data:
            # retrieve it
            self.retrieve()
        return GPMLParser.parse(self.data)

    def __repr__(self):
        return self.summary()

    def summary(self):
        '''
        Get summary of this pathway data, if you screen the search result, you will see the output of the method, in
        a list(the search result is a list object contain a series of PathwayData class and subclass).

        :return: Summary of this pathway data object.
        '''
        return "\nid: {}\nname: {}\nspecies: {}\nrevision: {}\nhasData: {}\nscore: {}\n".format(
            self.id, self.description, self.species, self.revision, True if self.data else False, self.score
        )

    def retrieve(self, proxies=None, error_queue=None, single=True):
        '''
        In the search process, we does not fill the pathway data (self.data) due to the large amount of search result.
         so in the load() method, we using this method to retrieve the GPML format data. if you doesnt wanna retrieval
         and parse pathway using load() method, you need to call this method USING DEFAULT params.

        :param proxies: the proxies
        :param error_queue: the error_queue
        :param single: the single method
        :return:
        '''
        url = "http://webservice.wikipathways.org/getPathway?pwId={}&format=json".format(self.id)
        gpml = MultiThreadNetworkRequest(
            url, NetworkMethod.GET, self, "data", callback=self._process_data, proxy=proxies, error_queue=error_queue
        )
        self.threads.extend([gpml])
        [x.start() for x in self.threads]
        if single:
            self._join_active_thread()

    def _join_active_thread(self):
        [x.join() for x in self.threads]

    def _process_data(self, data):
        try:
            content = json.loads(data)["pathway"]["gpml"]
        except:
            Exception("Pathway Not found in database")
        self.data = content
        self.GPML = content

    @property
    def hasData(self):
        return True if self.data else False


class KEGGPathwayDataList:
    def __init__(self, results):
        self.results = results
        self.pos = 0

    def __repr__(self):
        return str([x for x in self])

    def __getitem__(self, item):
        if item >= len(self.results) or not type(item) == int:
            return None
        else:
            return self.results[item]

    def __iter__(self):
        return self

    def __next__(self):
        if self.pos >= len(self.results):
            self.pos = 0
            raise StopIteration()
        res = self.results[self.pos]
        self.pos += 1
        return res

    def next(self):
        if self.pos >= len(self.results):
            self.pos = 0
            raise StopIteration()
        res = self.results[self.pos]
        self.pos += 1
        return res


class KEGGPathwayData(PathwayData):
    def __init__(self, id, description, organsim):
        PathwayData.__init__(self, SupportedDatabase.KEGG, id, description, [PathwayFormat.KGML], None)
        self.png = None
        self.threads = []
        self.organism = organsim

    '''
    The class used for storage the raw KEGG pathway data, we first fill the info then request the background
    Image and KGML files

    Attribute:
        png: the background image of pathway
        threads: the available thread of while query png and KGML in a multi-thread way

    Methods:
        retrieve: this method design for multi-usage of KEGGPathwayData class, so in this situation, we call
        Thread's join() method by join_active_thread manually
        join_active_thread: join the thread self.thread has while requesting
    '''

    def load(self, proxies=None):
        '''
        Load the pathway data to pathway object in KGML data structure
        :param proxies: if not None, proxys for requesting.
        :return: a kegg pathway object (instance of KEGGPathway).
        '''
        from ..core.KGMLImpl import KEGGParser
        if not self.data:
            raise Exception("Target pathway have no data in {}".format(self.organism))
        kg = KEGGParser.parse(self.data, self.png)
        # update at 16-11-03
        url = "http://www.kegg.jp/kegg-bin/show_pathway?map{}".format(self.id)
        try:
            res = NetworkRequest(url, NetworkMethod.GET)
        except Exception as e:
            raise NetworkException(url, e)
        try:
            result = {}
            for x in re.findall(r"<area.+?coords=([\d,]+).+?title=\"(.+?)\" />", res.text):
                result[x[0]] = x[1]
            # match the result in pathway
            id2name = {}
            for x in kg.entities:
                g = x.graphic[0]
                if not g.x or not g.y or not g.width or not g.height:
                    continue
                addr = "{},{},{},{}".format(int(g.x - g.width / 2), int(g.y - g.height / 2),
                                            int(g.x + g.width / 2), int(g.y + g.height / 2))
                if not result.get(addr):
                    pass
                else:
                    # print(result.get(addr))
                    if "map" in result.get(addr):
                        x.ko_id = [result.get(addr)[:8]]
                    else:
                        id2name[x.id] = result.get(addr).split(",")[0].split(" ")[1][1: -1]
                        if not x.ko_id:
                            x.ko_id = []
                        for kx in result.get(addr).split(", "):
                            x.ko_id.append(kx.split(" ")[0].replace("\n", ""))
            kg.set_label(id2name)
        except:
            raise
        for x in kg.genes:
            hsa = x.name.split(" ")
            # print(hsa, self.organism)
            setattr(x, self.organism, hsa)
        return kg

    def summary(self):
        '''
        Return the basic information of this pathway class.

        :return:
        '''
        return "format: {}\nid: {}\ndescription: {}\nhasData: {}".format(
            "KGML", self.id, self.description, self.data is not None
        )

    # def html(self, i):
    #     import os
    #     with open(os.path.dirname(os.path.abspath(__file__)) + "/../static/midviz/kegg_element_template") as fp:
    #         tem = fp.read()
    #     return tem.replace("{{id}}", self.id).replace("{{name}}", self.description)\
    #         .replace("{{hasData}}", str(True if self.data else False)).replace("{{i}}", str(i))\
    #         .replace("{{image}}", "http://rest.kegg.jp/get/{}{}/image".format(self.organism, self.id))

    def __repr__(self):
        return self.summary()

    # retrieve the pathway info and KGML data
    def retrieve(self, organism="hsa", proxies=None, error=None):
        '''
        Retrieve KEGG pathway data, kgml and png. DO NOT use this method except you don't want to parse pathway use
        load() method.

        :param organism: the organism
        :param proxies: proxies
        :param error: error handle DO NOT USE THIS
        :return: None
        '''
        self.organism = organism
        kgml_url = "http://rest.kegg.jp/get/{}{}/kgml".format(organism, self.id)
        png_url = "http://rest.kegg.jp/get/{}{}/image".format(organism, self.id)
        kgml = MultiThreadNetworkRequest(kgml_url, NetworkMethod.GET, self, "data",
                                         proxy=proxies, error_queue=error)
        png = MultiThreadNetworkRequest(png_url, NetworkMethod.GET, self, "png",
                                        binary=True, proxy=proxies, error_queue=error)
        self.threads.extend([kgml, png])
        [x.start() for x in self.threads]

    def _join_active_thread(self):
        [x.join() for x in self.threads]

    def _parse_info(self, data):
        pass


class CustomPathwayFileData(PathwayData):
    def __init__(self, file_path, format, id=None, description=None, source=None):
        if format not in PathwayFormat.__dict__:
            raise PathwayFileFormatNotSupportException("Use the member of PathwayFormat likes: PathwayFormat.BioPAX")
        try:
            with open(file_path, "r") as fp:
                data = fp.read()
        except IOError as e:
            raise PathwayFileFormatNotSupportException("{}".format(e.args[1]))
        except Exception:
            raise PathwayFileFormatNotSupportException("Other error, see traceback")
        PathwayData.__init__(self, source, id, description, [format], data)

    '''
    This class support the reading of local pathway file supported by our program

    Args:
        file_path: the path of pathway file
        format: the file format, should be the member of PathwayFormat
        id: if has, its id in certain database or what you like
        description: if has, its description on certain database or what you like
        source: if has, the source of this pathway file

    Methods:
        summary: return the necessary information
    '''

    def summary(self):
        return "User provide data: file read: Pass\nFormat: {}, data size: {}".format(
            self.format, len(self.data)
        )

# if __name__ == '__main__':
#     data_from_file = CustomPathwayFileData("test.owl", PathwayFormat.SBGN, None, None, None)