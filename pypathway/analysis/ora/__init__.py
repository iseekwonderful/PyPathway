from ...analysis import Analysis, EnrichmentResult
from ...pathviz.query.network import NetworkMethod, NetworkRequest
import json
import pandas as pd
from io import StringIO
from ...pathviz.utils import plot_json
import math
from ...netviz.goviz import RelPlot
from ...netviz import FromCYConfig


from goatools.go_enrichment import GOEnrichmentStudy
from goatools.obo_parser import GODag
from goatools.associations import read_associations


class Reactome(Analysis, EnrichmentResult):
    @staticmethod
    def run(exp, organism=None, cut_off=0.05):
        '''
        This method is implemented by the Reactome web server

        :param exp: the list of over expressed gene symbol
        :param pop: the population
        :param source: the source, here default reactome
        :param organism: the organism, default is human
        :param cut_off: the cut off p value, default is 0.05
        :param method: the method is ora
        :return: a reactome ora object.
        '''
        # submit the analysis
        url = 'http://www.reactome.org/AnalysisService/identifiers/?interactors=false&pageSize=100&page=1&sortBy=ENTITIES_FDR&order=ASC&resource=TOTAL'
        file = '\n'.join([str(x) for x in exp])
        res = NetworkRequest(url, NetworkMethod.POST, post_arg={
            'data': file,
            'headers': {
                'Content-Type': 'text/plain',
                'Accept': 'application/json'
            }
        })
        json_data = json.loads(res.text)
        rows = 'name\tdbId\tfound\tp-value\tfdr\tspecies\n'
        for x in json_data['pathways']:
            if organism and not organism == x['species']['name']:
                continue
            rows += '{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                x['name'], x['dbId'], x['entities']['found'], x['entities']['pValue'], x['entities']['fdr'],
                x['species']['name']
            )
        return Reactome(pd.read_table(StringIO(rows)), organism, exp, cut_off)

    def __init__(self, df, organism, exp, cut_off):
        self.df, self.organism, self.exp, self.cut_off = df, organism, exp, cut_off
        EnrichmentResult.__init__(self, self.df, exp, 'Reactome', 'ORA', '-log(2, Fdr)')

    @property
    def table(self):
        return self.df

    @property
    def main_property(self):
        return 'fdr'

    @property
    def network_data(self):
        raise Exception("Reactome network")

    @property
    def plot(self, count=15):
        self.basic_config['yAxis']['data'] = []
        self.basic_config['series'][0]['data'] = []
        self.basic_config['title']['subtext'] = self.target
        self.basic_config['title']['text'] = "{} Enrichment Analysis".format(self.method.upper())
        candidate = []
        for x in self.df.iterrows():
            candidate.append([x[1][0], -math.log2(x[1][4])])
        candidate = sorted(candidate, key=lambda x: x[1], reverse=True)
        for x in candidate[:15]:
            self.basic_config['yAxis']['data'].append(x[0])
            self.basic_config['series'][0]['data'].append(x[1])
        # print(self.basic_config)
        return plot_json(self.basic_config)

    def overview(self):
        raise NotImplementedError()

    def detail(self, index):
        raise NotImplementedError()


class GO(Analysis, EnrichmentResult):
    @staticmethod
    def run(study, pop, assoc, alpha=0.05, p_value=0.05, compare=False, ratio=None, obo='go-basic.obo', no_propagate_counts=False,
            method='bonferroni,sidak,holm', pvalcalc='fisher'):
        study, pop = GO._read_geneset(study, pop, compare=compare)
        # print(study)
        methods = method.split(",")
        obo_dag = GODag(obo)
        propagate_counts = not no_propagate_counts
        g = GOEnrichmentStudy(pop, read_associations(assoc), obo_dag,
                              propagate_counts=propagate_counts,
                              alpha=alpha,
                              pvalcalc=pvalcalc,
                              methods=methods)
        results = g.run_study(study)
        # g.print_summary(results, min_ratio=ratio, indent=False, pval=p_value)
        r = 'GO\tNS\tenrichment\tname\tratio_in_study\tratio_in_pop\tp_uncorrected\tdepth\tstudy_count\tp_bonferroni\tp_sidak	p_holm\n'
        for x in results:
            r += x.__str__() + "\n"
        tb = pd.read_table(StringIO(r))
        return GO(tb, study, pop, assoc, alpha, p_value, compare, ratio, obo, no_propagate_counts, method, pvalcalc)


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

    def __init__(self, df, exp, pop, assoc, alpha, p_value, compare, ratio, obo, no_propagate_counts, method, pvalcalc):
        self.exp, self.pop, self.assoc, self.alpha, self.p_value, self.compare = exp, pop, assoc, alpha, p_value, compare
        self.ratio, self.obo, self.no_propagate_counts, self.method, self.pvalcalc = ratio, obo, no_propagate_counts, method, pvalcalc
        self.df = df
        EnrichmentResult.__init__(self, self.df, exp, "Reactome", 'ORA', xlabel='-lg(p_bonferroni)')

    @property
    def table(self):
        return self.df

    @property
    def plot(self, count=15):
        self.basic_config['yAxis']['data'] = []
        self.basic_config['series'][0]['data'] = []
        self.basic_config['title']['subtext'] = self.target
        self.basic_config['title']['text'] = "{} Enrichment Analysis".format(self.method.upper())
        candidate = []
        for x in self.df.iterrows():
            candidate.append([x[1][3], -math.log2(x[1][9])])
        candidate = sorted(candidate, key=lambda x: x[1], reverse=True)
        for x in candidate[:15]:
            self.basic_config['yAxis']['data'].append(x[0])
            self.basic_config['series'][0]['data'].append(x[1])
        # print(self.basic_config)
        return plot_json(self.basic_config)

    def _gradient(self, index, count):
        start = (0xff, 0, 0)
        end = (0xff, 0xff, 0xff)
        return "#{:02X}{:02X}{:02X}".format(int(start[0] + (end[0] - start[0]) / count * index),
                                            int(start[1] + (end[1] - start[1]) / count * index),
                                            int(start[2] + (end[2] - start[2]) / count * index))

    def overview(self, dag=None, thresholds=0.05):
        args = {x[0]: x for i, x in self.table.iterrows()}
        # print(args['GO:0009078'])
        # print("draw the network")
        targets = [x[0] for _, x in self.table.iterrows() if x[6] < 0.001]
        # print(targets)
        configs = []
        edges = []
        nodes = []
        for x in targets:
            rec = dag[x]
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
            rec = dag[x]
            config['options']['elements'].append(
                {'group': 'nodes',
                 'data': {'id': rec.id.replace(":", ""), 'label': rec.name, 'level': rec.level,
                          'name': rec.name},
                 'style': {
                     'background-color': self._gradient(int(100 - args[x][6] * 100), 100),
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
                     'p_bonferroni': args[x][8]
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
        return FromCYConfig(config).plot()

    def detail(self, index):
        raise NotImplementedError()

    @property
    def main_property(self):
        return 'p_uncorrected'

    @property
    def network_data(self):
        raise NotImplementedError()


class KEGG(Analysis):
    pass


# if __name__ == '__main__':
    # path = '/Users/yangxu/goatools/'
    # GO.run(path + 'data/study', path + 'data/population', path + 'data/association',
    #        obo=path + 'go-basic.obo')