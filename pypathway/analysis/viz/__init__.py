import pandas as pd
# define class for draw table bar plot network and additional stats
import os


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
                    'value': [0.1, 1],
                    'step': 0.01
                }
            ]
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

    def generate_config(self):
        total = ""
        for e in self.elements:
            # every element has a tab area
            tab_content = '<form action="#" id="form" onchange="change_button({})">'.format("fix")
            for x in e.config()['config']:
                if x['type'] == 'switch':
                    tab_content += '<div style="padding-top:10px;padding-bottom:10px"class="switch">\n<label>\n{}<input type="checkbox" id="{}">\n' + \
                                    '<span class="lever">\n</span>\n{}</label>\n</label>\n</div>\n'
                    tab_content = tab_content.format(x['left'], x['id'], x['right'])
                if x['type'] == 'multiple_choose':
                    tab_content += '<p>\n<select id="{}">\n'.format(x['id'])
                    for i, s in enumerate(x['values']):
                        if i >= 0:
                            tab_content += '<option value="{}">\n{}</option>\n'.format(s, s)
                    tab_content += '</select>\n</p>'
                if x['type'] == 'slide':
                    tab_content += '<p class="range-field">\n<input type="range" id="{}" min="{}" max="{}" step="{}" value="{}"/>\n</p>'.format(
                        x['id'], x['value'][0], x['value'][1], x['step'], x['value'][0]
                    )
            total += tab_content + '</form>'
        return total
