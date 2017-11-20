from ...analysis import EnrichmentResult
from ...pathviz.query.network import NetworkMethod, NetworkRequest
import json
import pandas as pd
from io import StringIO
from ...netviz import FromCYConfig
from collections import defaultdict
import os
from scipy import stats
from statsmodels.sandbox.stats import multicomp
from ...utils import IdMapping, GeneSet, GMTUtils
import wget
from goatools.go_enrichment import GOEnrichmentStudy
from goatools.obo_parser import GODag
from goatools.associations import read_associations


class ExpressionData:
    def __init__(self, df, exp, background, diff_column='p-value', cutoff=0.05, class_vector=None,
                 pos_class=None, neg_class=None):
        self.df = df
        self.exp = exp
        self.background = background
        self.diff_column = diff_column
        self.cutoff = cutoff
        self.pos_class = pos_class
        self.neg_class = neg_class
        self.class_vector = class_vector

    @staticmethod
    def parse_diff_express_data(file, class_vector=None, pos_class=None,
                                neg_class=None, diff_columns='p-value', cutoff=0.05):
        '''
        This function parse the differential expression analysis result from READemption
        should be a table file contains the statistical of each gene
        
        :param file: the csv file
        :param class_vector: stand for the expression design of the data
        :param pos_class: positive or experiment group
        :param neg_class: negative or control group
        :param diff_columns: the columns for significance check
        :param cutoff: the threshold considers it is significance
        :return: instance of ExpressionData
        '''
        tdf = pd.read_csv(file, index_col=0)
        exp = list(tdf[tdf[diff_columns] < cutoff].index)
        background = list(tdf.index)
        return ExpressionData(tdf, exp, background, diff_columns, cutoff, class_vector, pos_class, neg_class)


class ORA(EnrichmentResult):
    '''
    Receive a set of study, background gene and a geneset, perform a Over-represnet analysis
    
    '''

    @staticmethod
    def run(study, pop, gene_set, adjust='fdr_bh'):
        '''
        Run a Over-represent analysis toward a gene set
        
        :param study: the significant gene set
        :param pop:  the background gene set
        :param gene_set: the function set
        :param adjust: the adjust method in the multiple tests, 
            details in http://www.statsmodels.org/dev/generated/statsmodels.sandbox.stats.multicomp.multipletests.html
        :return: the ORA analysis result
        '''
        gene_sets = gene_set if type(gene_set) == dict else GMTUtils.parse_gmt_file(gene_set)
        mapped = {k: list(set(v) & set([str(x) for x in pop])) for k, v in gene_sets.items()}
        s_mapped = {k: list(set(v) & set([str(x) for x in study])) for k, v in gene_sets.items()}
        result = {}
        for k, v in mapped.items():
            result[k] = stats.hypergeom.sf(len(s_mapped[k]) - 1, len(pop), len(mapped[k]), len(study))
        _, o, _, _ = multicomp.multipletests(list(result.values()), method=adjust)
        rfdr = {list(result.keys())[i]: o[i] for i in range(len(list(result.keys())))}
        # !
        df_result = {'name': [], 'mapped': [], 'number in study': [], 'p-value': [], 'fdr': []}
        for k, v in mapped.items():
            df_result['name'].append(k)
            df_result['mapped'].append(len(mapped[k]))
            df_result['number in study'].append(len(s_mapped[k]))
            df_result['p-value'].append(result[k])
            df_result['fdr'].append(rfdr[k])
        df = pd.DataFrame(df_result)
        df = df[['name', 'mapped', 'number in study', 'p-value', 'fdr']]
        return ORA(df, study, pop, adjust)

    def __init__(self, df, study, pop, adjust):
        EnrichmentResult.__init__(self, df, study, "ORA", "", 0, 4, '-lg(p-value)')
        self.df, self.study, self.pop, self.adjust = df, study, pop, adjust

    @property
    def main_property(self):
        return 'fdr'

    @property
    def graph(self):
        return None

    def overview(self):
        return "ORA based on custom dataset"

    def arguments(self):
        pass


class Reactome(EnrichmentResult):
    '''
    This class ths the HTTP wrapper of the Reactome Ananlysis server.
    
    '''
    @staticmethod
    def run(exp, organism=None):
        '''
        This method is implemented by the Reactome web server

        :param exp: the list of over expressed gene symbol
        :param organism: the organism, default is human
        :param cut_off: the cut off p value, default is 0.05
        :return: a reactome ora object.
        '''
        # submit the analysis
        url = 'http://www.reactome.org/AnalysisService/identifiers/?interactors=false&pageSize=200&page=1&sortBy=ENTITIES_FDR&order=ASC&resource=TOTAL'
        file = '\n'.join([str(x) for x in exp])
        res = NetworkRequest(url, NetworkMethod.POST, post_arg={
            'data': file,
            'headers': {
                'Content-Type': 'text/plain',
                'Accept': 'application/json'
            }
        })
        json_data = json.loads(res.text)
        if organism:
            for x in IdMapping.SPECIES:
                if organism in x:
                    organism = x[1]
                    break
            else:
                organism = None
        rows = 'name\tdbId\tfound\tp-value\tfdr\tspecies\n'
        for x in json_data['pathways']:
            if organism and not organism == x['species']['name']:
                continue
            rows += '{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                x['name'], x['dbId'], x['entities']['found'], x['entities']['pValue'], x['entities']['fdr'],
                x['species']['name']
            )
        return Reactome(pd.read_table(StringIO(rows)), organism, exp, json_data['identifiersNotFound'])

    def __init__(self, df, organism, exp, not_found):
        self.df, self.organism, self.exp, self.not_found = df, organism, exp, not_found
        EnrichmentResult.__init__(self, self.df, exp, 'Reactome', 'ORA', 0, 4, '-log(2, Fdr)')

    @property
    def main_property(self):
        return 'fdr'

    @property
    def graph(self):
        raise Exception("Reactome network")

    def overview(self):
        # this function render the significant pathway in the Reactome overview.
        pass

    def arguments(self):
        raise NotImplementedError()


class GO(EnrichmentResult):
    '''
    This class is the wrapper of the Goatools. Use the netviz.goviz.RelPlot to plot the go DAG  
    
    '''
    @staticmethod
    def run(study, pop, assoc, alpha=0.05, p_value=0.05, compare=False, ratio=None, obo='go-basic.obo', no_propagate_counts=False,
            method='bonferroni,sidak,holm', pvalcalc='fisher'):
        '''
        This is the wrapper of the Goatools function.
        
        :param study: a list of study gene
        :param pop: a list of population gene
        :param assoc: the association from the gene to the go term
        :return: 
        '''
        if type(study) == str and type(pop) == str:
            # load the study and pop from the file
            study, pop = GO._read_geneset(study, pop, compare=compare)
        else:
            # convert to the set
            study = frozenset(study)
            pop = set(pop)
        methods = method.split(",")
        if obo == 'go-basic.obo':
            obo = os.path.dirname(os.path.realpath(__file__)) + "/obo/go.obo"
        if not os.path.exists(obo):
            print("obo file not found, start to download")
            wget.download('http://purl.obolibrary.org/obo/go/go-basic.obo', obo)
        obo_dag = GODag(obo)
        propagate_counts = not no_propagate_counts
        if type(assoc) == dict:
            buf = ""
            for k, v in assoc.items():
                if not v: continue
                line = ";".join([str(x) for x in v if x])
                buf += "{}\t{}\n".format(k, line)
            path = os.path.dirname(os.path.realpath(__file__)) + "/assoc"
            with open(path, 'w') as fp:
                fp.write(buf)
            assoc = read_associations(path)
        elif type(assoc) == defaultdict:
            pass
        else:
            # if from a file
            assoc = read_associations(assoc)
        g = GOEnrichmentStudy(pop, assoc, obo_dag,
                              propagate_counts=propagate_counts,
                              alpha=alpha,
                              pvalcalc=pvalcalc,
                              methods=methods)
        results = g.run_study(study)
        # g.print_summary(results, min_ratio=ratio, indent=False, pval=p_value)
        r = 'GO\tNS\tenrichment\tname\tratio_in_study\tratio_in_pop\tp_uncorrected\tdepth\tstudy_count\tp_bonferroni\tp_sidak\tp_holm\thit\n'
        for x in results:
            r += x.__str__() + "\n"
        tb = pd.read_table(StringIO(r))
        return GO(tb, study, pop, assoc, alpha, p_value, compare, ratio, obo, no_propagate_counts, method, pvalcalc, obo_dag)


    @staticmethod
    def _read_geneset(study_fn, pop_fn, compare=False):
        pop = set(_.strip() for _ in open(pop_fn) if _.strip())
        study = frozenset(_.strip() for _ in open(study_fn) if _.strip())
        # some times the pop is a second group to compare, rather than the
        # population in that case, we need to make sure the overlapping terms
        # are removed first
        if compare:
            common = pop & study
            pop |= study
            pop -= common
            study -= common
            print("removed %d overlapping items\n" % (len(common)))
            print("Set 1: {0}, Set 2: {1}\n".format(
                len(study), len(pop)))

        return study, pop

    def __init__(self, df, exp, pop, assoc, alpha, p_value, compare, ratio, obo, no_propagate_counts, method, pvalcalc, dag):
        self.exp, self.pop, self.assoc, self.alpha, self.p_value, self.compare = exp, pop, assoc, alpha, p_value, compare
        self.ratio, self.obo, self.no_propagate_counts, self.method, self.pvalcalc = ratio, obo, no_propagate_counts, method, pvalcalc
        self.df, self.dag = df, dag
        EnrichmentResult.__init__(self, self.df, exp, "GO", 'ORA', 3, 9, xlabel='-lg(p_bonferroni)')

    def _gradient(self, index, count):
        end = (0xff, 0, 0)
        start = (0xff, 0xff, 0xff)
        return "#{:02X}{:02X}{:02X}".format(int(start[0] + (end[0] - start[0]) / count * index),
                                            int(start[1] + (end[1] - start[1]) / count * index),
                                            int(start[2] + (end[2] - start[2]) / count * index))

    def graph(self, thresholds=0.001, data=False):
        args = {x[0]: x for i, x in self.table.iterrows()}
        targets = [x[0] for _, x in self.table.iterrows() if x[6] < thresholds]
        configs = []
        edges = []
        nodes = []
        for x in targets:
            rec = self.dag[x]
            for i, x in enumerate(list(rec.get_all_parent_edges())):
                fs = frozenset(x)
                if fs not in edges:
                    edges.append(fs)
        nodes = set([list(x)[0] for x in edges] + [list(x)[1] for x in edges])
        # print(len(nodes))
        use_spring, layout = False, []
        config = {
            "type": "cy",
            "options": {
                "elements": [
                ],

                "layout": {
                    'name': 'preset' if use_spring else 'dagre',
                },
                "style": [
                    # from node style and edge style
                    {
                        "selector": "node",
                        "style": {
                            "content": "data(label)",
                        }
                    },
                    {
                        "selector": "edge",
                        "style": {
                            'background-color': 'pink',
                            "label": 'data(label)'
                        }
                    }
                ]

            }
        }
        for x in nodes:
            rec = self.dag[x]
            config['options']['elements'].append(
                {'group': 'nodes',
                 'data': {'id': rec.id.replace(":", ""), 'label': rec.name, 'level': rec.level,
                          'name': rec.name},
                 'style': {
                     'background-color': self._gradient(int(100 - args[x][9] * 100), 100),
                     'shape': 'roundrectangle',
                     'width': 'label',
                     'height': 'label',
                     'text-halign': 'center',
                     'text-valign': 'center',
                     'padding': '10px',
                     'text-wrap': 'wrap',
                     'text-max-width': '200px',
                     'color': '#000000',
                     'border-radius': '250px',
                     'border-color': '#000011',
                     'border-width': '2px',
                 },
                 'tooltip': {
                     # 'Name': r.name,
                     'Level': rec.level,
                     'Depth': rec.depth,
                     'id': rec.id,
                     'p-value': args[x][6],
                     'ratio_in_study': args[x][4],
                     'ratio_in_pop': args[x][5],
                     'p_bonferroni': args[x][9]
                 },
                 'expand': {
                     'source': 'local',
                     'targets': [x.id for x in rec.children + rec.parents]
                 },
                 'position': {'x': int(layout[rec.id][0] * 10000),
                              'y': int(layout[rec.id][1] * 10000)} if use_spring else None
                 }
            )
        for i, x in enumerate(edges):
            x = list(x)
            config['options']['elements'].append({'data': {
                'id': 'edge{}'.format(i),
                'source': x[0].replace(":", ""),
                'target': x[1].replace(":", ""),
                'label': 'is_a'
            }, 'style': {
                # "label": "data(label)",
                'curve-style': 'bezier',
                'width': 2,
                'target-arrow-shape': 'triangle',
                'opacity': 0.7
            }})
        if data:
            return config
        return FromCYConfig(config).plot()

    def overview(self):
        return ["Gene Ontology", 'ORA']

    @property
    def main_property(self):
        return 'p_uncorrected'

    def table_display(self):
        df = self.table.copy()
        del df["enrichment"]
        del df["depth"]
        del df['study_count']
        del df['GO']
        df = df.set_index(self.table.iloc[:, 0])
        del df.index.name
        return df.sort_values(by='p_holm')[:20].to_html()


class KEGG(EnrichmentResult):
    @staticmethod
    def run(study, pop, organism='hsa', adjust='fdr_bh'):
        for x in IdMapping.SPECIES:
            if organism in x:
                organism = x[3]
        gene_sets = GeneSet.get_kegg_geneset(organism)
        mapped = {k: list(set(v) & set([str(x) for x in pop])) for k, v in gene_sets.items()}
        s_mapped = {k: list(set(v) & set([str(x) for x in study])) for k, v in gene_sets.items()}
        result = {}
        for k, v in mapped.items():
            result[k] = stats.hypergeom.sf(len(s_mapped[k]) - 1, len(pop), len(mapped[k]), len(study))
        _, o, _, _ = multicomp.multipletests(list(result.values()), method=adjust)
        rfdr = {list(result.keys())[i]: o[i] for i in range(len(list(result.keys())))}
        # !
        df_result = {'ID': [], 'Name': [], 'mapped': [], 'deg': [], 'p-value': [], 'fdr': []}
        for k, v in mapped.items():
            df_result['ID'].append(k.split("::")[0])
            df_result['Name'].append(k.split("::")[1])
            df_result['mapped'].append(len(mapped[k]))
            df_result['deg'].append(len(s_mapped[k]))
            df_result['p-value'].append(result[k])
            df_result['fdr'].append(rfdr[k])
        df = pd.DataFrame(df_result)
        df = df[['ID', 'Name', 'mapped', 'deg', 'p-value', 'fdr']]
        return KEGG(df, study, pop, organism, adjust)

    def __init__(self, df, study, pop, organism, adjust):
        EnrichmentResult.__init__(self, df, study, "KEGG", "ORA", 1, 5, '-log(2, Fdr)')
        self.df, self.study, self.pop, self.organism, self.adjust = df, study, pop, organism, adjust

    # @property
    # def table(self):
    #     return self.df

    @property
    def main_property(self):
        return 'fdr'

    @property
    def graph(self):
        return None

    def overview(self):
        return "ORA based on KEGG dataset"

    def arguments(self):
        pass



