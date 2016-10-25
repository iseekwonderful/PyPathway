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

    def generate(self):
        convert = {
            "Rectangle": "rectangle",
            "RoundedRectangle": "roundrectangle",
            "Oval": "ellipse",
            "Triangle": "triangle"
        }
        if self.type == "Rectangle" or self.type == "RoundedRectangle" or self.type == "Oval" or self.type == "Triangle":
            return [{
                "nodes": {
                    "data": {
                        "id": self.x.props["GraphId"],
                    },
                    "position": {
                        "x": int(float(self.g.props["CenterX"])),
                        "y": int(float(self.g.props["CenterY"])),
                    },
                    "group": "nodes",
                },
                "style": {
                    "selector": "#{}".format(self.x.props["GraphId"]),
                    "style": {
                        "shape": convert[self.g.props.get("ShapeType")],
                        "width": int(float(self.g.props["Width"])),
                        "height": int(float(self.g.props["Height"])),
                        "label": self.x.props.get("TextLabel") or "",
                        # the align of a label:
                        "text-halign": "center",
                        "text-valign": "center",
                        "text-max-width": int(float(self.g.props["Width"])),
                        "text-wrap": "wrap",
                        "background-color": "#{}".format(self.g.props.get("FillColor") or "fff"),
                        "border-width": "1px",
                        # "border-style": "dotted",
                        "border-color": "#000",
                        "opacity": 0.3 if int(float(self.g.props["Width"])) > 500 or int(float(self.g.props["Height"])) > 500 else 1,
                        "z-index": self.g.props["ZOrder"]
                    }
                }
            }]
        elif self.type == "Arc":
            # this means a pi degree circle.
            return None


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

    # the method general Pathway should provide
    # the convert the gpml to cytoscape.js's config, new we use pvjs.
    def config(self, setting=None):
        if not self.is_root:
            Warning("you are not root")
            return
        result = []
        dataNodes = []
        shapes = []
        # before handle edge, shape must be handled well
        for x in self.find_by_class("Shape"):
            g = x.get_child("Graphics")
            shapes.append(g)
            # print x
            # print g
            s = Shape(g.props["ShapeType"], x, g)
            if s.generate():
                for sg in s.generate():
                    result.append(sg)
        # Handle DataNode first:
        for x in [x.get_child("Graphics") for x in self.find_by_class("DataNode")]:
            # print x
            # print x.father
            parent = None
            parent = None
            for s in shapes:
                if contain([int(float(s.props["CenterX"])),
                            int(float(s.props["CenterY"])),
                            int(float(s.props["Width"])),
                            int(float(s.props["Height"]))], s.props["ZOrder"],
                           [int(float(x.props["CenterX"])), int(float(x.props["CenterY"]))],
                           x.props["ZOrder"]):
                    parent = s
            dataNodes.append(x)
            setting = {
                "nodes": {
                    "data": {
                        "id": x.father.props["GraphId"]
                    },
                    "position": {
                        "x": int(float(x.props["CenterX"])),
                        "y": int(float(x.props["CenterY"])),
                    },
                    "group": "nodes"
                },
                "style": {
                    "selector": "#{}".format(x.father.props["GraphId"]),
                    "style": {
                        "shape": "rectangle",
                        "width": int(float(x.props["Width"])),
                        "height": int(float(x.props["Height"])),
                        "label": x.father.props["TextLabel"],
                        # the align of a label:
                        "text-halign": "center",
                        "text-valign": "center",
                        "background-color": "#fff",
                        "border-width": "1px",
                        # "border-style": "dotted",
                        "border-color": "#000",
                        "font-size": int(float(x.props["FontSize"])),
                        "z-index": 100000 - int(x.props.get("ZOrder"))
                    },
                }
            }
            # if parent:
            #     setting["nodes"]["data"]["parent"] = parent.father.props.get("GraphId")
            result.append(setting)
        # Next is Label:
        for x in self.find_by_class("Label"):
            g = x.get_child("Graphics")
            parent = None
            for s in shapes:
                if contain([int(float(s.props["CenterX"])),
                            int(float(s.props["CenterY"])),
                            int(float(s.props["Width"])),
                            int(float(s.props["Height"]))], s.props["ZOrder"],
                           [int(float(g.props["CenterX"])), int(float(g.props["CenterY"]))],
                           g.props["ZOrder"]):
                    parent = s
            setting = {
                "nodes": {
                        "data": {
                            "id": x.props["GraphId"],
                        },
                        "position": {
                            "x": int(float(g.props["CenterX"])),# - int(float(g.props["Width"])) / 2,
                            "y": int(float(g.props["CenterY"])),# - int(float(g.props["Height"])) / 2
                        },
                        "group": "nodes",
                    },
                "style": {
                    "selector": "#{}".format(x.props["GraphId"]),
                    "style": {
                        "shape": "rectangle",
                        "width": int(float(g.props["Width"])),
                        "height": int(float(g.props["Height"])),
                        "label": x.props["TextLabel"],
                        # the align of a label:
                        "text-halign": "center",
                        "text-valign": "center",
                        "background-opacity": 0,
                        "text-max-width": int(float(g.props["Width"])),
                        "text-wrap": "wrap",
                        "color": "#f00",
                        "font-size": int(float(g.props["FontSize"])),
                        "z-index": 100000 - int(g.props.get("ZOrder"))
                    }
                }
            }
            # if parent:
            #     setting["nodes"]["data"]["parent"] = parent.father.props.get("GraphId")
            result.append(setting)
        # Next handle State, this should find the ref
        for x in self.find_by_class("State"):
            g = x.get_child("Graphics")
            rg = None
            for dn in dataNodes:
                if dn.father.props["GraphId"] == x.props["GraphRef"]:
                    rg = dn
            if not rg:
                raise GPMLCorrespondeNodeNotFound("cant find the related node to a state")
            result.append({
                "nodes": {
                    "data": {
                        "id": x.props["GraphId"],
                    },
                    "position": {
                        "x": int(float(g.props["RelX"])) + int(int(float(rg.props["Width"])) / 2) + int(float(rg.props["CenterX"])),
                        "y": int(float(g.props["RelY"])) + int(int(float(rg.props["Height"])) / 2) + int(float(rg.props["CenterY"]))
                    },
                    "group": "nodes",
                },
                "style": {
                    "selector": "#{}".format(x.props["GraphId"]),
                    "style": {
                        "shape": "ellipse",
                        "width": int(float(g.props["Width"])),
                        "height": int(float(g.props["Height"])),
                        "label": x.props["TextLabel"],
                        # the align of a label:
                        "text-halign": "center",
                        "text-valign": "center",
                        "text-max-width": int(float(g.props["Width"])),
                        "text-wrap": "wrap",
                        "background-color": "#{}".format(g.props.get("FillColor") or "fff"),
                        "font-size": int(float(rg.props["FontSize"])),
                        "border-width": "1px",
                        # "border-style": "dotted",
                        "border-color": "#000",
                        "z-index": 100000 - int(rg.props.get("ZOrder"))
                    }
                }
            })
        # Now add the edge:
        count = 0
        # For edge, we have to create some of Invisible temp node
        for x in self.find_by_class("Point"):
            # print x.father
            if not x.props.get("GraphRef") or True:
                parent = None
                for s in shapes:
                    if contain([int(float(s.props["CenterX"])),
                                int(float(s.props["CenterY"])),
                                int(float(s.props["Width"])),
                                int(float(s.props["Height"]))], s.props["ZOrder"],
                               [int(float(x.props["X"])), int(float(x.props["Y"]))],
                               x.father.props["ZOrder"]):
                        parent = s
                # print "parent is {}".format(parent)
                # we need to create temp node for them
                node_id = "t{}{}".format(int(float(x.props["X"])), int(float(x.props["Y"])))
                x.props["GraphRef"] = node_id
                settings = {
                    "nodes": {
                        "data": {
                            "id": node_id,
                        },
                        "position": {
                            "x": int(float(x.props["X"])),
                            "y": int(float(x.props["Y"])),
                        "group": "nodes",
                        }
                    },
                    "style": {
                        "selector": "#{}".format(node_id),
                        "style": {
                            "shape": "ellipse",
                            "width": 2,
                            "height": 2,
                            "background-color": "#{}".format("f00"),
                            "z-index": 100000 - int(x.father.props.get("ZOrder"))
                        }
                    }
                }
                # if parent:
                #     settings["nodes"]["data"]["parent"] = parent.father.props["GraphId"]
                result.append(settings)
        for x in self.find_by_class("Interaction"):
            g = x.get_child("Graphics")
            p1, p2 = g.find_by_class("Point")[0], g.find_by_class("Point")[1]
            # draw the arraw
            if not g.props.get("LineStyle"):
                linestyle = "solid"
            elif g.props.get("LineStyle"):
                linestyle = "dashed"
            result.append({
                "nodes": {
                    "data": {
                        "id": "{}-{}".format(p1.props["GraphRef"], p2.props["GraphRef"]),
                        "source": p1.props["GraphRef"],
                        "target": p2.props["GraphRef"]
                    },
                    "group": "edges",
                },
                "style": {
                    "selector": "#{}".format("{}-{}".format(p1.props["GraphRef"], p2.props["GraphRef"])),
                    "style": {
                        "line-color": "#{}".format(g.props.get("Color") or "000"),
                        "line-width": g.props.get("LineThickness"),
                        "line-style": linestyle,
                        'target-arrow-color': "#{}".format(g.props.get("Color") or "000"),
                        'target-arrow-shape': 'triangle',
                        'target-arrow-fill': "filled",
                        'curve-style': 'bezier',
                        'arrow-size': 2,
                        "z-index": 100000 - int(g.props.get("ZOrder"))
                    }
                }
            })
            count += 1
        return result

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
        if not self.option:
            self.option = []
        with open(os.getcwd() + "/assets/GPML/gpml_data/config_{}.json".format(area_id), "w") as fp:
            fp.write(json.dumps({"option": self.option.json if isinstance(self.option, IntegrationOptions) else self.option}))
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

    def get_element_by_name(self, name):
        '''
        Get the element who match certain name (aka. TextLabel)

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
