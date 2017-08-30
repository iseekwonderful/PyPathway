from . import Interface


class SBGNInterface(Interface):
    pass


class WPInterface(Interface):
    pass


class CYInterface(Interface):
    pass


class InformationInterface(Interface):
    def __init__(self, host):
        Interface.__init__(self, host)

    def update(self):
        pass

    def on_update(self, data):
        pass