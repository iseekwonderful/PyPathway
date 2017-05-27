from ...analysis import ORASource, Analysis
from ...pathviz.query.network import NetworkMethod, NetworkRequest


class ORA(Analysis):
    @staticmethod
    def run(exp, pop=None, source=None, organism=None, cut_off=0.05, method=None):
        raise NotImplementedError()

    def stat(self):
        raise NotImplementedError()


class Reactome(ORA):
    @staticmethod
    def run(exp, pop=None, source=None, custom_set=None, organism=None, cut_off=0.05, method=None):
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
        print(res.text)

    def stat(self):
        pass


class GO:
    pass


class GoaAdaptor:
    pass


class KEGG:
    pass