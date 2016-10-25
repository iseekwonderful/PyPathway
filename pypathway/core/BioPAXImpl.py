# We use paxtools' api to convert BioPAX to sbgn and perform auto layout algorithm
import platform
from xml.sax import parseString, ContentHandler


class OperatingSystem:
    '''
    This Class Define the enum value of Operate System.
    '''
    WINDOWS = 1
    MAXOS = 2
    LINUX = 3
    OTHER = 4


class BioPAXParser:
    # @staticmethod
    # def parse(data):
    #     pass

    @staticmethod
    def parseFromFile(file):
        '''
        Parse a BioPAX file from local file system, a path is required

        :param file: The Path to the BioPAX file/
        :return: A pathway object with SBGN layout.
        '''
        os = BioPAXParser.os_specfic()
        if os == OperatingSystem.MAXOS:
            try:
                fp = open(file, "r")
            except:
                raise Exception("File not exist")
            import subprocess
            import os
            dir_path = os.path.dirname(os.path.realpath(__file__))
            path_to_paxtools = os.path.normpath(
                dir_path +
                "/../static/assets/paxtools-4.3.1.jar"
            )
            # cmd = "java -jar {} toSbgn {} out.sbgn".format(
            #     path_to_paxtools, file
            # )
            cmd = ["java", "-jar", path_to_paxtools, "toSbgn", file, "out.sbgn"]
            # if not subprocess.call(cmd, shell=True) == 0:
            FNULL = open(os.devnull, 'w')
            if not subprocess.call(cmd, stdout=FNULL) == 0:
                try:
                    subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    raise Exception(e.output)
                else:
                    raise Exception("paxtools convert exception")
            with open("out.sbgn") as fp:
                from .SBGNImpl import SBGNParser
                sb = SBGNParser.parse(fp.read())
            subprocess.call("rm out.sbgn", shell=True)
            sb.fix()
            return sb
        elif os == OperatingSystem.LINUX or os == OperatingSystem.OTHER:
            print("Not Implemented yet")
        elif os == OperatingSystem.WINDOWS:
            # sh is not available in windows, use subprocess
            try:
                fp = open(file, "r")
            except:
                raise Exception("File not exist")
            import subprocess
            import os
            dir_path = os.path.dirname(os.path.realpath(__file__))
            path_to_paxtools = os.path.normpath(
                dir_path +
                "/../static/assets/paxtools-4.3.1.jar"
            )
            # cmd = "java -jar {} toSbgn {} out.sbgn".format(
            #     path_to_paxtools, file
            # )
            cmd = ["java", "-jar", path_to_paxtools, "toSbgn", file, "out.sbgn"]
            FNULL = open(os.devnull, 'w')
            try:
                if not subprocess.call(cmd, stdout=FNULL) == 0:
                    try:
                        subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
                    except subprocess.CalledProcessError as e:
                        raise Exception(e.output)
                    else:
                        raise Exception("paxtools convert exception")
            except:
                raise
            with open("out.sbgn") as fp:
                from .SBGNImpl import SBGNParser
                sb = SBGNParser.parse(fp.read())
            subprocess.call("del out.sbgn", shell=True)
            sb.fix()
            return sb
        elif os == OperatingSystem.LINUX or os == OperatingSystem.OTHER:
            print("Not Implemented yet")

    @staticmethod
    def os_specfic():
        '''
        Inspect which system user is using, DO NOT CALL this method

        :return: operate system enum.
        '''
        os = platform.platform()
        if "Darwin" in os:
            return OperatingSystem.MAXOS
        elif "Windows" in os:
            return OperatingSystem.WINDOWS
        elif "Linux" in os:
            return OperatingSystem.LINUX
        else:
            return OperatingSystem.OTHER


class Heap(list):
    def __init__(self):
        list.__init__([])

    def push(self, element):
        self.insert(0, element)

    def peak(self):
        return self[0]


class Node:
    def __init__(self, class_, props, value):
        self.class_ = class_
        self.props = props
        self.value = value
        self.children = []
        self.father = None

    def find_by_id(self, id):
        if "rdf:ID" in self.props and self.props.get("rdf:ID") == "{}".format(id):
            return self
        for x in self.children:
            re = x.find_by_id(id)
            if re:
                return re

    def find_by_DB_ID(self, db_id):
        '''
        This is special design for reactome!

        :param db_id:
        :return:
        '''
        if self.value == "Reactome DB_ID: {}".format(db_id):
            return self
        for x in self.children:
            re = x.find_by_DB_ID(db_id)
            if re:
                return re

    def find_child(self, class_):
        return [x for x in self.children if x.class_ == "bp:{}".format(class_)]

    def summary(self, depth=0):
        result = "\t" * depth + "class: {}, props: {}, value: {}".format(
            self.class_,
            ", ".join(["{}: {}".format(k, v) for k, v in self.props.items()]),
            self.value) + "\n"
        for x in self.children:
            result += x.summary(depth + 1)
        return result


class BioPAXNativeHandler(ContentHandler):
    '''
    A Native BioPAX Handler, developing.
    '''
    def __init__(self):
        ContentHandler.__init__(self)
        self.gap = 0
        self.root = None
        self.heap = Heap()
        self.current_content = ""

    def startElement(self, name, attrs):
        # print "\t" * self.gap + "{}: {}".format(name, ",".join(["{}:{}".format(k, v) for k, v in attrs.items()]))
        if name == "rdf:RDF":
            self.root = Node(name, dict(attrs), None)
            self.heap.push(self.root)
        father = self.heap.peak()
        child = Node(name, dict(attrs), None)
        child.father = father
        father.children.append(child)
        self.heap.push(child)
        self.gap += 1

    def endElement(self, name):
        self.gap -= 1
        self.heap.pop(0)

    def characters(self, content):
        # print "\t" * self.gap + "value: {}".format(content.encode("utf8"))
        if content.strip():
            self.heap.peak().value = content.strip()
        pass


class NativeBioPAXParser:
    @staticmethod
    def parse(content):
        handler = BioPAXNativeHandler()
        parseString(content, handler)
        return handler.root
