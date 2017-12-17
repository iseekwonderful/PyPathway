import sqlite3
import os
import tarfile
import requests
import wget
import re
import shutil
import time
import json
from collections import namedtuple
import pickle as pk
import networkx as nx


GMTInfo = namedtuple('GMTInfo', ['genesPerTerm', 'numTerms', 'link', 'libraryName', 'geneCoverage'])


class GMTUtils:
    @staticmethod
    def parse_gmt_file(file):
        '''
        parse a local gmt file,
        the file should be presented like:
        setName\tsource[optional]\tgenes....
        
        :param file: the file path
        :return: the parsed dict
        '''
        with open(file) as fp:
            con = fp.read()
        return {x.split('\t')[0]: [t for t in x.split('\t')[2:] if t] for x in con.split('\n') if x}

    @staticmethod
    def list_enrichr_gmt():
        r = requests.get('http://amp.pharm.mssm.edu/Enrichr/datasetStatistics?_={}'.format(int(time.time()))).text
        json_data = json.loads(r)
        result = []
        for x in json_data['statistics']:
            result.append(GMTInfo(**x))
        return result

    @staticmethod
    def get_enrichr_gmt(gmt):
        '''
        retrieve and parse the gmt file from enrichr database
        
        :param gmt: the GMTInfo instance or the gmt name name
        :return: 
        '''
        name = gmt if type(gmt) == str else gmt.libraryName
        r = requests.get('http://amp.pharm.mssm.edu/Enrichr/geneSetLibrary?mode=text&libraryName={}'.format(name)).text
        return {x.split('\t')[0]: [t for t in x.split('\t')[2:] if t] for x in r.split('\n') if x}


class GeneSet:
    @staticmethod
    def get_kegg_geneset(organism):
        url = "http://rest.kegg.jp/link/pathway/{}".format(organism)
        r = requests.get(url).text
        if len(r) == 0:
            raise Exception("Organism not found")
        result = {}
        for x in r.split("\n"):
            if not x: continue
            g, p = x.split("\t")
            if p.replace("path:".format(organism), '') not in result:
                result[p.replace("path:".format(organism), '')] = []
            result[p.replace("path:".format(organism), '')].append(g.replace("{}:".format(organism), ''))
        url = "http://rest.kegg.jp/list/pathway/{}".format(organism)
        r = requests.get(url).text
        id2name = {x.split("\t")[0].replace("path:", ""): x.split("\t")[1] for x in r.split('\n') if x}
        r = {}
        for k, v in result.items():
            r["{}::{}".format(k, id2name[k])] = v
        return r

    @staticmethod
    def get_reactome_geneset(organism):
        pass


class ExpressionData:
    pass


class ColorectalCancer(ExpressionData):
    '''
    The case from SPIA package,

    cite: Y. Hong, K. S. Ho, K. W. Eu, and P. Y. Cheah. A susceptibility gene set for early onset colorectal
        cancer that integrates diverse signaling pathways: implication for tumorigenesis. Clin Cancer
        Res, 13(4):1107–14, 2007.

    '''
    def __init__(self):
        ExpressionData.__init__(self)
        data_path = os.path.dirname(os.path.realpath(__file__)) +\
                    "/datasets/ColorectalCancer"
        with open(data_path + '/all') as fp:
            bg = fp.read()
        with open(data_path + '/de') as fp:
            de = fp.read()
        self.background = set([int(x.split(" ")[1][1:-1]) for x in bg.split('\n') if x])
        self.deg = {int(x.split(" ")[0][1:-1]): float(x.split(" ")[1]) for x in de.split('\n') if x}
        self.deg_list = list(self.deg.keys())
        self.idtype = 'ENTREZID'


class ALL(ExpressionData):
    '''
    Data of T- and B-cell Acute Lymphocytic Leukemia from the Ritz Laboratory at the DFCI (includes Apr 2004 versions)
    
    '''
    def __init__(self):
        ExpressionData.__init__(self)
        # lol tb
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'datasets/ALL/ALL')) as fp:
            con = fp.read()
        self.deg, self.deg_list, self.background = {}, [], []
        for x in con.split("\n")[1:]:
            if not x:
                continue
            a, b, c, d = x.split(" ")
            if float(c) < 0.05:
                self.deg[int(a.replace('"', ''))] = float(b)
                self.deg_list.append(int(a.replace('"', '')))
            self.background.append(int(a.replace('"', '')))


class IdMapping:
    '''
    This class provides the id mapping service
    For org.db

    '''
    SPECIES = [["anopheles", "Anopheles gambiae", "Ag", "aga", "anoGam", "7165"],
                ["bovine", "Bos taurus", "Bt", "bta", "bosTau", "9913"],
                ["canine", "Canis familiaris", "Cf", "cfa", "canFam", "9615"],
                ["chicken", "Gallus gallus", "Gg", "gga", "galGal", "9031"],
                ["chimp", "Pan troglodytes", "Pt", "ptr", "PanTro", "9598"],
                ["ecoliK12", "Escherichia coli K12", "EcK12", "eco", None, "562,83333,511145"],
                ["ecoliSakai", "Escherichia coli Sakai", "EcSakai", "ecs", None, "83334"],
                ["fly", "Drosophila melanogaster", "Dm", "dme", "dm", "7227"],
                ["human", "Homo sapiens", "Hs", "hsa", "hg", "9606"],
                ["mouse", "Mus musculus", "Mm", "mmu", "mm", "10090"],
                ["pig", "Sus scrofa", "Ss", "ssc", "susScr", "9823"],
                ["rat", "Rattus norvegicus", "Rn", "rno", "rn", "10116"],
                ["rhesus", "Macaca mulatta", "Mmu", "mcc", "rheMac", "9544"],
                ["worm", "Caenorhabditis elegans", "Ce", "cel", "ce", "6239"],
                ["xenopus", "Xenopus laevis", "Xl", "xla", "NA", "8355"],
                ["yeast", "Saccharomyces cerevisiae", "Sc", "sce", "sacCer", "4932,559292"],
                ["zebrafish", "Danio rerio", "Dr", "dre", "danRer", "7955"]]

    POSSIBLE_KEY  =  {"ENTREZID" : ["genes","gene_id"],
                     "PFAM" : ["pfam","pfam_id"],
                     "IPI" : ["pfam","ipi_id"],
                     "PROSITE" : ["prosite","prosite_id"],
                     "ACCNUM" : ["accessions","accession"],
                     "ALIAS" : ["alias","alias_symbol"],
                     "ALIAS2EG" : ["alias","alias_symbol"],
                     "ALIAS2PROBE" : ["alias","alias_symbol"],
                     "CHR" : ["chromosomes","chromosome"],
                     "CHRLOCCHR" : ["chromosome_locations","seqname"],
                     "CHRLOC" : ["chromosome_locations","start_location"],
                     "CHRLOCEND" : ["chromosome_locations","end_location"],
                     "ENZYME" : ["ec","ec_number"],
                     "MAP" : ["cytogenetic_locations","cytogenetic_location"],
                     "PATH" : ["kegg","path_id"],
                     "PMID" : ["pubmed","pubmed_id"],
                     "REFSEQ" : ["refseq","accession"],
                     "SYMBOL" : ["gene_info","symbol"],
                     "UNIGENE" : ["unigene","unigene_id"],
                     "ENSEMBL" : ["ensembl","ensembl_id"],
                     "ENSEMBLPROT" : ["ensembl_prot","prot_id"],
                     "ENSEMBLTRANS" : ["ensembl_trans","trans_id"],
                     "GENENAME" : ["gene_info","gene_name"],
                     "UNIPROT" : ["uniprot","uniprot_id"],
                     "GO" : ["go","go_id"],
                     "EVIDENCE" : ["go","evidence"],
                     "ONTOLOGY" : ["go","ontology"],
                     "GOALL" : ["go_all","go_id"],
                     "EVIDENCEALL" : ["go_all","evidence"],
                     "ONTOLOGYALL" : ["go_all","ontology"]
    }

    @staticmethod
    def read_from_cache(db):
        '''
        parse id database from local file
        
        :param db: the db name
        :return: if db exists, return the loaded db, else return none
        '''
        ppath = os.path.dirname(os.path.realpath(__file__)) + '/caches/{}'.format(db.replace('.db', '.sqlite'))
        if not os.path.exists(ppath):
            return None
        else:
            return SQLiteManager(ppath)

    @staticmethod
    def retrieve_database(db):
        '''
        Retrieve database from bioconductor.org, the database will stored at caches/{db}
        
        :param db: the database name
        :return: the parsed db
        '''

        print("Database {} not found, will be downloaded from bioconductor".format(db))
        # # get info
        r = requests.get("http://bioconductor.org/packages/release/data/annotation/html/{}.html".format(db))
        download_address = re.findall('href=\"\.\./(src/contrib/.+?tar\.gz)\"', r.text)
        if not download_address:
            raise Exception("Server may update, cant find download address")
        address = "http://bioconductor.org/packages/release/data/annotation/" + download_address[0]
        wget.download(address, out=os.path.dirname(os.path.realpath(__file__)) + "/db")
        IdMapping._uncompress(os.path.dirname(os.path.realpath(__file__)) + "/db")
        shutil.copy(os.path.dirname(os.path.realpath(__file__)) + "/{}/inst/extdata/{}".format(
            db, db.replace(".db", '.sqlite')), os.path.dirname(
            os.path.realpath(__file__)) + "/caches/" + db.replace(".db", '.sqlite'))
        shutil.rmtree(os.path.dirname(os.path.realpath(__file__)) + "/{}".format(db))
        os.remove(os.path.dirname(os.path.realpath(__file__)) + "/db")
        return SQLiteManager(os.path.dirname(os.path.realpath(__file__)) + "/caches/{}".format(
            db.replace('.db', '.sqlite')))

    @staticmethod
    def _uncompress(path):
        tar = tarfile.open(path, "r:gz")
        tar.extractall(path=os.path.dirname(os.path.realpath(__file__)))
        tar.close()

    @staticmethod
    def check_db_available(organism):
        '''
        check if database of certain organism is exist at bioconductor.org or local cache
        
        :param organism: organism
        :return: the loaded database
        '''
        for x in IdMapping.SPECIES:
            if organism in x:
                db = 'org.{}.eg.db'.format(x[2])
                break
        else:
            raise Exception("Can not find the organism")
        local_db = IdMapping.read_from_cache(db)
        if not local_db:
            local_db = IdMapping.retrieve_database(db)
        return local_db

    @staticmethod
    def convert(input_id, species, source, target):
        '''
        convert a list id 
        
        :param input_id: iter. id list
        :param species: the organism
        :param source: source id type
        :param target: target id type
        :return: a list [[sid, [tid1, tid2 ...]]...]
        '''
        db = IdMapping.check_db_available(species)
        return db.convert(input_id, source, target)

    @staticmethod
    def convert_to_dict(input_id, species, source, target):
        '''
        identical to the convert function, this function return a dict  
        
        :param input_id: iter. id lis
        :param species: the organism
        :param source: source id type
        :param target: target id type
        :return: a dict {sid: [tid1, ...]} if no target id for certain source id, source id will
        not exist in the dict.
        '''
        db = IdMapping.check_db_available(species)
        r = db.convert(input_id, source, target)
        return {x[0]: x[1] for x in r}

    @staticmethod
    def get_keys(organism):
        return IdMapping.check_db_available(organism).keys


    @staticmethod
    def clear():
        '''
        This method clear the local cache of all the database.

        :return:
        '''
        path = os.path.dirname(os.path.realpath(__file__)) + "/caches"
        for x in os.listdir(path):
            # delete sqlite database only
            if "sqlite" in x:
                os.remove(path + "/" + x)


class SQLiteManager:
    '''
    This class load a database and

    '''
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()
        self.exist_conversion = {}
        self.exist_table = []
        tables = []
        self.cursor.execute("SELECT * FROM sqlite_master where type='view'")
        for x in self.cursor.fetchall():
            tables.append(x[1])
        self.cursor.execute("SELECT * FROM sqlite_master where type='table'")
        for x in self.cursor.fetchall():
            tables.append(x[1])
        table2columns = {}
        for x in tables:
            self.cursor.execute('PRAGMA table_info({});'.format(x))
            table2columns[x] = [c[1] for c in self.cursor.fetchall()]
        for k, v in IdMapping.POSSIBLE_KEY.items():
            if v[0] in table2columns and v[1] in table2columns.get(v[0]):
                self.exist_table.append(k)
                self.exist_conversion[k] = v

    @property
    def keys(self):
        return self.exist_table

    def convert(self, ids, source, target):
        st, sc = self.exist_conversion[source]
        dt, dc = self.exist_conversion[target]
        if source not in self.exist_table or target not in self.exist_table:
            raise Exception("Keys not in the database, please refer to key method to get the support keys")
        sql = "select {}.{}, {}.{} from {} left join {} on {}._id = {}._id where {} in {}".format(
            st, sc, dt, dc, st, dt, st, dt, sc, "({})".format(', '.join(["'{}'".format(str(i)) for i in ids]))
        )
        self.cursor.execute(sql)
        s2t = {}
        for x in self.cursor.fetchall():
            if not str(x[0]) in s2t:
                s2t[str(x[0])] = []
            s2t[str(x[0])].append(x[1])
        result = [[x, s2t[str(x)]] if str(x) in s2t else [x, None] for x in ids]
        return result


def load_hint_hi12012_network():
    '''
    Load hint interactive network as a test network.

    :return: the networkx Graph
    '''
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'datasets/hint.bin'), 'rb') as fp:
        naive = pk.load(fp)
    if nx.__version__[0] == '2':
        G = nx.Graph()
        edges = []
        for i, j in naive.edge.items():
            for k, t in j.items():
                edges.append(frozenset([i, k]))
        G.add_edges_from(set(edges))
        return G
    else:
        return naive


if __name__ == '__main__':
    print(GMTUtils.parse_gmt_file('/Users/sheep/PyPathway/tests/gmt_file/h.all.v6.0.symbols.gmt'))
