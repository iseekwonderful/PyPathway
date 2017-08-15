import pandas as pd
# define class for draw table bar plot network and additional stats
import os
import time


class Settable:
    def config(self):
        '''
        The config for the setting panel, if not, nothing display

        :return:
        '''
        raise NotImplementedError()

    def listening_list(self):
        '''
        the id list for the listening id of the react module

        :return:
        '''
        raise NotImplementedError()

    def apply_function(self):
        '''
        the apply function in the iframe that tells the listen function what to call and what to pass

        :return:
        '''

        raise NotImplementedError()


class Table(Settable):
    def __init__(self, table: pd.DataFrame):
        self.table = table
        self.name = 'table'

    def config(self):
        return {
            'config': [
                {
                    'name': 'Show All',
                    'type': 'switch',
                    'id': 'switch',
                    'left': 'No',
                    'right': 'Yes'
                }, {
                    'name': 'Sort',
                    'type': 'multiple_choose',
                    'id': 'sort',
                    'values': ['pvalue', 'name']
                }, {
                    'name': 'display percent',
                    'type': 'slide',
                    'id': 'percent',
                    'max': 1,
                    'min': 0.1,
                    'step': 0.01
                }
            ]
        }

    def callback_config(self):
        return {
            'listen_id': 'A'
        }

    def render_content(self):
        content = '<table class="bordered striped centered responsive-table"><thead><tr>'
        for x in self.table.columns:
            content += "<th>{}</th>".format(x)
        content += '</tr></thead><tbody>'
        for i, x in self.table.iterrows():
            content += '<tr>'
            for j, e in x.iteritems():
                content += "<td>{}</td>".format(e)
            content += '</tr>'
        content += '</tbody></table>'
        return content


class BarPlot:
    pass


class Glyph:
    pass


class Stats:
    pass


class EnrichView:
    def __init__(self, elements):
        self.elements = elements

    def generate_call_back(self):
        '''
        Generete the call back function for the element change
        The configure should like this:
        {
            display: 'table'
            setting: {
                switch: 1,
                percent: 0.5,
                sort: name
            }
        }
        the JavaScript call back function listen the event and pass the event to the execute function or switch the
        display content.

        the callback is generate from the configure file from the element
        :return:
        '''



    def generate_card(self):
        '''
        Generate the card element, the setting pannel

        :return:
        '''
        with open(os.path.dirname(os.path.realpath(__file__)) + '/assets/templates/card_with_tab') as fp:
            con = fp.read()
        for x in self.elements:
            print(x.config())
        con = con.replace('{{ title }}', 'The GSEA enrichment analysis')
        tabs, contents = self.generate_card_tab()
        con = con.replace("{{ card_tabs }}", tabs).replace("{{ card_contents }}", contents)
        with open(os.path.dirname(os.path.realpath(__file__)) + '/assets/viz3.html') as fp:
            viz = fp.read()
        viz = viz.replace("{{ card }}", con)
        with open(os.path.dirname(os.path.realpath(__file__)) + '/assets/viz4.html', 'w') as fp:
            fp.write(viz)

    def generate_card_tab(self):
        '''
        This method generate the card body for the config

        :return:
        '''
        tabs = ""
        tabs_id = []
        tab_contents = []
        for i, x in enumerate(self.elements):
            tab_id = 'card_element-{}-{}'.format(str(time.time()), i)
            tabs_id.append(tab_id)
            if i == 0:
                tabs += '<li class="tab"><a class="active" href="#{}">{}</a></li>'.format(tab_id, x.name)
            else:
                tabs += '<li class="tab"><a href="#{}">{}</a></li>'.format(tab_id, x.name)
            card_content = EnrichView.generate_card_body(x, tab_id)
            tab_contents.append(card_content)
        return tabs, '\n'.join(tab_contents)

    @staticmethod
    def generate_card_body(element, element_id):
        print(element_id)
        div = '<div id="{}"><form action="#" id={} onchange="change_button(\'{}\')">{}</form></div>'
        content = ""
        for x in element.config()['config']:
            if x['type'] == "switch":
                content += EnrichView.generate_switch(x)
            if x['type'] == "multiple_choose":
                content += EnrichView.generate_choose(x)
            if x['type'] == 'slide':
                content += EnrichView.generate_slider(x)
        div = div.format(element_id, element_id + "F", element_id + "F", content)
        return div

    @staticmethod
    def generate_switch(config):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/assets/templates/switch') as fp:
            con = fp.read()
        con = con.replace('{{ describe }}', config['name']).replace('{{ id }}', config['id'])
        return con

    @staticmethod
    def generate_slider(config):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/assets/templates/slider') as fp:
            con = fp.read()
        con = con.replace('{{ name }}', config['name']).replace('{{ id }}', config['id'])
        con = con.replace("{{ min }}",
                          str(config['min'])).replace("{{ max }}",
                                                      str(config['max'])).replace("{{ step }}",
                                                                                  str(config['step']))
        return con

    @staticmethod
    def generate_choose(config):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/assets/templates/selector') as fp:
            con = fp.read()
        con = con.replace('{{ name }}', config['name']).replace('{{ id }}', config['id'])
        ops = ''
        for i, x in enumerate(config['values']):
            if i == 0:
                con = con.replace("{{ default }}", x)
            else:
                ops += '<option value="{}">{}</option>\n'.format(x, x)
        con = con.replace("{{ options }}", ops)
        return con

    def generate(self):
        # handle drew area first
        text = '<div class="col s8 m8 l8 xl8" style="height: 80px;background-color: #1abc9c">{}</div>'
        with open(os.path.dirname(os.path.realpath(__file__)) + '/assets/viz.html') as fp:
            con = fp.read()
        body = ""
        for x in self.elements:
            body += text.format(x.render_content())
        con = con.replace("{{ body }}", body)
        con = con.replace("{{ card_test }}", self.generate_config())
        with open(os.path.dirname(os.path.realpath(__file__)) + '/assets/viz3.html', "w") as fp:
            fp.write(con)
