from xml.sax import *
from .general import Pathway, vertex2id
from ..query.common import PathwayFormat
from xml.dom.minidom import Document
from ..utils import environment as env
from ..utils import SBGNParseException
from .BioPAXImpl import NativeBioPAXParser
import os
import shutil
import json
import re
import sys
import time


def id_handle(id):
    '''
    In SBGNviz.js if the id contain some spacial characters, will lead to a select failure, so, we replace the
    illegal char in the id

    :param id:
    :return: filtered id
    '''
    if id:
        return "".join([x for x in re.findall(r"[\d\w]{1}", id)]).replace("_", "")
    else:
        return None


# First define the errors:
class TypeNotInNestedElementListError(Exception):
    def __init__(self, input_type, exist_types):
        self.input_type = input_type
        self.exist_types = exist_types


# Bbox not found while visualization
class BboxNotFoundInGlyphException(Exception):
    def __init__(self):
        pass


class ObjectCaller:
    def __init__(self):
        self.dicts = {"notes": [Notes, ["notes"]], "extension": [Extension, ["extension"]],
                      "point": [Point, ["x", "y"]], "bbox": [BBox, ["x", "y", "h", "w"]],
                      "sbgn": [SBGNRoot, ["version"]], "map": [Map, ["language"]],
                      "arc": [Arc, ["class", "id", "source", "target"]], "arcgroup": [ArcGroup, ["class"]],
                      "glyph": [Glyph, ["class", "compartmentOrder", "compartmentRef", "id", "orientation"]],
                      "label": [Label, ["text"]], "state": [State, ["value", "variable"]], "clone": [Clone, ["label"]],
                      "callout": [CallOut, ["target"]],
                      "port": [Port, ["id", "x", "y"]], "start": [Start, ["x", "y"]],
                      "next": [Next, ["x", "y"]], "end": [End, ["x", "y"]]}

    def call(self, name, attrs):
        if name not in self.dicts:
            raise TypeNotInNestedElementListError(name, self.dicts.keys())
        args = [attrs.get(x) for x in self.dicts[name][1]]
        return self.dicts[name][0](*args)


class Heap(list):
    def __init__(self):
        list.__init__([])

    def push(self, element):
        self.insert(0, element)

    def peak(self):
        return self[0]


# A parser for SBGN-PD
class SBGNParser:
    @staticmethod
    def parse(stream, BioPAX=None):
        handler = SBGNHandler()
        parseString(stream, handler)
        if BioPAX:
            handler.root.BioPAX = BioPAX
        return handler.root

    @staticmethod
    def parseFromFile(file, BioPAX=None):
        try:
            if sys.version[0] == "2":
                with open(file) as fp:
                    if BioPAX:
                        with open(BioPAX) as fp2:
                            return SBGNParser.parse(fp.read(), BioPAX=fp2.read())
                    else:
                        return SBGNParser.parse(fp.read(), BioPAX=None)
            else:
                with open(file, encoding="utf8") as fp:
                    if BioPAX:
                        with open(BioPAX, encoding="utf8") as fp2:
                            return SBGNParser.parse(fp.read(), BioPAX=fp2.read())
                    else:
                        return SBGNParser.parse(fp.read(), BioPAX=None)
        except IOError:
            raise SBGNParseException("Fail reading file")
        except Exception as e:
            import traceback
            # print(traceback.format_exc())


# basic class of all SBGN-PD Objects.
class SBGNObject(Pathway):
    def __init__(self, name, ref):
        Pathway.__init__(self)
        self.core_implement = PathwayFormat.SBGN
        self.name = name
        self.ref = ref
        if name == "sbgn":
            self.id = "root"

    def add_child(self, child):
        child.father = self
        if child.name not in self.ref:
            print("Me {}, Child: {} not in {}".format(self.name, child.name, ", ".join(self.ref.keys())))
            raise TypeNotInNestedElementListError(child.name, self.ref.keys())
        try:
            self.ref[child.name].append(child)
        except Exception as e:
            import traceback
            print(self)
            print(traceback.format_exc())
            print(self.name, self.ref)
            exit()

    def summary(self, deepth=0):
        refs = self.ref.values()
        result = []
        for x in refs:
            for y in x:
                result.append(y)
        if not result:
            return "...." * deepth + "class: {}, Props: {}\n".format(self.name, ", ".join(
                ["{}: {}".format(k, v) for k, v in self.__dict__.items()
                 if not k == "name"
                 and not isinstance(v, list)
                 and not isinstance(v, dict)
                 and not k == "father"
                 and not k == "BioPAX"]))
        else:
            result = "...." * deepth + "class: {}, props: {}\n".format(self.name, ", ".join(
                ["{}: {}".format(k, v) for k, v in self.__dict__.items()
                 if not k == "name" and not isinstance(v, list) and not isinstance(v, dict) and not k == "father"
                 and not k == "BioPAX"]))
            for x in refs:
                if x:
                    for y in x:
                        result += y.summary(deepth=deepth + 1)
            return result

    # These properties, is essential in a tree object.
    @property
    def children(self):
        result = []
        for x in self.ref.values():
            for y in x:
                result.append(y)
        return result

    @property
    def root(self):
        father = self.father
        while not isinstance(father, SBGNRoot):
            father = father.father
        return father

    @property
    def is_root(self):
        return isinstance(self, SBGNRoot)

    # this class should not be overwritten
    def export(self):
        raise Exception("You can only use export in a SBGN tree's root")

    def draw(self, setting=None):
        raise NotImplementedError

    # Do not call this method directly, please use root's export method
    def _xml_object(self, father, doc):
        # if hasattr(self, "id") and self.id == "reactionVertex10616398":
        #     print self.bbox
        me = doc.createElement(self.name)
        for k, v in self.__dict__.items():
            if k == "ref" or k == "father" or k == "root" or k == "children" or k == "core_implement" \
                    or k in self.ref.keys() or k == "external_id" or k == "raw_id":
                continue
            if not v and not type(v) == float:
                # if hasattr(self, "name") and self.name == "bbox":
                #     print k, type(v)
                continue
            if k == "type":
                k = "class"
            if sys.version[0] == "2":
                me.setAttribute(k, str(v))
            else:
                if k == "text":
                    me.setAttribute(k, str(v.decode()))
                else:
                    me.setAttribute(k, str(v))
        father.appendChild(me)
        children = self.children
        if self.name == "arc":
            def cmp_s(x, y):
                if x == "start":
                    return -1
                elif x == "next" and y == "end":
                    return -1
                else:
                    return 1
            if sys.version[0] == "2":
                children.sort(cmp=cmp_s, key=lambda x: x.name)
        new = []
        for x in self.children:
            if hasattr(x, "name") and x.name == "bbox":
                new.insert(0, x)
            else:
                new.append(x)
        for x in new:
            x._xml_object(me, doc)

    @property
    def visualize_able(self):
        return False

    @property
    def db_id(self):
        results = []
        if self.ref.get("label"):
            results.append(self.ref.get("label")[0].text)
        return results

    def __repr__(self):
        # return str({k: v for k, v in self.__dict__.items() if not k == "father"
        #             and not k == "children" and not k == "ref"})
        return "class: {}, id: {}, type: {}, external_id: {}".format(self.name,
                                                                     self.id if hasattr(self, "id") else None,
                                                                     self.type if hasattr(self, "type") else None,
                                                                     self.external_id if hasattr(self, "external_id")
                                                                     else None)

    def _flatten(self, list):
        if self.children:
            list.extend([x for x in self.children])
        for x in self.children:
            x._flatten(list)

    def flatten(self):
        result = []
        self._flatten(result)
        return result

    def _structure(self, nodes, edges, elements):
        try:
            for x in self.children:
                nodes.append([x.name, x.id if hasattr(x, "id") else None])
                elements.append({
                    "group": "nodes",
                    "data": {
                        "id": x.id
                    },
                    "css": {
                        "color": "red"
                    }
                })
                edges.append([x.id if hasattr(x, "id") else None, self.id if hasattr(self, "id") else None])
                elements.append({
                    "groups": "edges",
                    "data": {
                        "id": self.id + x.id,
                        "source": x.id,
                        "target": self.id
                    },
                    "css": {
                        "width": "3",
                        "color": "red"
                    }
                })
                x._structure(nodes, edges, elements)
        except:
            print(self)
            exit()

    def structure(self):
        no_id_er = set([x.name for x in self.flatten() if not hasattr(x, "id")])
        for x in no_id_er:
            cx = [t for t in self.flatten() if t.name == x]
            for i, n in enumerate(cx):
                n.id = x + str(i)
        nodes = []
        edges = []
        elements = []
        self._structure(nodes, edges, elements)
        with open("/Users/sheep/WebstormProjects/treeviz/data.json", "w") as fp:
            fp.write(json.dumps(elements))
        return nodes

    @property
    def entities(self):
        exist_entities = ["unspecified entity", "simple chemical", "macromolecule", "nucleic acid feature",
                          "perturing agent", "source sink", "complex"]
        result = []
        for x in self.flatten():
            for e in exist_entities:
                if hasattr(x, "type") and e in x.type:
                    result.append(x)
                    continue
        return result

    @property
    def reactions(self):
        exist_reaction = ["process", "omitted process", "uncertain process", "association", "phenotype", "dissociation"]
        result = []
        for x in self.flatten():
            for e in exist_reaction:
                if hasattr(x, "type") and e in x.type:
                    result.append(x)
                    continue
        return result

    @property
    def nodes(self):
        return self.entities

    @property
    def arcs(self):
        exist_arcs = ["consumption", "production", "modulation", "stimulation", "catalysis", "inhibition", "logic arc",
                      "equivalence arc"]
        result = []
        for x in self.flatten():
            for e in exist_arcs:
                if hasattr(x, "type") and e in x.type:
                    result.append(x)
                    continue
        return result

    @property
    def members(self):
        return self.flatten()

    @property
    def compartments(self):
        result = []
        for x in self.flatten():
            for e in ["compartment"]:
                if hasattr(x, "type") and e in x.type:
                    result.append(x)
                    continue
        return result

    # def get_element_by_class(self, _class):
    #     return [x for x in self.flatten() if hasattr(x, "name") and x.name == _class]
    #
    # def get_element_by_type(self, type):
    #     return [x for x in self.flatten() if hasattr(x, "type") and x.type == type]
    #
    # def get_element_by_text(self, name):
    #     result = []
    #     for x in self.flatten():
    #         for c in x.children:
    #             if c.name == "label" and c.props.get("text") == name:
    #                 if x not in result:
    #                     result.append(x)
    #     return result
    #
    # def get_element_by_id(self, id):
    #     return [x for x in self.flatten() if hasattr(x, "id") and x.id == id]
    #
    # def get_element_by_oid(self, oid):
    #     return [x for x in self.flatten() if hasattr(x, "external_id") and oid in x.external_id]


# note or notes?
class Notes(SBGNObject):
    def __init__(self, note):
        SBGNObject.__init__(self, "notes", {})
        self.note = note

    @property
    def visualize_able(self):
        return False


class Extension(SBGNObject):
    def __init__(self, extension):
        SBGNObject.__init__(self, "extension", {})
        self.extension = extension

    @property
    def visualize_able(self):
        return False


class Point(SBGNObject):
    def __init__(self, x, y):
        self.extension, self.notes, self.x, self.y = [], [], x, y
        SBGNObject.__init__(self, "point", {"notes": self.notes, "extension": self.extension})

    @property
    def visualize_able(self):
        return False


class BBox(SBGNObject):
    def __init__(self, x, y, h, w):
        self.notes, self.extension = [], []
        SBGNObject.__init__(self, "bbox", {"notes": self.notes, "extension": self.extension})
        self.x, self.y, self.h, self.w = float(x), float(y), float(h), float(w)

    @property
    def visualize_able(self):
        return False


# this is the root class of SBGN
# this class provide the function like a DOM tree
# get_node(entity)_by_id, get_arc_by_id
# defined exception: IDNotFoundINPathwayTree
# When you call SBGNParser.parse(stringbuffer) you get a instance of a pathway.
class SBGNRoot(SBGNObject):
    '''
    The root class of a SBGN-PD graph, the export and draw method are implement here.
    '''

    def __init__(self, version):
        self.father = None
        self.extension, self.notes, self.map, self.version = [], [], [], version
        SBGNObject.__init__(self, "sbgn", {"notes": self.notes, "extension": self.extension, "map": self.map})
        self.BioPAX = None

    @property
    def visualize_able(self):
        return False

    def draw(self, setting=None):
        '''
        Export the pathway, options and copy the static dir to the ipython's workdir, run it!
        :param setting: ignore it.
        :return: None
        '''
        area_id = str(time.time()).replace(".", "")
        with open(os.path.dirname(os.path.abspath(__file__)) + "/../static/box.html") as fp:
            con = fp.read()
        if self.option:
            content = self.option.json
        else:
            content = {}
        if not os.path.exists(os.getcwd() + "/assets/SBGN/"):
            shutil.copytree(os.path.dirname(os.path.abspath(__file__)) + "/../static/SBGN", os.getcwd() + "/assets/SBGN/")
        with open(os.getcwd() + "/assets/SBGN/sampleapp-components/data/config_{}.json".format(area_id), "w") as fp:
            fp.write(json.dumps(content))
        with open(os.getcwd() + "/assets/SBGN/sampleapp-components/data/pathway_{}.xml".format(area_id), "w") as fp:
            fp.write(self.export())
        con = con.replace("{{path}}", "'assets/SBGN/index_{}.html'".format(area_id))
        con = con.replace("{{ratio}}", "0.7").replace("{{time}}", area_id)
        with open(os.path.dirname(os.path.abspath(__file__)) + "/../static/SBGN/index.html") as fp:
            id_con = fp.read()
        with open(os.getcwd() + "/assets/SBGN/index_{}.html".format(area_id), "w") as fp:
            fp.write(id_con.replace("{{time}}", area_id))
        #js
        with open(os.path.dirname(os.path.abspath(__file__)) + "/../static/SBGN/sampleapp-components/js/interface.js") as fp:
            id_con = fp.read()
        with open(os.getcwd() + "/assets/SBGN/sampleapp-components/js/interface_{}.js".format(area_id), "w") as fp:
            fp.write(id_con.replace("{{time}}", area_id))
        if env():
            # here we are in IPython, import IPython assert here, copy static to target dir
            from IPython.display import HTML
            return HTML(con)
        else:
            import webbrowser
            from ..utils import get_local_http_server
            ls = get_local_http_server(os.getcwd())
            try:
                webbrowser.open_new("http://localhost:{}/assets/SBGN/index_{}.html".format(ls.port, area_id))
            except KeyboardInterrupt:
                exit()

    def export(self):
        # if format == PathwayFormat.KGML:
        #     Warning("[!] Convert from SBGN-PD to Other format is not supported")
        # elif format == PathwayFormat.SBGN:
        doc = Document()
        root = doc.createElement("sbgn")
        root.setAttribute("xmlns", "http://sbgn.org/libsbgn/pd/0.1")
        for x in self.children:
            x._xml_object(root, doc)
        doc.appendChild(root)
        con = doc.toprettyxml(indent="  ")
        return con

    @property
    def members(self):
        member = []
        for x in self.children:
            member.extend(x.flatten())
        return member

    @property
    def nodes(self):
        '''
        Get the list of visualize node id
        :return: list of id
        '''
        return [x for x in self.members if x.name == "glyph"]

    @property
    def entities(self):
        return self.nodes

    def get_element_by_class(self, class_):
        return [x for x in self.members if x.name == class_]

    def get_element_by_id(self, id):
        return [x for x in self.members if hasattr(x, "id") and x.id == id]

    def get_element_by_type(self, type):
        return [x for x in self.members if hasattr(x, "type") and x.type == type]

    def get_element_by_name(self, name):
        result = []
        for x in self.flatten():
            for c in x.children:
                if c.name == "label":
                    if c.text.decode("utf8") == name:
                        if x not in result:
                            result.append(x)
        return result

    def get_element_by_oid(self, oid):
        result = []
        for x in self.flatten():
            if hasattr(x, "external_id"):
                for d in x.external_id:
                    if oid in d.values():
                        result.append(x)
        return result

    def fix(self):
        '''
        Fix the error while converting to sbgn from BioPAX
        :return: None
        '''
        glyph = {x.id: (float(x.bbox[0].x) + float(x.bbox[0].w) / 2, float(x.bbox[0].y) + float(x.bbox[0].h) / 2.0)
                 for x in self.members if x.name == "glyph" and x.bbox}
        port = {x.id: (x.x, x.y, x.father.id) for x in self.members if x.name == "port"}
        for x in self.members:
            if x.name == "arc":
                if x.source in glyph:
                    x.start[0].x = glyph[x.source][0]
                    x.start[0].y = glyph[x.source][1]
                elif x.source in port:
                    x.start[0].x = port[x.source][0]
                    x.start[0].y = port[x.source][1]
                    x.source = port[x.source][2]
                else:
                    print("Wrong: {}".format(x.source))
                    # raise Exception("Where?")
                if x.target in glyph:
                    x.end[0].x = glyph[x.target][0]
                    x.end[0].y = glyph[x.target][1]
                elif x.target in port:
                    x.end[0].x = port[x.target][0]
                    x.end[0].y = port[x.target][1]
                    x.target = port[x.target][2]
                else:
                    print("Wrong target: {}".format(x.target))
                x.ref["glyph"] = []
        # fix the too large modification
        for x in self.members:
            if x.name == "glyph":
                x.port = []
        for x in self.members:
            if x.name == "state":
                if x.value == "phosres":
                    x.value = "P"
                    r = min(float(x.father.bbox[0].w), float(x.father.bbox[0].h))
                    x.father.bbox[0].w = r
                    x.father.bbox[0].h = r

    def fix_reactome(self, ratio=2.2):
        '''
        Special for reactome source pathway, need BioPAX data
        1. repair complex
        2. repair scale
        3. repair the external ID
        :param ratio:
        :return:
        '''
        # first delete the arcs, let us try nodes
        # self.children[0].ref["arc"] = []
        for x in self.members:
            if x.name == "port":
                # print x.father.bbox[0].x, x.father.bbox[0].y, x.x, x.y
                x.x = float(x.father.bbox[0].x) / ratio + float(x.x) - float(x.father.bbox[0].x)
                x.y = float(x.father.bbox[0].y) / ratio + float(x.y) - float(x.father.bbox[0].y)
        for x in self.members:
            if x.name == "glyph":
                if x.type == "compartment":
                    if x.bbox:
                        # print("w: {}, h: {}, x: {}, y: {}".format(x.bbox[0].w, x.bbox[0].h, x.bbox[0].x, x.bbox[0].y))
                        x.bbox[0].w = (float(x.bbox[0].w) + float(x.bbox[0].x)) / ratio - float(x.bbox[0].x) / ratio
                        x.bbox[0].h = (float(x.bbox[0].h) + float(x.bbox[0].y)) / ratio - float(x.bbox[0].y) / ratio
                        x.bbox[0].x = float(x.bbox[0].x) / ratio
                        x.bbox[0].y = float(x.bbox[0].y) / ratio
                        # print("w: {}, h: {}, x: {}, y: {}".format(x.bbox[0].w, x.bbox[0].h, x.bbox[0].x, x.bbox[0].y))
                else:
                    if x.bbox:
                        x.bbox[0].x = float(x.bbox[0].x) / ratio
                        x.bbox[0].y = float(x.bbox[0].y) / ratio
        # for x in self.members:
        #     if hasattr(x, "id") and x.id == "reactionVertex10616398":
        #         print x
        # filter compartments
        refs = []
        for x in self.members:
            if hasattr(x, "type") and x.type == "compartment":
                refs.append([x, [x.bbox[0].x, x.bbox[0].y, float(x.bbox[0].w) + float(x.bbox[0].x),
                                 float(x.bbox[0].h) + float(x.bbox[0].y)], []])
        for x in self.members:
            if x.name == "bbox" and hasattr(x.father, "type") and x.father.type != "compartment":
                bd = [(float(x.x), float(x.y)),
                      (float(x.x), float(x.h) + float(x.y)),
                      (float(x.w) + float(x.x), float(x.y)),
                      (float(x.w) + float(x.x), float(x.h) + float(x.y))]
                for r in refs:
                    for p in bd:
                        if self._check_point(p, r[1]):
                            state = True
                            r[2].append(True)

        need_delete = [r[0].id for r in refs if len(r[2]) == 0]
        # for x in refs:
        #     print x[0].id, len(x[2])
        temp = []
        for x in self.children[0].glyph:
            if x.id not in need_delete:
                temp.append(x)
        self.children[0].ref["glyph"] = temp
        # fix complex and id_ref
        # parse first:
        pax = NativeBioPAXParser.parse(self.BioPAX)
        # print "prepare to fix biopax"
        for x in self.members:
            if not hasattr(x, "id"):
                return
            if "compartment" in x.id:
                # ignore now
                cid = x.raw_id.split("_")[2]
            elif "entity" in x.id:
                eid = x.raw_id.split("_")[1]
                bioId = vertex2id(eid)
                if not bioId:
                    # print("None corID")
                    continue
                    raise SBGNParseException("No corID find")
                else:
                    try:
                        cor = pax.find_by_DB_ID(bioId).father
                    except:
                        # print(eid, bioId)
                        continue
                    for n in cor.find_child("xref"):
                        ref = pax.find_by_id(n.props["rdf:resource"].replace("#", ""))
                        x.external_id.append({ref.find_child("db")[0].value: ref.find_child("id")[0].value})
                    # print x.external_id
                    # step 2: fix the compartments's elements
                    # print cor.summary()
                    members = []
                    if cor.class_ == "bp:Complex":
                        self._complex_members(cor, members, pax)
                        fbbox = x.ref["bbox"][0]
                        # print members
                        # x.ref["glyph"] = []
                        for i, m in enumerate(members):
                            if m[1] == "1":
                                g = Glyph("macromolecule", None, None, x.id + m[0], None)
                            else:
                                g = Glyph("macromolecule multimer", None, None, x.id + m[0], None)
                            bbox = self.complex_layout(fbbox, i)
                            label = Label(m[0])
                            g.ref["bbox"].append(bbox)
                            g.ref["label"].append(label)
                            if m[2]:
                                for i, md in enumerate(m[2]):
                                    sg = Glyph("state variable", None, None, x.id + m[0] + md, None)
                                    sg.ref["bbox"].append(BBox(bbox.x - 11 + (i % 2) * bbox.w,
                                                               bbox.y - 11 + (i / 2) * bbox.h, 22, 22))
                                    if "phospho" in md:
                                        md = "P"
                                    sg.ref["state"].append(State(value=md, variable=None))
                                    g.ref["glyph"].append(sg)
                            x.ref["glyph"].append(g)
                            # print x.summary()

            elif "reaction" in x.id:
                # ignore now
                rid = x.raw_id.split("_")[1]
                bioId = vertex2id(rid)

    def complex_layout(self, bbox, i):
        x, y, w, h = 0, 0, 0, 0
        if i == 0:
            x, y, w, h = bbox.x, bbox.y, bbox.w - 10, bbox.h - 10
        elif i % 2 == 0:
            offset = i / 2
            x, y, w, h = bbox.x, bbox.y - bbox.h * offset, bbox.w - 10, bbox.h - 10
        elif i % 2 == 1:
            offset = (i + 1) / 2
            x, y, w, h = bbox.x, bbox.y + bbox.h * offset, bbox.w - 10, bbox.h - 10
        return BBox(x, y, h, w)

    def _complex_members(self, pax, result, root, s=None):
        # for x in pax.find_child("componentStoichiometry"):
        #     print root.find_by_id(x.props["rdf:resource"].replace("#", "")).summary()
        cs = pax.find_child("componentStoichiometry")
        cp = pax.find_child("component")
        if not len(cs) == len(cp):
            raise SBGNParseException("count of componentStoichiometry != count of component")
        info = []
        for x in range(len(cs)):
            info.append((cs[x], cp[x]))
        if pax.class_ == "bp:Complex":
            for s, p in info:
                # print x.props["rdf:resource"].replace("#", "")
                target = root.find_by_id(p.props["rdf:resource"].replace("#", ""))
                if target:
                    self._complex_members(target, result, root, s)
        else:
            # print pax.summary()
            display = pax.find_child("displayName")
            if display:
                # may be unstable
                mods = []
                count = 1
                for x in pax.find_child("feature"):
                    if root.find_by_id(x.props["rdf:resource"].replace("#", "")).class_ == "bp:ModificationFeature":
                        target = \
                        root.find_by_id(x.props["rdf:resource"].replace("#", "")).find_child("modificationType")[0]
                        modf = root.find_by_id(target.props["rdf:resource"].replace("#", ""))
                        if modf:
                            if modf.find_child("term"):
                                mods.append(modf.find_child("term")[0].value)
                if s:
                    if root.find_by_id(s.props["rdf:resource"].replace("#", "")):
                        if root.find_by_id(s.props["rdf:resource"].replace("#", "")).find_child(
                                "stoichiometricCoefficient"):
                            count = root.find_by_id(s.props["rdf:resource"].replace("#", "")).find_child(
                                "stoichiometricCoefficient")[0].value
                result.append([display[0].value, count, mods])

    def _check_point(self, p, bbox):
        if bbox[0] < p[0] < bbox[2] and bbox[1] < p[1] < bbox[3]:
            return True
        else:
            return False


class Map(SBGNObject):
    def __init__(self, language):
        self.arc, self.arcgroup, self.bbox, self.extension, self.glyph, self.notes = [], [], [], [], [], []
        SBGNObject.__init__(self, "map", {"arc": self.arc, "arcgroup": self.arcgroup, "bbox": self.bbox,
                                          "extension": self.extension, "glyph": self.glyph, "notes": self.notes})
        self.language = language

    @property
    def visualize_able(self):
        return False


# this is a PD implement so no port currently
class Arc(SBGNObject):
    def __init__(self, type, id, source, target):
        self.end, self.extension, self.glyph, self.next_element, self.notes, self.start = [], [], [], [], [], []
        SBGNObject.__init__(self, "arc", {"end": self.end, "extension": self.extension, "glyph": self.glyph,
                                          "next": self.next_element, "notes": self.notes, "start": self.start})

        self.type = type
        self.id = id_handle(id)
        self.source = id_handle(source)
        self.target = id_handle(target)

    @property
    def visualize_able(self):
        return True


class ArcGroup(SBGNObject):
    def __init__(self, type):
        self.arc, self.extension, self.glyph, self.note, type = [], [], [], [], type
        SBGNObject.__init__(self, "arcgroup", {"arc": self.arc, "extension": self.extension, "glyph": self.glyph,
                                               "note": self.note})

    # note that arcgroup itself cannot be visualized
    # but its child could
    @property
    def visualize_able(self):
        return False


# entity only used in AF, ignore
class Glyph(SBGNObject):
    def __init__(self, type, compartmentOrder, compartmentRef, id, orientation):
        self.notes, self.extension, self.label, self.state, self.clone, self.callout = [], [], [], [], [], []
        self.bbox, self.glyph, self.port, self.point = [], [], [], []
        SBGNObject.__init__(self, "glyph", {"notes": self.notes, "extension": self.extension, "label": self.label,
                                            "state": self.state, "clone": self.clone, "callout": self.callout,
                                            "bbox": self.bbox, "glyph": self.glyph, "port": self.port,
                                            "point": self.point})
        self.type, self.compartmentOrder = type, compartmentOrder
        self.compartmentRef, self.orientation = compartmentRef, orientation
        self.id = id_handle(id)
        self.raw_id = id
        self.external_id = []

    @property
    def visualize_able(self):
        return True


class Label(SBGNObject):
    def __init__(self, text):
        self.notes, self.extension, self.bbox = [], [], []
        SBGNObject.__init__(self, "label", {"notes": self.notes, "extension": self.extension, "bbox": self.bbox})
        self.text = text.encode("utf8")

    @property
    def visualize_able(self):
        return True


class State(SBGNObject):
    def __init__(self, value, variable):
        self.value = value
        self.variable = variable
        SBGNObject.__init__(self, "state", {})

    @property
    def visualize_able(self):
        return True


class Clone(SBGNObject):
    def __init__(self, label=None):
        self.label = label
        SBGNObject.__init__(self, "clone", {})

    @property
    def visualize_able(self):
        return True


class CallOut(SBGNObject):
    def __init__(self, target):
        self.point, self.target = [], target
        SBGNObject.__init__(self, "callout", {"point": self.point})

    # is it?
    @property
    def visualize_able(self):
        return False


class Port(SBGNObject):
    def __init__(self, id, x, y):
        self.notes, self.extension, self.x, self.y, self.id = [], [], x, y, id_handle(id)
        SBGNObject.__init__(self, "port", {"notes": self.notes, "extension": self.extension})

    @property
    def visualize_able(self):
        return False


class Start(SBGNObject):
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        SBGNObject.__init__(self, "start", {})

    @property
    def visualize_able(self):
        return False


class Next(SBGNObject):
    def __init__(self, x, y):
        self.x, self.y, self.point = float(x), float(y), []
        SBGNObject.__init__(self, "next", {"point": self.point})

    @property
    def visualize_able(self):
        return False


class End(SBGNObject):
    def __init__(self, x, y):
        self.x, self.y, self.point = float(x), float(y), []
        SBGNObject.__init__(self, "end", {"point": self.point})

    @property
    def visualize_able(self):
        return False


# A Handler class
class SBGNHandler(ContentHandler):
    def __init__(self):
        ContentHandler.__init__(self)
        self.root = SBGNRoot("")
        self.heap = Heap()
        self.caller = ObjectCaller()

    def startElement(self, name, attrs):
        if name == "sbgn":
            self.root.name = "sbgn"
            self.root.attrs = attrs
            self.heap.push(self.root)
            return
        if "sbgn" in name:
            name = name.replace("sbgn:", "")
        super_name = self.heap.peak()
        current = self.caller.call(name, attrs)
        super_name.add_child(current)
        self.heap.push(current)

    def endElement(self, name):
        if not name == "sbgn" and "sbgn" in name:
            name = name.replace("sbgn:", "")
        if self.heap.peak().name != name:
            print("should be: {} and is {}".format(name, self.heap.peak().name))
            raise AttributeError
        self.heap.pop(0)
