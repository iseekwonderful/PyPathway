from jucell.display import Plotable, PlotOnlyInterface
import os
import networkx as nx
import math


class StylePresets:
    DEFAULT = {}
    RED = {
        'node': {'label': 'data(label)',
                 'width': 18,
                 'height': 18,
                 'font-size': '-1em',
                 'font-weight': 1,
                 'background-color': '#CC2025',
                 'border-width': 2,
                 'border-color': 'white'
                 },
        'edge': {
            'width': 3,
            'line-color': '#CC2025'
        },
        'spring_length': 50
    }
    ORANGE = {
        'node': {'label': 'data(label)',
                 'width': 18,
                 'height': 18,
                 'font-size': '-1em',
                 'font-weight': 1,
                 'background-color': '#F69924',
                 'border-width': 2,
                 'border-color': 'white'
                 },
        'edge': {
            'width': 3,
            'line-color': '#F69924'
        },
        'spring_length': 50
    }
    BLUE = {
        'node': {'label': 'data(label)',
                 'width': 18,
                 'height': 18,
                 'font-size': '-1em',
                 'font-weight': 1,
                 'background-color': '#4D90C8',
                 'border-width': 2,
                 'border-color': 'white'
                 },
        'edge': {
            'width': 3,
            'line-color': '#4D90C8'
        },
        'spring_length': 50
    }
    RED_CENTERED_LABEL = {
        'node': {'label': 'data(label)',
                 'width': 24,
                 'height': 24,
                 'font-size': '-1em',
                 'font-weight': 2,
                 'background-color': '#CC2025',
                 'border-width': 2,
                 'border-color': 'white',
                 'text-valign': 'center',
                 'text-halign': 'center',
                 'color': 'white'
                 },
        'edge': {
            'width': 3,
            'line-color': '#CC2025'
        },
        'spring_length': 50
    }
    ORANGE_CENTERED_LABEL = {
        'node': {'label': 'data(label)',
                 'width': 24,
                 'height': 24,
                 'font-size': '-1em',
                 'font-weight': 2,
                 'background-color': '#F69924',
                 'border-width': 2,
                 'border-color': 'white',
                 'text-valign': 'center',
                 'text-halign': 'center',
                 'color': 'white'
                 },
        'edge': {
            'width': 3,
            'line-color': '#F69924'
        },
        'spring_length': 50
    }
    BLUE_CENTERED_LABEL = {
        'node': {'label': 'data(label)',
                 'width': 24,
                 'height': 24,
                 'font-size': '-1em',
                 'font-weight': 2,
                 'background-color': '#4D90C8',
                 'border-width': 2,
                 'border-color': 'white',
                 'text-valign': 'center',
                 'text-halign': 'center',
                 'color': 'white'
                 },
        'edge': {
            'width': 3,
            'line-color': '#4D90C8'
        },
        'spring_length': 50
    }


class FromNetworkX(Plotable):
    def __init__(self, G, layout='cose', node_styles=None, edge_styles=None, label='node_name',
                 snapshot=False, preset=StylePresets.DEFAULT):
        self.nx = G
        self.layout = layout
        self.node_styles = node_styles
        self.edge_styles = edge_styles
        self.spring_length = 100
        if not preset == StylePresets.DEFAULT:
            self.node_styles = preset['node']
            self.edge_styles = preset['edge']
            self.spring_length = preset["spring_length"]
        self.menu = None
        self.label = label
        # if snapshot, the edge will be shorter and the text will be larger
        self.snapshot = snapshot

    def plot(self, menu=None):
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
        default_node = {'label': 'data(label)',
                        'width': 18,
                        'height': 18,
                        'font-size': '-1em',
                        'font-weight': 1,
                        'background-color': '#91c7ae',
                        'border-width': 2,
                        'border-color': '#2f4554'
                        }
        default_edge = {
                    'width': 1,
                    'line-color': '#b4bcc3'
                }
        config = {
            "type": "cy",
            "options": {
                "elements": [
                ],

                "layout": {
                    'name': 'cose-bilkent',
                    'animate': False,
                    'idealEdgeLength': self.spring_length,

                },
                "style": [
                    {
                        "selector": "node",
                        "style": self.node_styles or default_node
                    },
                    {
                        "selector": "edge",
                        "style": self.edge_styles or default_edge
                    }
                ]

            },
            'menu': self.menu if self.menu else None
        }
        layout = None
        if len(self.nx.node) > 20:
            # use the layout provided by
            layout = nx.spring_layout(self.nx, iterations=1000, k=1 / math.sqrt(len(self.nx.node)))
            config['options']['layout'] = {'name': 'preset'}
        for k, v in self.nx.node.items():
            label = k if self.label == 'node_name' else v[self.label]
            style = v.get('snapshot') if self.snapshot else v.get('style') or self.node_styles or default_node
            config['options']['elements'].append(
                {'group': 'nodes',
                 'data': {'id': k,
                          'label': label,
                          },
                 'style': style,
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
        if type(self.nx) == nx.Graph:
            exist_edge = []
            for k, v in self.nx.edge.items():
                if len(v):
                    for i, j in v.items():
                        edg = frozenset(sorted([k, i]))
                        if edg in exist_edge:
                            continue
                        exist_edge.append(edg)
                        config['options']['elements'].append({
                             'group': 'edges',
                             'data': {'source': k,
                                      'target': i,
                                      },
                             'style': j.get('style') or self.edge_styles or default_edge,
                             'tooltips': j.get('tooltips') or None
                        })
        else:
            # if it is a DiGraph, we should plot the arrow
            for k, v in self.nx.edge.items():
                if len(v):
                    for i, j in v.items():
                        config['options']['elements'].append({
                             'group': 'edges',
                             'data': {'source': k,
                                      'target': i,
                                      },
                             'style': j.get('style') or self.edge_styles or default_edge,
                             'tooltips': j.get('tooltips') or None
                        })
                        config['options']['elements'][-1]['style']["target-arrow-shape"] = "triangle"
                        config['options']['elements'][-1]['style']["target-arrow-fill"] = "filled"
                        config['options']['elements'][-1]['style']["target-arrow-color"] = config['options']['elements'][-1]['style']["line-color"]
                        config['options']['elements'][-1]['style']["arrow-scale"] = "10"
                        config['options']['elements'][-1]['style']['curve-style'] = 'bezier'
        # print(config)
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

    def plot(self):
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


# the shortcut from the from networkx
NetViz = FromNetworkX


