class Share:
    '''
    This class is intend to sharing visualization result to the public
    Two options could be used, first is the static HTML method, second is the dynamic Django project

    '''
    @staticmethod
    def tab_layout(tabs):
        pass

    @staticmethod
    def float_panel():
        pass

    @staticmethod
    def static_panel():
        pass

    @staticmethod
    def title_bar():
        pass


class CommunicationDefinition:
    def __init__(self):
        raise Exception("This class is NOT for usage")

    nodes = {
        'label-size': 0,
        'opacity': 1,
        'shape': 'rect',
        'color': 'color',
        'border-color': 'border-color',
        'size': 'size',
        'border-width': 'border-width',
    }

    edges = {
        'width': 'width',
        'type': 'type',
        'color': 'color',
        'opacity': 'opacity',
        'label': 'label'
    }
