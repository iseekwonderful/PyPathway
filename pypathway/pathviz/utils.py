# Common Objects
# We define the Visualize Attribute, Interactive Event, Interactive Option and Visualization Option here
from threading import Thread
import time
import os
import imghdr
import struct
import json


def environment():
    '''
    To identify the current environment, a IPython notebook environment or a command-line environment
    We highly recommend you use a IPython notebook with the package
    :return:
    '''
    try:
        env = __IPYTHON__
        return 1
    except NameError:
        return 0


class IDNotFoundInPathwayTree(Exception):
    def __init__(self):
        pass


class PathwayDataInstanceContainNoValidDataException(Exception):
    def __init__(self):
        pass


class FormatNotFoundINPathwayDataInstanceException(Exception):
    def __init__(self):
        pass


class PaxtoolExecuteException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class GPMLCorrespondeNodeNotFound(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class OptionProcessException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class SBGNParseException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


# Reraise of the exceptions

import sys

PY3 = sys.version_info[0] == 3
if PY3:
    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        else:
            raise value
else:
    exec('''def reraise(tp, value, tb=None):
           raise tp, value, tb
    ''')


if PY3:
    from http.server import SimpleHTTPRequestHandler


    class CustomHTTPHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            return
else:
    from SimpleHTTPServer import SimpleHTTPRequestHandler


    class CustomHTTPHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            return


exist_server = None


def get_local_http_server(path):
    global exist_server
    if not exist_server:
        sv = LocalHTTPServer(path)
        sv.start()
        exist_server = sv
    return exist_server


class LocalHTTPServer(Thread):
    def __init__(self, path):
        Thread.__init__(self)
        self.path = path
        self.port = LocalHTTPServer.get_open_port()
        self.daemon = True

    def run(self):
        if sys.version[0] == "3":
            # print("start http server @ {}".format(self.path))
            import socketserver
            os.chdir(self.path)
            httpd = socketserver.TCPServer(("", self.port), CustomHTTPHandler)
            httpd.serve_forever()
        else:
            import SocketServer
            # print("start http server @ {}".format(self.path))
            os.chdir(self.path)
            httpd = SocketServer.TCPServer(("", self.port), CustomHTTPHandler)
            httpd.serve_forever()

    @staticmethod
    def get_open_port():
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port


def get_image_size(fname):
    '''
    Determine the image type of fhandle and return its size.
    from draco
    source of this function:
    http://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib
    best regard to author: Fred the Fantastic
    '''
    with open(fname, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        if imghdr.what(fname) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(fname) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(fname) == 'jpeg':
            try:
                fhandle.seek(0) # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception: #IGNORE:W0703
                return
        else:
            return
        return width, height


def plot(chart):
    area_id = str(time.time()).replace(".", "")
    # make proper dir
    if not os.path.exists(os.getcwd() + "/assets"):
        os.makedirs(os.getcwd() + "/assets")
    if not os.path.exists(os.getcwd() + "/assets/plot/"):
        os.makedirs(os.getcwd() + "/assets/plot/")
    # load the template
    with open(os.path.dirname(os.path.abspath(__file__)) + "/static/box.html") as fp:
        iframe = fp.read()
    with open(os.path.dirname(os.path.abspath(__file__)) + "/static/assets/chart/plot.j2") as fp:
        info = fp.read()
    with open(os.getcwd() + "/assets/plot/plot_{}.html".format(area_id), "w") as fp:
        fp.write(info.replace("{{ opt }}", json.dumps(chart.json)))
    html = iframe.replace("{{path}}", "'assets/plot/plot_{}.html'".format(area_id))\
        .replace("{{ratio}}", "0.6").replace("{{time}}", area_id)
    if environment():
        from IPython.display import HTML
        # print(html)
        return HTML(html)


class C:
    def __init__(self, jsons):
        self.json = jsons


def plot_json(json_config):
    return plot(C(json_config))
