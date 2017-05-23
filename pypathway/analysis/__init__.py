class Analysis:
    pass


class ORASource:
    KEGG = 'kegg'
    Reactome = 'reactome'
    GENE_ONTOLOGY = 'gene_ontology'
    Custom = 'custom'


class GSEASource:
    pass


class DeNovoSource:
    pass


class EnrichmentResult:
    def __init__(self, df, source_data, target, method):
        self.df, self.source_data, self.target, self.method = df, source_data, target, method
        self.basic_config = {
                        'title': {
                            'text': 'Enrichment result',
                            'subtext': 'Unknown'
                        },
                        'tooltip': {
                            'trigger': 'axis',
                            'axisPointer': {
                                'type': 'shadow'
                            }
                        },
                        'grid': {
                            'left': '3%',
                            'right': '4%',
                            'bottom': '3%',
                            'containLabel': True
                        },
                        'xAxis': {
                            'type': 'value',
                            'boundaryGap': [0, 0.01]
                        },
                        'yAxis': {
                            'type': 'category',
                            'data': []
                        },
                        'series': [
                            {
                                'name': '-log(p-value)',
                                'type': 'bar',
                                'data': []
                            },
                        ]
                    }

    @property
    def plot(self):
        raise NotImplementedError()

    @property
    def table(self):
        raise NotImplementedError()

    def overview(self):
        raise NotImplementedError()

    def detail(self, index):
        raise NotImplementedError()


class ModelingResult:
    pass

