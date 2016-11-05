# 2016-11-03 rewrite KGML module

from xml.sax import ContentHandler, parseString
from .SBGNImpl import TypeNotInNestedElementListError
from ..visualize.options import IntegrationOptions
from .general import Pathway as RootPathway
from ..utils import environment as env
import json
import os
import shutil
import sys
import time


class KEGGTagNotFoundException(Exception):
    def __init__(self):
        pass


class EntryGraphicRelationException(Exception):
    def __init__(self):
        pass


class BackgroundImageQueryException(Exception):
    def __init__(self):
        pass


class KEGGParser:
    '''
    The KEGG's KGML parser, return a KEGG pathway tree, you can visualize it using draw method, it is same like other
    pathway's object.
    '''
    @staticmethod
    def parse(data, png):
        handler = KEGGHandler(png)
        parseString(data, handler=handler)
        return handler.root

    @staticmethod
    def parseFromFile(kgml, png):
        if sys.version[0] == "2":
            with open(kgml) as fp:
                k = fp.read()
        else:
            with open(kgml, encoding="utf8") as fp:
                k = fp.read()
        if png:
            with open(png, "rb") as fp:
                p = fp.read()
        else:
            p = None
        return KEGGParser.parse(k, p)


class KEGGCaller:
    def __init__(self):
        self._call_dict = {
            "pathway": [Pathway, ["name", "org", "number", "title", "image", "link"]],
            "entry": [Entry, ["id", "name", "type", "link", "reaction"]],
            "component": [Component, ["id"]],
            "graphics": [Graphics, ["name", "x", "y", "coords", "type", "width", "height", "fgcolor"]],
            "reaction": [Reaction, ["id", "name", "type"]],
            "substrate": [Substrate, ["id", "name"]],
            "product": [Product, ["id", "name"]],
            "alt": [Alt, ["name"]],
            "relation": [Relation, ["entry1", "entry2", "type"]],
            "subtype": [Subtype, ["name", "value"]]
        }

    def call(self, name, attrs):
        if name not in self._call_dict:
            raise KEGGTagNotFoundException()
        # print name, dict(attrs)
        args = [attrs.get(x) for x in self._call_dict[name][1]]
        return self._call_dict[name][0](*args)


class Heap(list):
    def __init__(self):
        list.__init__([])

    def push(self, element):
        self.insert(0, element)

    def peak(self):
        return self[0]


class KEGGHandler(ContentHandler):
    def __init__(self, png):
        ContentHandler.__init__(self)
        self.png = png
        self.root = Pathway()
        self.heap = Heap()
        self.caller = KEGGCaller()

    '''
    Handler used by xml.sax.
    '''

    def startElement(self, name, attrs):
        if name == "pathway":
            self.root = self.caller.call(name, attrs)
            self.root.png = self.png
            self.heap.push(self.root)
            return
        super_name = self.heap.peak()
        current = self.caller.call(name, attrs)
        super_name.add_child(current)
        self.heap.push(current)

    def endElement(self, name):
        if self.heap.peak().class_ != name:
            raise AttributeError
        self.heap.pop(0)


class KEGGNode:
    '''
    This class is the subclass of a RootPathway (aka. Pathway class) and the root class of every KEGG class
    '''
    def __init__(self, name, ref):
        self.class_ = name
        self.ref = ref
        self.ko_id = []

    def add_child(self, child):
        child.father = self
        if child.class_ not in self.ref:
            raise TypeNotInNestedElementListError(child.name, self.ref.keys())
        self.ref[child.class_].append(child)

    def summary(self, deepth=0):
        '''
        The method to show node and its children's infromation

        :param deepth: option count of tab in child
        :return: a formatted string.
        '''
        refs = self.ref.values()
        result = []
        for x in refs:
            for y in x:
                result.append(y)
        if not result:
            return "...." * deepth + "class: {}, props: {}\n".format(self.class_, ", ".join(
                ["{}: {}".format(k, v) for k, v in self.__dict__.items()
                 if not k == "class_" and not k == "png" and not k == "father" and not isinstance(v, list)
                 and not k == "link" and v is not None and not isinstance(v, dict)]))
        else:
            result = "...." * deepth + "class: {}, props: {}\n".format(self.class_, ", ".join(
                ["{}: {}".format(k, v) for k, v in self.__dict__.items()
                 if not k == "class_" and not k == "png" and not k == "father" and not isinstance(v, list)
                 and not k == "link" and v is not None and not isinstance(v, dict)]))
            for x in refs:
                if x:
                    for y in x:
                        result += y.summary(deepth=deepth + 1)
            return result

    def __repr__(self):
        if self.class_ == "relation":
            return self.summary()
        elif self.class_ == "entry":
            return "class: {}, name: {}, type: {}, id: {}, KO: {}".format(
                self.class_, self.name, self.type, self.id, self.ko_id
            )
        elif self.class_ == "pathway":
            return "class: {}, name: {}, title: {}".format(
                self.class_, self.name, self.title
            )
        else:
            return self.summary()

    @property
    def ko(self):
        return self.ko_id

    @property
    def children(self):
        '''
        Get the list of self's children

        :return: list of children
        '''
        result = []
        for x in self.ref.values():
            for y in x:
                result.append(y)
        return result

    # this class should not be overwritten
    def export(self):
        '''
        Currently not implemented

        :return: None
        '''
        if not self.class_ == "pathway":
            raise Exception("Only root could be export!")
        raise NotImplementedError()

    @property
    def visualize_able(self):
        '''
        If the node is visualize able

        :return: Boolean, True if it is
        '''
        return False

    def _flatten(self, result):
        result.append(self)
        for x in self.children:
            x._flatten(result)

    def flatten(self):
        """
        Get the flatten of pathway tree

        :return: a list of all pathway nodes
        """
        result = []
        self._flatten(result)
        return result

    @property
    def root(self):
        '''
        Get the pathway's root elements

        :return: The root of a pathway object
        '''
        father = self.father
        while not father.class_ == "pathway":
            father = father.father
        return father

    # test function for creating a interacting api for user in cytoscope.js
    def derive_data(self, glyph_list):
        '''
        Get the config json, there is no needs to call this fnction
        '''
        if not self.visualize_able and not self.children:
            return
        if self.visualize_able:
            if self.data:
                glyph_list[self.data[0]] = self.data[1]
        if self.children:
            for x in self.children:
                x.derive_data(glyph_list)

    @property
    def id_lists(self):
        '''
        List fo IDs
        :return: a list of useful ids
        '''
        if self.class_ == "relation":
            return [self.entry2]
        av = []
        av.append(self.id)
        av.append(self.name)
        if self.ko_id:
            for x in self.ko_id:
                av.append(x)
        return av

    @property
    def is_root(self):
        return self.class_ == "pathway"


class Pathway(KEGGNode, RootPathway):
    '''
    In KEGG's specification, the pathway is defined in Pathway class, so we use it.
    Caution: If you use this with our ROOT Pathway class use import as to avoid namespace conflict.
    '''
    def __init__(self, name=None, org=None, number=None, title=None, image=None, link=None):
        self.name, self.org, self.number, self.title, self.image, self.link = name, org, number, title, image, link
        self.entry, self.relation, self.reaction = [], [], []
        self.xrange, self.yrange, self.father = 1273, 803, None
        self.father = self
        # self.is_root = True
        self.png = None
        KEGGNode.__init__(self, "pathway", {"entry": self.entry, "relation": self.relation, "reaction": self.reaction})

    def draw(self, area_id=None):
        '''
        Draw the content in ipython notebook!
        :return: return a HTML objects in ipython notebook.
        '''
        # calculate the area_id and prepare the HTML element
        if not area_id:
            area_id = str(time.time()).replace(".", "")
        with open(os.path.dirname(os.path.abspath(__file__)) + "/../static/box.html") as fp:
            con = fp.read()
        # is asset/KEGG not exist, copy it!
        if not os.path.exists(os.getcwd() + "/assets/KEGG/"):
            shutil.copytree(os.path.dirname(os.path.abspath(__file__)) + "/../static/KEGG",
                            os.getcwd() + "/assets/KEGG")
        # derive the options
        graph = {}
        self.derive_data(graph)
        with open(os.getcwd() + "/assets/KEGG/kegg_data/bg_{}.png".format(area_id), "wb") as fp:
            fp.write(self.png)
        from ..utils import get_image_size as gs
        w, h = gs(os.getcwd() + "/assets/KEGG/kegg_data/bg_{}.png".format(area_id))
        if not self.option:
            self.option = []
        with open(os.getcwd() + "/assets/KEGG/kegg_data/config_{}.json".format(area_id), "w") as fp:
            fp.write(json.dumps({"pathway": graph, "option": self._get_option(), #self.option.json if isinstance(self.option,
                                                                                            #IntegrationOptions) else self.option,
                                 "bg": {"width": w, "height": h}}))
        if sys.version[0] == '3':
            with open(os.path.dirname(os.path.abspath(__file__)) + "/../static/KEGG/kegg.html", encoding="utf8") as fp:
                kg_index = fp.read()
            with open(os.getcwd() + "/assets/KEGG/kegg_{}.html".format(area_id), "w") as fp:
                fp.write(kg_index.replace("{{time}}", area_id))
        else:
            with open(os.path.dirname(os.path.abspath(__file__)) + "/../static/KEGG/kegg.html") as fp:
                kg_index = fp.read().decode("utf8").encode("utf8")
            with open(os.getcwd() + "/assets/KEGG/kegg_{}.html".format(area_id), "w") as fp:
                fp.write(kg_index.replace("{{time}}", area_id))
        # js
        with open(os.path.dirname(os.path.abspath(__file__)) + "/../static/KEGG/kegg_data/interface_kegg.js") as fp:
            kg_index = fp.read()
        with open(os.getcwd() + "/assets/KEGG/kegg_data/interface_kegg_{}.js".format(area_id), "w") as fp:
            fp.write(kg_index.replace("{{time}}", area_id))
        # the kegg view
        ratio = str(float(h) / w)
        con = con.replace("{{path}}",
                          "'assets/KEGG/kegg_{}.html'".format(area_id)).replace("{{ratio}}", ratio).replace("{{time}}", area_id)
        # different in environment, do diff things
        if env():
            from IPython.display import HTML
            return HTML(con)
        else:
            import webbrowser
            from ..utils import get_local_http_server
            ls = get_local_http_server(os.getcwd())
            try:
                webbrowser.open_new("http://localhost:{}/assets/KEGG/kegg_{}.html".format(ls.port, area_id))
            except KeyboardInterrupt:
                exit()

    def integrate(self, id_lists, visualize_option_lists):
        total_id = [x.id_lists for x in self.entities]
        new = []
        new_option = []
        for i, x in enumerate(id_lists):
            for exist in total_id:
                if x in exist:
                    new.append(exist[0])
                    new_option.append(visualize_option_lists[i])
                    break
        io = IntegrationOptions()
        # if there is a connection, change the target id
        for x in visualize_option_lists:
            for k, v in x.__dict__.items():
                if "connection" in v:
                    for c in v["connection"]:
                        for ids in total_id:
                            if c[0] in ids:
                                c[0] = ids[0]
        io.set(new, new_option)
        self.option = io

    def _get_option(self):
        option = self.option.json if self.option else {}
        # print(self.option.json if self.option is not [] else [])
        # any time if you have option in integrate option, will overwrite the options
        for x in self.genes:
            if x.id in option:
                if "value_changed" in option[x.id]["default"]:
                    continue
                else:
                    option[x.id]["default"] = {"value_changed": {"color": x.color, "background-color": x.bg_color,
                                                                 "opacity": x.opacity, "scale": x.scale}}
            if x.id not in option:
                option[x.id] = {
                    'left': {},
                    'default': {
                        "value_changed": {
                            "color": x.color,
                            "background-color": x.bg_color,
                            "opacity": x.opacity,
                            "scale": x.scale
                        }
                    },
                    'right': {},
                    'over': {},
                }
        # print(option)
        return option

    @property
    def entities(self):
        return self.entry

    @property
    def reactions(self):
        return self.relation

    @property
    def genes(self):
        return [x for x in self.entry if x.type == "gene"]

    def get_element_by_class(self, class_):
        '''
        Get node by its class, like entry, relation, components
        :param class_: class
        :return: a list of node object.
        '''
        return [x for x in self.flatten() if x.class_ == class_]

    def get_element_by_name(self, name):
        return [x for x in self.flatten() if hasattr(x, "name") and x.name == name]

    def get_element_by_id(self, id):
        return [x for x in self.flatten() if hasattr(x, "id") and x.id == str(id)]

    def get_element_by_type(self, type):
        return [x for x in self.flatten() if hasattr(x, "type") and x.type == type]

    def _prepare_addition_info(self, candidate):
        '''
        Do not call this function, this is internal usage.
        :param queue: add the needed info requester to the queue
        :return:
        '''
        for i, x in enumerate(self.entry):
            if not x.link is None:
                candidate.append([x.link.replace("http://www.kegg.jp/dbget-bin/www_bget?",
                                                 "http://rest.kegg.jp/get/"), x])

    def get_element_by_label(self, label):
        # return [x for x in self.flatten() if hasattr(x, "display_name") and x.display_name == label]
        result = []
        for x in self.flatten():
            if hasattr(x, "display_name") and x.display_name == label:
                result.append(x)
        return result

    def __getattr__(self, item):
        if item in ["__str__"]:
            raise AttributeError
        if item in ["children", "root", "is_root", "father", "__str__",
                    "display_name", "id", "display_name", "name", "id", "type", "entry"]:
            return None
        l = self.get_element_by_label(item)
        if l:
            return l
        i = self.get_element_by_id(item)
        if i:
            return i
        else:
            return None

    def __cmp__(self, other):
        if id(self) == id(other):
            return True
        else:
            return -1

    def __eq__(self, other):
        return id(self) == id(other)

    def set_label(self, id2name):
        if not type(id2name) == dict:
            raise Exception("set_display_name receive a dictionary")
        for x in id2name:
            tr = self.get_element_by_id(str(x))
            if tr:
                tr[0].add_name = id2name[x]

    def set_color(self, id2color):
        if not type(id2color) == dict:
            raise Exception("set_display_name receive a dictionary")
        for x in id2color:
            tr = self.get_element_by_id(str(x))
            if tr:
                if isinstance(tr[0], Entry):
                    tr[0].color = id2color[x]
            nm = self.get_element_by_label(str(x))
            for n in nm:
                n.color = id2color[x]

    def set_scale(self, id2scale):
        if not type(id2scale) == dict:
            raise Exception("set_display_name receive a dictionary")
        for x in id2scale:
            tr = self.get_element_by_id(str(x))
            if tr:
                if isinstance(tr[0], Entry):
                    tr[0].scale = id2scale[x]
            nm = self.get_element_by_label(str(x))
            for n in nm:
                n.color = id2scale[x]

    def set_opacity(self, id2opacity):
        if not type(id2opacity) == dict:
            raise Exception("set_display_name receive a dictionary")
        for x in id2opacity:
            tr = self.get_element_by_id(str(x))
            if tr:
                if isinstance(tr[0], Entry):
                    tr[0].opacity = id2opacity[x]
            nm = self.get_element_by_label(str(x))
            for n in nm:
                n.opacity = id2opacity[x]

    def set_bg_color(self, id2bg):
        if not type(id2bg) == dict:
            raise Exception("set_display_name receive a dictionary")
        for x in id2bg:
            tr = self.get_element_by_id(str(x))
            if tr:
                if isinstance(tr[0], Entry):
                    tr[0].bg_color = id2bg[x]
            nm = self.get_element_by_label(str(x))
            for n in nm:
                n.bg_color = id2bg[x]


class Entry(KEGGNode):
    def __init__(self, id, name, type, link, reaction):
        self.id, self.name, self.type, self.link, self.reaction = id, name, type, link, reaction
        self.kegg_id = None
        self.component, self.graphic = [], []
        # self.back_color = (random.random(), random.random(), random.random())
        KEGGNode.__init__(self, "entry", {"component": self.component, "graphics": self.graphic})
        self.info = None
        self.ko_id = []
        self.add_name = None
        self.color = "black"
        self.opacity = 1
        self.bg_color = "white"
        self.scale = 1

    def visualize_able(self):
        return True

    def omic_data(self):
        if self.kegg_id in self.root.omic:
            return self.root.omic[self.kegg_id]
        else:
            print("Not Found")
            return -1

    @property
    def display_name(self):
        if self.add_name:
            return self.add_name
        g = self.graphic[0]
        if not g:
            return None
        if not g.name:
            return None
        names = g.name.replace(".", "").split(",")
        name = ""
        for x in names:
            if len(x) < 7:
                name = x.replace(" ", "")
                break
        if name == "":
            name = names[0]
        return name

    @property
    def data(self):
        '''
        Generate the graph information, for cytoscape.js drawing
        :return: a tuple(id, dict)
        '''
        g = self.graphic[0]
        if g.type != "rectangle":
            return
        if not g.name:
            return None
        names = g.name.replace(".", "").split(",")
        name = ""
        for x in names:
            if len(x) < 7:
                name = x.replace(" ", "")
                break
        if name == "":
            name = names[0]
        if self.add_name:
            name = self.add_name
        graphic = {
            "data": {"id": self.id, "name": name, "parent": "back"},
            "css":
                {
                    "shape": "rectangle",
                    "width": g.width,
                    "height": g.height,
                    "opacity": 1,
                    "background-color": "#ffffff",
                    "text-halign": "center",
                    "text-valign": "center",
                    "font-size": 10,
                    "border-style": "solid",
                    "border-width": "1px",
                },
            "position": {
                "x": g.x,
                "y": g.y
            },
            "locked": "true",
            "group": "nodes",
        }
        # print name, g.x, g.y
        return self.id, {"nodes": graphic}

    @property
    def root(self):
        o = self.father
        while not o.class_ == "pathway":
            o = o.father
        return o

    # def fill_info(self):
    #     kd = KEGGAdditionData(self.link, self)
    #     kd.start()
    #     print("start to fill {}".format(self.name))


class Component(KEGGNode):
    def __init__(self, id):
        self.id = id
        KEGGNode.__init__(self, "component", {})


class Graphics(KEGGNode):
    def __init__(self, name, x, y, coords, type, width, height, fgcolor):
        self.name, self.x, self.y, self.coords = name, float(x) if x is not None else None,\
                                                 float(y) if y is not None else None, coords
        self.type, self.width, self.height, self.fgcolor = type, float(width) if width is not None else None,\
                                                           float(height) if height is not None else None, fgcolor
        KEGGNode.__init__(self, "graphics", {})


class Reaction(KEGGNode):
    def __init__(self, id, name, type):
        self.id, self.name, self.type = id, name, type
        self.substrate, self.product = [], []
        KEGGNode.__init__(self, "reaction", {"substrate": self.substrate, "product": self.product})


class Substrate(KEGGNode):
    def __init__(self, id, name):
        self.id, self.name = id, name
        self.alt = []
        KEGGNode.__init__(self, "substrate", {"alt": self.alt})


class Product(KEGGNode):
    def __init__(self, id, name):
        self.id, self.name = id, name
        self.alt = []
        KEGGNode.__init__(self, "product", {"alt": self.alt})


class Alt(KEGGNode):
    def __init__(self, name):
        self.name = name
        KEGGNode.__init__(self, "alt", {})


class Relation(KEGGNode):
    def __init__(self, entry1, entry2, type):
        self.entry1, self.entry2, self.type = entry1, entry2, type
        self.subtype = []
        KEGGNode.__init__(self, "relation", {"subtype": self.subtype})


class Subtype(KEGGNode):
    def __init__(self, name, value):
        self.name, self.value = name, value
        KEGGNode.__init__(self, "subtype", {})
