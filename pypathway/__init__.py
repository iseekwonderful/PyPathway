# the interfaces core object exposes to users
from .utils import IdMapping, GMTUtils, ColorectalCancer

from .pathviz.query import PublicDatabase, STRING, BioGRID

from .analysis.ora import ORA, KEGG, Reactome, GO

from .analysis.gsea import GSEA

from .analysis.network import SPIA, Enrichnet

from .analysis.modelling import MAGI, Hotnet2

from .netviz import FromCYConfig, FromNetworkX, StylePresets

from .exportion import EnrichmentExport, MAGIExport, Hotnet2Export

from .analysis.propagation import random_walk, random_walk_with_restart, diffusion_kernel


def version():
    return "0.3.5"

