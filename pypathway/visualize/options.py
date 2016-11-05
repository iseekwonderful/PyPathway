from ..utils import OptionProcessException


class IntegrationOptions:
    '''
    Warning: this class now is integrate in each pathway class, DO NOT using this yourself.
        IntegrationOption is a class that tell the module the appearance of the pathway graphic.
    We can abstract the procedure: when the module wanna to know the default setting and interactive response,
    they call the instance of IntegrationOptions hold by pathway object, ask for the visualize option of certain
    node by the unique ID.
        The total design of this class is to build a relation of object ID and the visualize option, include the
    function set(2). and provide a query interface: get(1) for module and advance usage

    Attributes:
        id_option: a dictionary contain the id and visualize options
        handle: a function eat a id and return a visualize option
    '''
    def __init__(self):
        # A dictionary contain the id and visualize options
        self.id_option = {}
        # A function eat a id and return a visualize option
        self.handle = lambda x: None

    def set(self, id_list, visualize_option_list):
        '''
        set the options for certain ids
        :param id_list: a list of id, should be string
        :param visualize_option_list: a list of instance of visualize option
        :return: None
        '''
        if len(id_list) != len(visualize_option_list):
            raise OptionProcessException("Length of id_list != length of visualize_option_list")
        for x in range(len(id_list)):
            if not isinstance(visualize_option_list[x], VisualizationOption):
                raise OptionProcessException("This member of list visualize_option_list should be the instance of VisualizeOption!")
            self.id_option[id_list[x]] = visualize_option_list[x]

    @property
    def json(self):
        return {k: v.json for k, v in self.id_option.items()}


class NodeProps:
    COLOR = "color"
    BG_COLOR = "background-color"
    OPACITY = "opacity"
    SCALE = "scale"

NP = NodeProps


def rgb(r, g, b):
    '''
    rbg to web color

    :param r: red, 0~255
    :param g: green, 0~255
    :param b: blue, 0~255
    :return:
    '''
    try:
        rf = int(r)
        gf = int(g)
        bf = int(b)
    except:
        raise Exception("Cant convert color value to float!")
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


class VisualizationOption:
    def __init__(self, default=None, over=None, click=None):
        self.default = {}
        if default:
            for x in default:
                self.default[list(x.json.keys())[0]] = list(x.json.values())[0]
        self.mouse_over = {}
        if over:
            for x in over:
                self.mouse_over[list(x.json.keys())[0]] = list(x.json.values())[0]
        self.left_click = {}
        if click:
            for x in click:
                self.left_click[list(x.json.keys())[0]] = list(x.json.values())[0]

    '''
    While making a Visualization Option we are care about
     1. which object will be influenced,
     2. what to response in the InteractiveEvent
     3. what is the default value(prepare to do for some high freq data)

    Attributes:
        default: a list of interactive actions, however for default, we receive ValueChanged,
         we consider it as the default value
        mouse_over: a list of interactive actions defined the action when mouse in the node/edge
        left_click: a list of interactive actions defined the action when mouse left click the node/edge
        right_click: a list of interactive actions defined the action when mouse left click the node/edge
    '''

    @property
    def json(self):
        '''
        to generate a json data structure for javascript usage.
        :return:
        '''
        return {
            "default": self.default,
            "over": self.mouse_over,
            "left": self.left_click,
        }


Option = VisualizationOption

class InteractiveAction:
    def __init__(self):
        self.type = 'option'

    '''
        The basic class of every Interactive Action.
    '''

    @property
    def json(self):
        raise NotImplementedError


class ValueChanged(InteractiveAction):
    def __init__(self, setting):
        InteractiveAction.__init__(self)
        if type(setting) is not dict:
            raise Exception("Setting must be a dictionary")
        self.setting = setting

    @property
    def json(self):
        return {"value_changed": self.setting}

VC = ValueChanged


class Prop(InteractiveAction):
    def __init__(self, color=None, bg_color=None, opacity=None, scale=None):
        InteractiveAction.__init__(self)
        self.setting = {
            NP.COLOR: color,
            NP.BG_COLOR: bg_color,
            NP.OPACITY: opacity,
            NP.SCALE: scale
        }

    @property
    def json(self):
        return {"value_changed": {k: v for k, v in self.setting.items() if v}}


class Connection(InteractiveAction):
    def __init__(self, edges):
        InteractiveAction.__init__(self)
        self.targets = edges

    @property
    def json(self):
        return {"connection": [x.json for x in self.targets]}


class Edge:
    def __init__(self, targetId, width=1, line_style="solid",
                 line_color="#000000", opacity=1, target_style=None):
        self.targetId = targetId
        self.width = width
        self.line_style = line_style
        self.line_color = line_color
        self.opacity = opacity
        self.target_style = target_style

    '''
    For a EDGE, set itself property and the target node property
    Attributes:
        target_style: a dictionary or a instance of ValueChanged.
    '''

    @property
    def json(self):
        return [
            self.targetId, {
                "width": self.width,
                "line-color": self.line_color,
                "line-style": self.line_style if self.line_style in ("solid", "dotted", "dashed") else "solid",
                "opacity": self.opacity,
                "target-style": self.target_style.json if isinstance(self.target_style,
                                                                     ValueChanged) else self.target_style
            }
        ]


class HyperLink(InteractiveAction):
    def __init__(self, name, url):
        InteractiveAction.__init__(self)
        self.name = name
        self.url = url

    @property
    def json(self):
        return {
            "link":
                {"url":  self.url,
                 "name": self.name
                 }
        }


class PopUp(InteractiveAction):
    '''
    A PopUp windows, is implemented by qtip in javascript, it is tab based, with means you can add many(suggested <=3)
    tabs to show the information you want to display to the users, one tab usage may like: 1. Information Tab, 2. Value
    Tab, 3. Model or sequence tab.
    '''
    def __init__(self, tab_lists, width=400, height=300):
        InteractiveAction.__init__(self)
        self.tabs = tab_lists
        self.width = width
        self.height = height

    @property
    def json(self):
        return {"popup": {"tab": [x.json for x in self.tabs], "width": self.width, "height": self.height}}


class PopUpTab:
    '''
    I am the father of all pop up tab
    '''
    def __init__(self, name, subtype):
        self.type = 'tab'
        self.subtype = subtype
        self.name = name

    @property
    def json(self):
        raise NotImplementedError


class TextTab(PopUpTab):
    def __init__(self, name, text):
        PopUpTab.__init__(self, name, "text")
        self.name = name
        self.text = text

    @property
    def json(self):
        return ["text", {"text": self.text, "name": self.name}]


class TableTab(PopUpTab):
    '''
    This is a table tab, we will automaticly draw the Table in a tab for u
    Input:
        table: a 2D array: [
            [raw1_1, raw1_2, ...]
            [raw2_1, raw2_2, ...]
            ...
        ], note: every element in table should have same length

    '''
    def __init__(self, name, table):
        PopUpTab.__init__(self, name, "table")
        self.table = table

    def content(self):
        content = ""
        for x in self.table:
            content += "<tr>\n\t"
            for y in x:
                content += "<td>{}</td>\n".format(y)
            content += "</tr>\n"
        return content

    @property
    def json(self):
        return ["table", {"table": self.table, "name": self.name}]


class ImageTab(PopUpTab):
    '''
    This is a image tab, when using this, input a image file path.
    '''
    def __init__(self, name, image_path):
        PopUpTab.__init__(self, name, "image")
        self.image_path = image_path

    @property
    def json(self):
        return ["image", {"url": self.image_path, "name": self.name}]


class ChartTab(PopUpTab):
    '''
    This is a Chart tab that draw tab in javascript interactively. using Echarts
    Inputs:
        type: currently support Pie, Bar, Scatter, Line and Box plot.
    '''
    def __init__(self, name, setting):
        PopUpTab.__init__(self, name, "chart")
        self.setting = setting

    @property
    def json(self):
        return ["chart", {"option": self.setting, "name": self.name}]


class ModelTab(PopUpTab):
    '''
    This class visualize a tab containing a 3D model.
    '''
    def __init__(self, name, model):
        PopUpTab.__init__(self, name, model)
        self.model = model

    @property
    def json(self):
        return ["model", {"model": self.model, "name": self.name}]
