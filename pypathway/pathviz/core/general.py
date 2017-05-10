# First write in 2016-7-30
# by sheep @ scut
# Usage: Pathway objects and interfaces
import json
import os

from pathviz.visualize import IntegrationOptions


class Pathway:
    def __init__(self):
        self.core_implement = None
        self.option = None
        pass

    '''
    This is the core object of this module, parse files from file or public database, provide methods for data
    export, integration, visualize and modify

    Attribute:
        core_implement: KEGG, BioPAX or SBGN.
    '''

    def export(self):
        '''
        Export self to certain pathway format
        :param format: the desire format want to export
        :return: a xml string of export result
        '''
        raise NotImplementedError

    def draw(self):
        '''
        draw self
        :return: None
        '''
        raise NotImplementedError

    def integrate(self, id_lists, visualize_option_lists):
        '''
        to integrate custom data to the pathway
        :param id_lists: the id list of a pathway
        :param visualize_option_lists: the visualize option of a pathway
        :return: None
        '''
        self.option = IntegrationOptions()
        self.option.set(id_lists, visualize_option_lists)

    # below is several property
    @property
    def root(self):
        raise NotImplementedError

    @property
    def is_root(self):
        raise NotImplementedError

    @property
    def children(self):
        raise NotImplementedError

    def flatten(self):
        raise NotImplementedError

    @property
    def members(self):
        raise NotImplementedError

    @property
    def nodes(self):
        raise NotImplementedError


data = None


def compress(data):
    data = sorted(data, key=lambda x: x[0])
    first_dif = [data[0]]
    print(data[0:10])
    for i, x in enumerate(data[1:]):
        first_dif.append((x[0] - data[i][0], x[1] - data[i][1]))
    print(max([x[0] for x in first_dif[1:]]))
    with open("/../static/assets/raw.json", "w") as fp:
        fp.write(json.dumps(data))


def vertex2id(v):
    global data
    if not data:
        with open(os.path.dirname(os.path.abspath(__file__)) + "/../static/assets/raw.json") as fp:
            con = json.loads(fp.read())
        data = {x[0]: x[1] for x in con}
    return data.get(int(v))
