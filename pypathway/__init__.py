import sys

# the interfaces core object exposes to users
if sys.version[0] == "2":
    from core.SBGNImpl import SBGNParser
    from core.GPMLImpl import GPMLParser
    from core.KGMLImpl import KEGGParser
    from core.BioPAXImpl import BioPAXParser

    # the interface database query expose to users
    from query.database import PublicDatabase
    from query.common import PathwayFormat, SupportedDatabase
    from visualize.options import *
    from query.network import *

    from utils import plot
else:
    from .core.SBGNImpl import SBGNParser
    from .core.GPMLImpl import GPMLParser
    from .core.KGMLImpl import KEGGParser
    from .core.BioPAXImpl import BioPAXParser

    # the interface database query expose to users
    from .query.database import PublicDatabase
    from .query.common import PathwayFormat, SupportedDatabase
    from .visualize.options import *
    from .query.network import *

    from .utils import plot


def version():
    return "0.17.1"

