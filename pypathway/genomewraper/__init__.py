# This module warp the islandplot as output area, provide the API.
from jucell.display import Plotable, PlotOnlyInterface
import os


class IslandPlot(Plotable):
    def __init__(self, config: dict):
        self.config = config

    def plot(self):
        pi = PlotOnlyInterface(host=self)
        return pi.update()

    def serialize(self):
        return {}

    @property
    def data(self):
        return self.serialize()

    @property
    def instance_name(self):
        return 'genome_view'

    @property
    def assets_path(self):
        return os.path.dirname(os.path.realpath(__file__)) + '/assets'

    @property
    def config_path(self):
        return '/data/test2.json'
