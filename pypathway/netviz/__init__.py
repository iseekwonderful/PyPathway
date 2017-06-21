from jucell.display import Plotable, PlotOnlyInterface
import os
import networkx as nx
import math


class Engine:
    CYTOSCAPE = 'cytoscape'
    VIVASVG = 'vivagraph.js.svg'
    VIVAWEBGL = 'vivagraph.js.webgl'
    D3 = 'D3'


class FromNetworkX(Plotable):
    def __init__(self, G, layout='cose', node_styles=None, edge_styles=None):
        self.nx = G
        self.layout = layout
        self.node_styles = node_styles
        self.edge_styles = edge_styles
        self.menu = None

    def plot(self, engine=Engine.CYTOSCAPE, menu=None):
        self.menu = menu
        pi = PlotOnlyInterface(host=self)
        return pi.update()

    @property
    def instance_name(self):
        return 'nx_plot'

    @property
    def assets_path(self):
        return os.path.dirname(os.path.realpath(__file__)) + '/assets'

    @property
    def config_path(self):
        return '/data/test2.json'

    def serialize(self):
        # generate the configs
        config = {
            "type": "cy",
            "options": {
                "elements": [
                ],

                "layout": {
                    'name': 'cose-bilkent',
                    'animate': False,
                    'idealEdgeLength': 200,

                },
                "style": [
                    {
                        "selector": "node",
                        "style": self.node_styles or {'label': 'data(label)',
                                                      'background-color': '#546570'}
                    },
                    {
                        "selector": "edge",
                        "style": self.edge_styles or {'opacity': 0.5}
                    }
                ]

            },
            'menu': self.menu if self.menu else None
        }
        layout = None
        if len(self.nx.node) > 20:
            # use the layout provided by
            layout = nx.spring_layout(self.nx, iterations=1000, k=0.08 / math.sqrt(len(self.nx.node)))
            config['options']['layout'] = {'name': 'preset'}
        for k, v in self.nx.node.items():
            config['options']['elements'].append(
                {'group': 'nodes',
                 'data': {'id': k,
                          'label': k,
                          },
                 'style': v.get('style') or {
                     'background-color': '#546570'
                    },
                 'position': {
                        'x': int(layout[k][0] * 1000) if layout else 0,
                        'y': int(layout[k][1] * 1000) if layout else 0
                    }
                 }
            )
            for key, value in v.items():
                if key == 'style' or key == 'position' or key == 'data':
                    continue
                config['options']['elements'][-1][key] = value
        for k, v in self.nx.edge.items():
            if len(v):
                for i, j in v.items():
                    config['options']['elements'].append({
                         'group': 'edges',
                         'data': {'source': k,
                                  'target': i,
                                  },
                         'style': j.get('style')
                    })
        return config

    @property
    def data(self):
        return self.serialize()


class FromCYConfig(Plotable):
    def __init__(self, config: dict):
        self.config = config

    def check(self):
        '''
        The cytoscape.js could be slow in certain situation, so check the node and edge count is necessary, remind user
        to switch to vivaGraph.js or d3.js.

        :return: a Warning or None
        '''
        pass

    def serialize(self):
        return self.config

    @property
    def data(self):
        return self.serialize()

    @property
    def instance_name(self):
        return 'cy_plot'

    @property
    def assets_path(self):
        return os.path.dirname(os.path.realpath(__file__)) + '/assets'

    @property
    def config_path(self):
        return '/data/test2.json'

    def on_change(self, *args, **kwargs):
        pass

    def deserialize(self):
        pass

    def plot(self, engine=Engine.CYTOSCAPE):
        pi = PlotOnlyInterface(host=self)
        return pi.update()


class DefaultStyle:
    def __init__(self):
        self.config = {
            'nodes': {
                'size': 20,
                'border-width': 2,
                'border-color': '#2f4554',
                'background-color': {
                    'circle': '#91c7ae',
                    'rectangle': '#61a0a8',
                    'triangle': '#546570',
                    'other': '#749f83'
                },
                'color': '#546570'
            },
            'edges': {
                'width': 2,
                'color': 'black'
            }
        }

    def json(self):
        return self.config

    @staticmethod
    def random():
        return None


class Style:
    def __init__(self):
        pass


