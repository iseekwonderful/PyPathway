class Analysis:
    @property
    def table(self):
        '''
        The result of functional enrichment, should be in the format of pandas.Dataframes

        :return: the table of analysis
        '''
        raise NotImplementedError()

    @property
    def main_property(self):
        '''
        The property used to plot in the bar chart, default is the -log2(columns)

        :return:
        '''
        raise NotImplementedError()

    @property
    def network_data(self):
        '''
        The property provide the network for the viz class

        :return:
        '''
        raise NotImplementedError()


class EnrichmentResult:
    def __init__(self, df, source_data, target, method, xlabel='-lg(P-Value)'):
        self.df, self.source_data, self.target, self.method, self.xlabel = df, source_data, target, method, xlabel
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
                            'right': '12%',
                            'bottom': '3%',
                            'containLabel': True
                        },
                        'xAxis': {
                            'type': 'value',
                            'boundaryGap': [0, 0.01],
                            'name': self.xlabel
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

