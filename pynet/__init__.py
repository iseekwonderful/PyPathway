# the interfaces core object exposes to users
from .utils import IdMapping, GMTUtils

from .pathviz.query import PublicDatabase, STRING, BioGRID

from .analysis.ora import ORA, KEGG, Reactome, GO

from .analysis.gsea import GSEA

from .analysis.network import SPIA, Enrichnet

from .analysis.modelling import MAGI, Hotnet2

from .netviz import FromCYConfig, FromNetworkX, StylePresets


def version():
    return "0.31"

