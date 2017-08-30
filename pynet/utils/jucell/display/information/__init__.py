from ..interfaces import InformationInterface
from ..utils import copy_dir
from .. import common
from ... import iframe
from shutil import rmtree
import time
import json
import os


class ListInterface(InformationInterface):
    def __init__(self, host):
        InformationInterface.__init__(self, host)
        self._name = str(time.time()).replace('.', '')
        common[self._name] = self
        self._call_back = "display.common['{}'].on_update".format(self._name)
        self.data = {"a": 1, "b": 2}

    def update(self):
        if not os.path.exists(os.path.abspath(os.path.curdir) + '/caches'):
            os.makedirs(os.path.abspath(os.path.curdir) + '/caches')
        if os.path.exists(os.path.abspath(os.path.curdir) + '/caches/tests'):
            rmtree(os.path.abspath(os.path.curdir) + '/caches/tests')
        copy_dir('/usr/local/lib/python3.5/site-packages/display/templates/information/tests',
                os.path.abspath(os.path.curdir) + '/caches/tests')
        self.save_data(os.path.abspath(os.path.curdir) + '/caches/tests')
        # print(os.path.abspath(os.path.curdir))
        return iframe('files/caches/tests/index.html')

    def on_update(self, data):
        self.data = data
        self.host.on_change(data)

    def save_data(self, path):
        p = path + '/data/nodes.json'
        with open(p, 'w') as fp:
            fp.write(json.dumps({'call_back': self._call_back,
                                 'data': self.host.data}))

    def __repr__(self):
        return self.update()

