import os
from jinja2 import Template
import json
from copy import deepcopy
import shutil
from ..netviz import FromNetworkX


class MAGIExport:
    @staticmethod
    def export(res, output_dirs='.'):
        items = []
        json_config = {}
        # generate the card layout
        for i, x in enumerate(res):
            if i % 2 == 0:
                current = {'has1': True, 'has2': False}
                current['F'] = {'tags': x.genes.keys(), 'id': "plot{}".format(i)}
                if i == len(res) - 1:
                    items.append(current)
            else:
                current['has2'] = True
                current['S'] = {'tags': x.genes.keys(), 'id': "plot{}".format(i)}
                items.append(current)
            json_config["plot{}".format(i)] = {
                'type': 'graph',
                'snap': FromNetworkX(x.graph).data
            }
        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates', 'enrichment')
        with open(template_path + "/card-magi.html") as fp:
            con = fp.read()
        t = Template(con)
        with open(template_path + "/index.html", 'w') as fp:
            fp.write(t.render(items=items))
        with open(template_path + '/js/card_template') as fp:
            con = fp.read()
        t = Template(con)
        with open(template_path + '/js/card.js', 'w') as fp:
            fp.write(t.render(config=json.dumps(json_config)))
        # save to folder
        path = os.getcwd() + "/magi_result" if output_dirs == '.' else output_dirs + '/magi_result'
        if os.path.exists(path):
            # exist path, delete it
            shutil.rmtree(path)
        # copy
        shutil.copytree(os.path.dirname(os.path.realpath(__file__)) + '/templates/enrichment', path)
        os.remove(path + '/card.html')
        os.remove(path + '/card-magi.html')
        os.remove(path + '/enrichment_display.html')


class Hotnet2Export:
    @staticmethod
    def export(result, output_dir='.'):
        pass


class EnrichmentExport:
    @staticmethod
    def export(results, sort_by_dataset=False, output_dirs='.'):
        '''
        Export a set of result to enrichment dir. if the enrichment folder exist, overwrite it
        
        :param results: a set of enrichment result object
        :param sort_by_dataset: weather have a dataset layer to sort different dataset
        :param output_dirs: the output dirs
        :return: None
        '''
        layout = {}
        snapshot = []
        detail = []
        if sort_by_dataset:
            pass
        else:
            layout = {'layer': 1, 'display': 'card'}
        for i, x in enumerate(results):
            detail.append({'bar': x.plot(data=True), 'overview': x.graph(data=True), 'table': x.table_display()})
            snapshot.append({'snap': x.snapshot(), 'id': 'plot{}'.format(i), 'tags': x.overview()})
        config = {"layout": layout, 'snapshot': snapshot, 'detail': detail}
        EnrichmentExport.generate_page_by_config(config)
        EnrichmentExport.generate_page_for_each_result(config)

        path = os.getcwd() + "/enrichment_results" if output_dirs == '.' else output_dirs + '/enrichment_results'
        if os.path.exists(path):
            # exist path, delete it
            shutil.rmtree(path)
        # copy
        shutil.copytree(os.path.dirname(os.path.realpath(__file__)) + '/templates/enrichment', path)
        os.remove(path + '/card.html')
        os.remove(path + '/enrichment_display.html')

    @staticmethod
    def generate_page_for_each_result(config):
        data = {}
        for i, x in enumerate(config['detail']):
            data[config['snapshot'][i]['id']] = x
        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates', 'enrichment')
        with open(template_path + '/js/enrichment_display_template') as fp:
            con = fp.read()
        t = Template(con)
        with open(template_path + '/js/enrichment_display3.js', 'w') as fp:
            fp.write(t.render(type='local', data=json.dumps(data)))
        with open(template_path + '/data/data2.json', 'w') as fp:
            json.dump(data, fp)
        with open(template_path + '/enrichment_display.html') as fp:
            con = fp.read()
        for i, x in enumerate(config['snapshot']):
            t = Template(deepcopy(con))
            with open(template_path + "/details/{}.html".format(x['id']), 'w') as fp:
                fp.write(t.render(table=config['detail'][i]['table']))

    @staticmethod
    def generate_page_by_config(config):
        # first generate the card page
        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates', 'enrichment')
        with open(template_path + '/card.html') as fp:
            con = fp.read()
        t = Template(con)
        items = []
        # generate the card layout
        for i, x in enumerate(config['snapshot']):
            if i % 2 == 0:
                current = {'has1': True, 'has2': False}
                current['F'] = {'id': x['id'], 'tags': x['tags'],
                                'path': './details/{}.html?id={}'.format(x['id'], x['id'])}
                if i == len(config['snapshot']) - 1:
                    items.append(current)
            else:
                current['has2'] = True
                current['S'] = {'id': x['id'], 'tags': x['tags'],
                                'path': './details/{}.html?id={}'.format(x['id'], x['id'])}
                items.append(current)
        with open(template_path + '/index.html', 'w') as fp:
            fp.write(t.render(items=items, title='Enrichments'))
        # generate the snapshot config
        snapshot_config = {}
        snapshot_config_path = template_path + "/data/card.json"
        for x in config['snapshot']:
            snapshot_config[x['id']] = {'type': 'chart', 'snap': x['snap'], 'detail': {"method": "ORA"}}
        with open(snapshot_config_path, 'w') as fp:
            json.dump(snapshot_config, fp)
        with open(template_path + '/js/card_template') as fp:
            con = fp.read()
        t = Template(con)
        with open(template_path + '/js/card.js', 'w') as fp:
            fp.write(t.render(config=json.dumps(snapshot_config)))


class PlotObject:
    def __init__(self):
        pass

    @property
    def graph(self):
        '''
        The content to display in the card's plot region in the list's expanding region
        supports: graph config, table html,  or a image

        :return: a json setting
        '''
        return None

    @property
    def title(self):
        '''
        The content to display as title, should contain basic information

        :return: the title string
        '''
        return None

    @property
    def viz_address(self):
        '''
        If available, click and redirect to here

        :return:
        '''
        return None

    @property
    def plot_type(self):
        '''
        A table, a network or a image?

        :return:
        '''
        return None


class Combine:
    def __init__(self, name, plots, configs):
        '''
        The combine presentation of bench of visualizations

        :param name: the name of this set of visualization
        :param plots: the list of plot objects
        :param configs: the configs of layouts
        '''
        self.name, self.plots, self.config = name, plots, configs

    @property
    def data(self):
        return {
            'name': self.name,
            'plots': [{
                'graph': x.graph, 'title': x.title, 'address': x.viz_address, 'type': x.plot_type
            } for x in self.plots],
            'config': self.config.card
        }

    def generate(self):
        '''
        generate the assets from the config with the settings

        :return: a html dir
        '''
        raise NotImplementedError()


class List(Combine):
    def __init__(self, plots, configs):
        Combine.__init__(self, 'list', plots, configs)

    def generate(self):
        pass


class Card(Combine):
    def __init__(self, plots, configs):
        Combine.__init__(self, 'card', plots, configs)

    def generate(self):
        '''
        generate the card index.html

        :return:
        '''
        card_count = len(self.plots)
        card_per_line = self.config.card['card_per_line']
        # read the necessary assets
        with open(os.path.dirname(os.path.realpath(__file__)) + '/templates/index.html') as fp:
            template = fp.read()
        with open(os.path.dirname(os.path.realpath(__file__)) + '/templates/card/card') as fp:
            card = fp.read()
        with open(os.path.dirname(os.path.realpath(__file__)) + '/templates/card/row') as fp:
            row = fp.read()
        card_contents = ''
        row_contents = ''
        for i, p in enumerate(self.plots):
            if i % card_per_line == 0:
                card_contents += row.replace('{{ cards }}', row_contents)
                row_contents = ""
            row_contents += card.replace('{{ id }}', 'card_{}'.format(i))\
                .replace("{{ height }}", str(self.config.card['card_height']))\
                .replace('{{ width }}', str(int(12 / self.config.card['card_per_line'])))
        padding = 'col s{} offset-s{}'.format(12 - 2 * self.config.card['padding'],
                                              self.config.card['padding'])
        template = template.replace("{{ card_content }}", card_contents)\
            .replace('{{ side_padding }}', padding)
        return template


class Layout:
    pass


class DefaultConfig(Layout):
    def __init__(self):
        self.card = {
            'padding': 2,
            'card_per_line': 3,
            'card_height': 15
        }