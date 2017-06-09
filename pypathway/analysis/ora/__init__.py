# from ...analysis import ORASource, Analysis
# from ...pathviz.query.network import NetworkMethod, NetworkRequest

from goatools.go_enrichment import GOEnrichmentStudy
from goatools.obo_parser import GODag
from goatools.associations import read_associations
from goatools.multiple_testing import Methods
from goatools.pvalcalc import FisherFactory


# class ORA(Analysis):
#     @staticmethod
#     def run(exp, pop=None, source=None, organism=None, cut_off=0.05, method=None):
#         raise NotImplementedError()
#
#     def stat(self):
#         raise NotImplementedError()
#
#
# class Reactome(ORA):
#     @staticmethod
#     def run(exp, pop=None, source=None, custom_set=None, organism=None, cut_off=0.05, method=None):
#         '''
#         This method is implemented by the Reactome web server
#
#         :param exp: the list of over expressed gene symbol
#         :param pop: the population
#         :param source: the source, here default reactome
#         :param organism: the organism, default is human
#         :param cut_off: the cut off p value, default is 0.05
#         :param method: the method is ora
#         :return: a reactome ora object.
#         '''
#         # submit the analysis
#         url = 'http://www.reactome.org/AnalysisService/identifiers/?interactors=false&pageSize=100&page=1&sortBy=ENTITIES_FDR&order=ASC&resource=TOTAL'
#         file = '\n'.join([str(x) for x in exp])
#         res = NetworkRequest(url, NetworkMethod.POST, post_arg={
#             'data': file,
#             'headers': {
#                 'Content-Type': 'text/plain',
#                 'Accept': 'application/json'
#             }
#         })
#         print(res.text)
#
#     def stat(self):
#         pass


class GO:
    @staticmethod
    def run(study, pop, assoc, alpha=0.05, p_value=0.05, compare=False, ratio=None, obo='go-basic.obo', no_propagate_counts=False,
            method='bonferroni,sidak,holm', pvalcalc='fisher'):
        study, pop = GO.read_geneset(study, pop, compare=compare)
        print(study)
        methods = method.split(",")
        obo_dag = GODag(obo)
        propagate_counts = not no_propagate_counts
        g = GOEnrichmentStudy(pop, read_associations(assoc), obo_dag,
                              propagate_counts=propagate_counts,
                              alpha=alpha,
                              pvalcalc=pvalcalc,
                              methods=methods)
        results = g.run_study(study)
        g.print_summary(results, min_ratio=ratio, indent=False, pval=p_value)
        return results

    @staticmethod
    def read_geneset(study_fn, pop_fn, compare=False):
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


class GoaAdaptor:
    pass


class KEGG:
    pass


if __name__ == '__main__':
    path = '/Users/yangxu/goatools/'
    GO.run(path + 'data/study', path + 'data/population', path + 'data/association',
           obo=path + 'go-basic.obo')