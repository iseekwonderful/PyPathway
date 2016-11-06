from xml.sax import parseString, ContentHandler
from .general import Pathway
from ..visualize.options import IntegrationOptions
from ..utils import environment as env
from ..utils import GPMLCorrespondeNodeNotFound
from xml.dom.minidom import Document
import json
import os
import shutil
import math
import sys
import time


def contain(rect, source_z, target, target_z):
    if math.fabs(target[0] - rect[0]) <= rect[2] / 2.0 and math.fabs(target[1] - rect[1]) < rect[3] / 2.0 and int(target_z) > int(source_z):
        return True
    else:
        return False


class Shape:
    def __init__(self, type, x, g):
        self.type, self.x, self.g = type, x, g


class GPMLParser(Pathway):
    '''
    GPMLParser, parse GPML format pathway data
    '''
    def __init__(self, _class, props, is_root=False):
        Pathway.__init__(self)
        self._class = _class
        self.props = props
        self._is_root = is_root
        self._children = []
        self._father = None
        self.value = None

        # for default vaule
        self.color = "black"
        self.bg_color = "white"
        self.opacity = 1
        self.scale = 1

    def _get_option(self):
        content = self.option.json if isinstance(self.option, IntegrationOptions) else {}
        for x in self.entities:
            if x.id not in content:
                if not x.color == "black" or not x.bg_color == "white" or not x.scale == 1 or not x.opacity == 1:
                    content[x.id] = {}
                    content[x.id]['default'] = {
                        "value_changed": {
                            "background-color": x.bg_color,
                            "color": x.color,
                            "opacity": x.opacity,
                            "scale": x.scale
                        }
                    }
            else:
                if 'default' not in content[x.id]:
                    if not x.color == "black" or not x.bg_color == "white" or not x.scale == 1 or not x.opacity == 1:
                        content[x.id]['default'] = {
                            "value_changed": {
                                "background-color": x.bg_color,
                                "color": x.color,
                                "opacity": x.opacity,
                                "scale": x.scale
                            }
                        }
        return content

    def draw(self, setting=None):
        '''
        Draw GPML pathway, In IPython notebook

        :param setting: preserved, currently no usage
        :return: a plot region in output area
        '''
        area_id = str(time.time()).replace(".", "")
        with open(os.path.dirname(os.path.abspath(__file__)) + "/../static/box.html") as fp:
            con = fp.read()
        if not os.path.exists(os.getcwd() + "/assets/GPML/"):
            shutil.copytree(os.path.dirname(os.path.abspath(__file__)) + "/../static/GPML/", os.getcwd() + "/assets/GPML")
        # if not self.option:
        #     self.option = []
        with open(os.getcwd() + "/assets/GPML/gpml_data/config_{}.json".format(area_id), "w") as fp:
            fp.write(json.dumps({"option": self._get_option()}))
        data = self.export()
        with open(os.getcwd() + "/assets/GPML/gpml_data/pathway_{}.xml".format(area_id), "w") as fp:
            if sys.version[0] == "3":
                fp.write(data.decode("utf8"))
            else:
                fp.write(data)
        ratio = "0.7"
        con = con.replace("{{path}}", "'assets/GPML/gpml_{}.html'".format(area_id)).replace("{{ratio}}", ratio).replace("{{time}}", area_id)
        # modity index.html
        with open(os.path.dirname(os.path.abspath(__file__)) + "/../static/GPML/gpml.html") as fp:
            gp_index = fp.read()
        with open(os.getcwd() + "/assets/GPML/gpml_{}.html".format(area_id), "w") as fp:
            fp.write(gp_index.replace("{{time}}", area_id))
        # modigy js
        with open(os.path.dirname(os.path.abspath(__file__)) + "/../static/GPML/gpml_data/interface_gpml.js") as fp:
            gp_index = fp.read()
        with open(os.getcwd() + "/assets/GPML/gpml_data/interface_gpml_{}.js".format(area_id), "w") as fp:
            fp.write(gp_index.replace("{{time}}", area_id))
        if env():
            from IPython.display import HTML
            return HTML(con)
        else:
            import webbrowser
            from ..utils import get_local_http_server
            ls = get_local_http_server(os.getcwd())
            try:
                webbrowser.open_new("http://localhost:{}/assets/GPML/gpml_{}.html".format(ls.port, area_id))
            except KeyboardInterrupt:
                exit()

    def export(self, format=None):
        '''
        Export the GPML file.

        :param format: raise warning, if not input a GPML
        :return: a string with GPML file conetent
        '''
        doc = Document()
        root = doc.createElement(self._class)
        for k, v in self.props.items():
            root.setAttribute(k, v)
        for x in self.children:
            x._xml_object(root, doc)
        doc.appendChild(root)
        return doc.toprettyxml(indent='  ', encoding="utf8")

    def _xml_object(self, father, doc):
        me = doc.createElement(self._class)
        for k, v in self.props.items():
            if k == "ref" or k == "_father" or k == "_is_root" or k == "_children" or k == "core_implement":
                continue
            if not v:
                continue
            if k == "_class":
                k = "class"
            if sys.version[0] == "2":
                me.setAttribute(k, str(v.encode("utf8")).decode("utf8"))
            else:
                me.setAttribute(k, str(v))
        father.appendChild(me)
        children = self.children
        for x in children:
            x._xml_object(me, doc)

    def integrate(self, id_lists, visualize_option_lists):
        '''
        Mapping data to pathway

        :param id_lists: list of graphic element's ID
        :param visualize_option_lists: a list of visualize option corresponds to each id
        :return: None
        '''
        self.option = IntegrationOptions()
        self.option.set(id_lists, visualize_option_lists)

    def _flatten(self, list):
        list.append(self)
        for x in self.children:
            x._flatten(list)

    def flatten(self):
        '''
        Flatten the pathway tree.

        :return: a list of nodes.
        '''
        result = []
        self._flatten(result)
        return result

    # the property should impl
    @property
    def root(self):
        '''
        The root of pathway

        :return: The root node of pathway
        '''
        father = self.father
        while not father.is_root:
            father = father.father
        return father

    @property
    def is_root(self):
        '''
        Check if current node is root

        :return: True if is root else false
        '''
        return self._is_root

    @property
    def father(self):
        '''
        Get self's father element

        :return: father node
        '''
        return self._father

    @property
    def children(self):
        '''
        Get list of children

        :return: a list of children nodes
        '''
        return self._children

    @property
    def members(self):
        '''
        Members in nodes (aka. self.flatten)

        :return: a flatten list of pathway tree's nodes
        '''
        return self.flatten()

    @property
    def nodes(self):
        '''
        Get the DataNode elements in a GPML format pathway tree

        :return: a list of nodes whose class is DataNode
        '''
        return [x for x in self.members if x._class == "DataNode"]

    @property
    def entities(self):
        '''
        Get pathway objects's nodes (aka. self.nodes)

        :return: self.nodes
        '''
        return self.nodes

    @property
    def reactions(self):
        '''
        Get the reactions in pathway (aka. class=Interaction)

        :return: a list of reaction
        '''
        return [x for x in self.members if x._class == "Interaction"]

    @property
    def graphics(self):
        '''
        Get the graphic elements in a GPML pathway (aka. class=Graphics)

        :return: a list of GPML pathway graphic
        '''
        return [x for x in self.flatten() if x._class == "Graphics"]

    def add_child(self, child):
        self._children.append(child)

    def set_father(self, father):
        self._father = father

    def xrefs(self):
        return [x for x in self.children if x._class == "Xref"]

    @property
    def external_id(self):
        '''
        Get the external database ID in a GPML file

        :return: a dict of external ID
        '''
        res = {}
        for x in self.xrefs():
            if x.props.get("Database") and x.props.get("ID"):
                res[x.props.get("Database")] = x.props.get("ID")
        return res

    @property
    def id(self):
        return self.props.get("GraphId")

    def summary(self, depth=0):
        '''
        Summary of what pathway has

        :param depth: tab's start count, if you are not anti-human, do not change this.
        :return: a string summary
        '''
        self_str = "\t" * depth + "{}: {}, value: {}\n".format(self._class,
                                   ", ".join(["{}: {}".format(k, v.encode("utf8")) for k, v in self.props.items()]),
                                                               self.value.encode("utf8") if self.value else None)
        for x in self._children:
            self_str += x.summary(depth=depth+1)
        return self_str

    def __repr__(self):
        return "class: {}, props: [{}], value: {}, database ID: {}\n".format(self._class,
                                             ",".join(["{}: {} ".format(k, v.encode("utf8")) for k, v in self.props.items()]),
                                                        self.value.encode("utf8") if self.value else None,
                                                                           self.external_id)

    def _find_by_class(self, _class, result):
        if self._class == _class:
            result.append(self)
        for x in self._children:
            x._find_by_class(_class, result)

    def find_by_class(self, _class):
        '''
        Find node by its class

        :param _class: the class wanna use.
        :return: a list of satisfied class
        '''
        result = []
        self._find_by_class(_class, result)
        return result

    def get_element_by_class(self, _class):
        '''
        Get the element who match certain class

        :param _class: the desired class
        :return: a list of nodes who match desired class
        '''
        return self.find_by_class(_class)

    def get_element_by_id(self, id):
        '''
        Get the element who match certain id

        :param id: the desired id
        :return: a list of nodes who match desired class
        '''
        return [x for x in self.flatten() if x.props.get("GraphId") == id]

    def get_element_by_label(self, name):
        '''
        Get the element who match certain label (aka. TextLabel)

        :param name: the desired name
        :return: a list of nodes who match the name.
        '''
        return [x for x in self.flatten() if x.props.get("TextLabel") == name]

    def get_element_by_type(self, type):
        '''
        Get the element who match certain type

        :param type: the desired type
        :return: a list of node who match the type
        '''
        return [x for x in self.flatten() if x.props.get("Type") == type]

    def get_element_by_oid(self, oid):
        '''
        Get element by ontology id(aka the id wikipathway provides or external database id)

        :return: a list of match node
        '''
        return [x for x in self.flatten() if hasattr(x, "external_id") and oid in x.external_id.values()]

    def get_child(self, _class):
        '''
        Get the child who match certain class

        :param _class: the class wanna use.
        :return: a satisfied node
        '''
        for x in self._children:
            if x._class == _class:
                return x
        else:
            return None

    def __getattr__(self, item):
        if item in ["__str__"]:
            raise AttributeError
        if item in ["external_id", "name"]:
            return None
        l = self.get_element_by_label(item)
        return l if l else None

    def __eq__(self, other):
        return id(self) == id(other)

    @staticmethod
    def parse(data):
        '''
        Parse a string to pathway object

        :param data: string format of pathway data
        :return: a GMPL pathway object
        '''
        hander = GPMLHandler()
        parseString(data.encode("utf8"), hander)
        return hander.root

    @staticmethod
    def parseFromFile(file):
        '''
        Parse from local file system, a path to file is needed.

        :param file: the path to the file
        :return: a gpml pathway object
        '''
        if sys.version[0] == "2":
            with open(file) as fp:
                return GPMLParser.parse(fp.read().decode("utf8"))
        else:
            with open(file, encoding="utf8") as fp:
                return GPMLParser.parse(fp.read())


class Heap(list):
    def __init__(self):
        list.__init__([])

    def push(self, element):
        self.insert(0, element)

    def peak(self):
        return self[0]


class GPMLHandler(ContentHandler):
    def __init__(self):
        ContentHandler.__init__(self)
        self.gap = 0
        self.root = None
        self.heap = Heap()
        self.current_content = ""

    def startElement(self, name, attrs):
        if name == "Pathway":
            self.root = GPMLParser(name, dict(attrs), True)
            self.heap.push(self.root)
        else:
            node = GPMLParser(name, dict(attrs), False)
            father = self.heap.peak()
            father.add_child(node)
            node.set_father(father)
            self.heap.push(node)

    def endElement(self, name):
        self.gap -= 1
        self.heap.pop(0)

    def characters(self, content):
        if content.strip():
            self.heap.peak().value = content.strip()
