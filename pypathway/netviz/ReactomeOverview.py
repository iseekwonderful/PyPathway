import requests
import json
from ..netviz import FromCYConfig
import time


class ReactomeOverview:
    CONFIG = {
        "type": "cy",
        "options": {
            "elements": [
            ],

            "layout": {
                'name': 'preset'
            },
            "style": [
                {
                    "selector": "node",
                    "style": {'label': 'data(label)',
                              'width': 3,
                              'height': 3,
                              'background-color': '#91c7ae',
                              'border-width': 1,
                              'border-color': '#2f4554'
                              }
                },
                {
                    "selector": "edge",
                    'style': {
                        "curve-style": "haystack",
                        'width': 1,
                        'line-color': '#b4bcc3'
                    }
                }
            ]

        }
    }

    @staticmethod
    def all(species='Homo sapiens', config_only=False):
        r = requests.get('http://www.reactome.org/download/current/fireworks/{}.json?t={}'.format(
            species.replace(" ", "_"), str(int(time.time()))
        ))
        data = json.loads(r.text)
        r = requests.get('http://www.reactome.org/ReactomeRESTfulAPI/RESTfulWS/frontPageItems/{}'.format(
            species.replace(" ", '+')
        ))
        names = [x['displayName'] for x in json.loads(r.text)]
        config = ReactomeOverview.CONFIG
        for x in data['nodes']:
            config['options']['elements'].append({
                'group': 'nodes',
                'data': {
                    'id': x['dbId'],
                    'name': x['name'],
                    'label': x['name'] if x['name'] in names else None
                },
                'position': {
                    'x': x['x'],
                    'y': x['y']
                },
                'tooltip': {
                    'name': x['name'],
                    'id': x['dbId']
                },
                'style': {
                    'width': 6,
                    'height': 6
                } if x['name'] in names else None
            })
        for x in data['edges']:
            config['options']['elements'].append({
                'data': {
                    'source': x['from'],
                    'target': x['to']
                }
            })
        if config_only:
            return config
        c = FromCYConfig(config)
        return c.plot()

    @staticmethod
    def highlight(setting: dict, species='Homo sapiens'):
        '''
        This function highlight input pathway in the Reactome's Overview

        :param setting: the dict like {'dbId': {'color': 'red'}}
        :param species: the species
        :return: the plot
        '''
        # the naive implementation
        config = ReactomeOverview.all(species=species, config_only=True)
        for node in config['options']['elements']:
            if not node.get('group'):
                continue
            if str(node['data']['id']) in setting:
                if 'style' not in node:
                    node['style'] = {}
                node['style']['background-color'] = setting[str(node['data']['id'])]['color']
                node['style']['width'] = 12
                node['style']['height'] = 12
        c = FromCYConfig(config)
        return c.plot()




