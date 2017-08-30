import os
from shutil import rmtree, copytree
from .. import iframe
import json


common = {}


class PlotType:
    SBGN = 'sbgnviz'
    CYTOSACPES = 'cytoscapes'
    WPJS = 'wikipathway'
    INFORMATION = 'information'
    ECHARTS = 'echarts'


class Plotable:
    @property
    def instance_name(self):
        raise NotImplementedError()

    @property
    def data(self):
        return self.serialize()

    @property
    def assets_path(self):
        raise NotImplementedError()

    @property
    def config_path(self):
        '''
        get the RELATIVE path from assets path to config path.

        :return: the relative path
        '''
        raise NotImplementedError()

    # def __repr__(self):
    #     '''
    #     suggest to call plot
    #
    #     :return: None
    #     '''
    #     pass

    def plot(self):
        '''
        any plot object whom must implement this function, suggested to handle the __repr__ on the same way
        
        :return: None
        '''
        pass

    def on_change(self, *args, **kwargs):
        '''
        Interface call this function while handle is done, this should be implemented
        
        :return: None
        '''
        raise NotImplementedError()

    def serialize(self):
        '''
        Any time we need to send data to client, implement this method
        
        :return: 
        '''
        raise NotImplementedError()

    def deserialize(self):
        '''
        Any time we need parse data from client, using this method
        
        :return: 
        '''
        raise NotImplementedError()


class Interface:
    def __init__(self, host: Plotable):
        '''
        Abstract class Interface, plot plotable in output area and send JS event to plotable
        
        :param host: the object implement data and callback
        '''
        self.host = host

    def update(self):
        '''
        update plot on on the code side
        
        :return: None
        '''
        pass

    def on_update(self, data):
        '''
        js call this function while plot region update or user modify
        
        :param data: the data return from js
        :return: None
        '''
        pass

    def export_html(self):
        '''
        Export current display module as a statistic HTML with assets
        
        :return: 
        '''
        pass


class PlotOnlyInterface(Interface):
    def update(self):
        # print(self.host.assets_path)
        if not os.path.exists(os.path.abspath(os.path.curdir) + '/caches'):
            os.makedirs(os.path.abspath(os.path.curdir) + '/caches')
        if os.path.exists(os.path.abspath(os.path.curdir) + '/caches/' + self.host.instance_name):
            rmtree(os.path.abspath(os.path.curdir) + '/caches/' + self.host.instance_name)
        copytree(self.host.assets_path,
                 os.path.abspath(os.path.curdir) + '/caches/' + self.host.instance_name)
        self.save_data(os.path.abspath(os.path.curdir) + '/caches/' + self.host.instance_name)
        return iframe('files/caches/{}/index.html'.format(self.host.instance_name))

    def save_data(self, path):
        p = path + self.host.config_path
        with open(p, 'w') as fp:
            json.dump(self.host.data, fp)

