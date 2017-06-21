from ..netviz import FromCYConfig
from goatools.obo_parser import GODag, GOTerm
import networkx as nx
import math


class RelPlot:
    def __init__(self, rec: GOTerm, dag: GODag):
        if not isinstance(rec, GOTerm):
            raise Exception("Target of plot must be an instance of goatools.obo_parser.GOTerm")
        self.rec = rec
        self.config = {}
        self.nodes = []
        self.dag = dag

    def _gradient_color(self, gap):
        # start = (0x00, 0x39, 0x73)
        # end = (0xe5, 0xe5, 0xbe)
        start = (0x29, 0x80, 0xb9)
        end = (0x2c, 0x3e, 0x50)
        return [(int(start[0] + (end[0] - start[0]) / gap * x),
                 int(start[1] + (end[1] - start[1]) / gap * x),
                 int(start[2] + (end[2] - start[2]) / gap * x)) for x in range(gap + 1)]

    def serialize(self, level_color=True, tooltip=True):
        '''
        Generate a json file as the config of cytoscape

        :return: json contents
        '''
        # find a graduate color
        levels = max([self.dag.query_term(x).level
                      for x in list(self.rec.get_all_parents()) + list(self.rec.get_all_children())])
        graduate_color = ["#{:02X}{:02X}{:02X}".format(x[0], x[1], x[2]) for x in self._gradient_color(levels)]
        use_spring, G = False, None
        # for expand, the candidate node
        candidate_id, candidate = [], {}
        if len(list(self.rec.get_all_parents()) + list(self.rec.get_all_children())) > 200:
            # try networkx layout
            G, use_spring = nx.Graph(), True
        # print(graduate_color)
        # clear self.nodes
        self.nodes = []
        for i, x in enumerate(list(self.rec.get_all_parent_edges()) + list(self.rec.get_all_child_edges())):
            if use_spring:
                G.add_edge(x[0], x[1])
            self.nodes.append({'data': {
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
        if use_spring:
            layout = nx.spring_layout(G, scale=0.5, iterations=1000, k=0.3 / math.sqrt(
                len(list(self.rec.get_all_parents()) + list(self.rec.get_all_children()))))
            # print(layout)
        # puts into full configs
        self.nodes.append({'group': 'nodes',
                           'data': {'id': self.rec.id.replace(":", ""), 'label': self.rec.name, 'level': self.rec.level,
                                    'name': self.rec.name},
                           'style': {
                               'background-color': '#DA5961',
                               'shape': 'roundrectangle',
                               'width': 'label',
                               'height': 'label',
                               'text-halign': 'center',
                               'text-valign': 'center',
                               'padding': '10px',
                               'text-wrap': 'wrap',
                               'text-max-width': '200px',
                               'color': '#ffffff',
                               'border-radius': '250px'
                           },
                           'tooltip': {
                               # 'Name': r.name,
                               'Level': self.rec.level,
                               'Depth': self.rec.depth,
                               'id': self.rec.id
                           },
                           'expand': {
                               'source': 'local',
                               'targets': [x.id for x in self.rec.children + self.rec.parents]
                           },
                           'position': {'x': int(layout[self.rec.id][0] * 10000),
                                        'y': int(layout[self.rec.id][1] * 10000)} if use_spring else None
                           })
        for x in list(self.rec.get_all_parents()) + list(self.rec.get_all_children()):
            r = self.dag.query_term(x, verbose=False)
            candidate_id += [x.id for x in r.children + r.parents]
            self.nodes.append({'group': 'nodes',
                               'data': {
                                   'id': x.replace(":", ""),
                                   'label': r.name,
                                   'level': r.level,
                                   'name': r.name,
                                   'depth': r.depth},
                               'tooltip': {
                                   # 'Name': r.name,
                                   'Level': r.level,
                                   'Depth': r.depth,
                                   'id': x
                               },
                               'expand': {
                                   'source': 'local',
                                   'targets': [xx.id for xx in r.children + r.parents]
                               },
                               'style': {
                                   'background-color': graduate_color[r.level] if level_color else '#34495d',
                                   'shape': 'roundrectangle',
                                   'width': 'label',
                                   'height': 'label',
                                   'text-halign': 'center',
                                   'text-valign': 'center',
                                   'padding': '10px',
                                   'text-wrap': 'wrap',
                                   'text-max-width': '200px',
                                   'border-width': '2px',
                                   'border-color': graduate_color[r.level] if level_color else '#34495d',
                                   'color': '#ffffff'
                               },
                               'position': {'x': int(layout[x][0] * 10000),
                                            'y': int(layout[x][1] * 10000)} if use_spring else None
                               })
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
        exist = list(self.rec.get_all_parents()) + list(self.rec.get_all_children()) + [self.rec.id]
        for k, v in self.dag.items():
            candidate[v.id] = {
                'id': v.id,
                'name': v.name,
                'level': v.level,
                'depth': v.depth
            }
        config['options']['elements'] = self.nodes
        config['candidate'] = candidate
        config['default_node'] = {
             'group': 'nodes',
             'data': {
                 'id': 'id',
                 'label': 'name',
                 'level': 'level',
                 'name': 'name',
                 'depth': 'depth'},
             'tooltip': {
                 # 'Name': r.name,
                 'Level': 'level',
                 'Depth': 'depth',
                 'id': 'id'
             },
             'expand': {
                 'source': 'local',
                 'targets': 'targets'
             },
             'style': {
                 'background-color': '#34495d',
                 'shape': 'roundrectangle',
                 'width': 'label',
                 'height': 'label',
                 'text-halign': 'center',
                 'text-valign': 'center',
                 'padding': '10px',
                 'text-wrap': 'wrap',
                 'text-max-width': '200px',
                 'border-width': '2px',
                 'border-color': '#34495d',
                 'color': '#ffffff'
             },
             'position': {'x': 'x',
                          'y': 'y'}
        }
        config['default_edge'] = {
            'data': {
                'id': 'edgeid',
                'source': 's',
                'target': 't',
                'label': 'is_a'
            }, 'style': {
                'curve-style': 'bezier',
                'width': 2,
                'target-arrow-shape': 'triangle',
                'opacity': 0.7
            }
        }
        self.config = config
        # print(config)
        # return the config as data
        return self.config

    def plot(self, level_color=True, tooltip=True):
        # the go viz is using the cy plot interface, we need add the tooltip and the menu
        ci = FromCYConfig(config=self.serialize())
        return ci.plot()

