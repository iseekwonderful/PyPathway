integrated toolkit for pathway based analysis

![](https://img.shields.io/badge/license-MIT-blue.svg)


## Installation

## Overview
* Public databases APIs: `STRING`, `BioGRID`, `KEGG`, `Reactome` and `WikiPathway`
* Functional set based and network based enrichment analysis algorithms implemented: `ORA`, `GSEA` and `SPIA`
* Performance optimize for denovo enrichment algorithm `MAGI` and `Hotnet2`.
* Interactive visualization for pathway, graph and analysis result.
* Web page exportation for results.

## Features
* Integrated with numpy and networkx
* Dynamic visualization for IPython notebook
* Most classes implement `__repr__` method for interactive environment

## Network process

Intuitive APIs for querying and retrieval interaction network from public database. The return object are stored in networkx graph object.

### search
```
from pypathway import PublicDatabase
kg = PublicDatabase.search_kegg('CD4')
wp = PublicDatabase.search_wp('CD4')
rt = PublicDatabase.search_reactome('CD4')
```

### load

```
pathway = r[0].load()
```

### plot

```
pathway.draw()
```

![](https://github.com/iseekwonderful/PyPathway/blob/master/docs/markdowns/images/network_process/netprocess_KEGG.png)

### IPython examples

* [STRING and BioGRID](https://github.com/iseekwonderful/PyPathway/blob/master/examples/pathviz/STRING%7CBioGID_query.ipynb)
* [Pathway databases](https://github.com/iseekwonderful/PyPathway/blob/master/examples/pathviz/Pathway_Datatbase_APIs.ipynb)

## Enrichment Analysis

### Supports

* ORA
* GSEA
* Network enrichment (SPIA and Enrichment)
* denovo enrichment (MAGI and Hotnet2)

### Implementation

* Staticmethod `run()` for the starting of the analysis
 
```python
r = SPIA.run(all=c.background, de=c.deg, organism='hsa')
```

* `table`, `plot()` and `graph()` method for the presentation of the analysis

![](https://github.com/iseekwonderful/PyPathway/blob/master/docs/markdowns/images/enrichment/enrichment_table.png)
![](https://github.com/iseekwonderful/PyPathway/blob/master/docs/markdowns/images/enrichment/enrichment_general_ora.png)
![](https://github.com/iseekwonderful/PyPathway/blob/master/docs/markdowns/images/enrichment/GO%20graph%20plot.png)

### IPython examples

* [ORA](https://github.com/iseekwonderful/PyPathway/blob/master/examples/analysis/ORA.ipynb)
* [GSEA](https://github.com/iseekwonderful/PyPathway/blob/master/examples/analysis/GSEA.ipynb)
* [Network enrichment](https://github.com/iseekwonderful/PyPathway/blob/master/examples/analysis/network_enrichment.ipynb)
* [MAGI](https://github.com/iseekwonderful/PyPathway/blob/master/examples/analysis/MAGI.ipynb)
* [Hotnet2](https://github.com/iseekwonderful/PyPathway/blob/master/examples/analysis/Hotnet2.ipynb)

## Modeling



## Propagation

Implemented algorithms

* Random walk
* Random walk with restart
* Heat kernel

### detail

> ![](https://github.com/iseekwonderful/PyPathway/blob/master/docs/markdowns/images/propagation/propagation_overview.png)

image source: [Network propagation: a universal amplifier of genetic associations](http://www.nature.com/nrg/journal/v18/n9/abs/nrg.2017.38.html)

## performance

## Interactive Visualization
