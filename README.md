# PyPathway
A IPython package for pathway visualization

## Installation
* Install this package using PyPI
```shell
pip install pypathway
```

## Get started
* Start a IPython notebook

```shell
# in shell
ipython notebook
```

* Search pathway with keyword `Jak`, parse and draw the first result
![](https://iseekwonderful.github.io/PyPathway/images/query/try_it_out_kg.png)

## Search and Retrieve

`PublicDatabase` class provide staticmethod `search_kegg`, `search_wp`, `search_reactome` for databse **KEGG**, **Reactome** and **WikiPathway**
* example of search these database and draw the first result of WikiPathway
![](https://iseekwonderful.github.io/PyPathway/images/query/try_it_out_image.png)

You can also view the docs about [Search and Retrieve](https://iseekwonderful.github.io/PyPathway/user-guide/query/)
 
## Parse and Tree API
`SBGNParser`, `BioPAXParser`, `GPMLParser` and `KGMLParser` is implemented to parse `KGML`, `SBGN`, `BioPAX` and `GPML` format pathway data. the `BioPAXParser` is based on [paxtools](https://biopax.github.io/Paxtools/), other is implement native.

We offer API to operate pathway as a tree, which has documentation at [docs](https://iseekwonderful.github.io/PyPathway/user-guide/core/)

## Data mapping
Using Python API to add addition information to pathway various graphic property
* glyph property: `color`, `scale`, `opacity`
* edge: `additional edge`, `width`, `style`, `color`
* chart, table, image and textField in a popup while certain event happend, such as mouse_over, left click, right_click.

docs is [here](https://iseekwonderful.github.io/PyPathway/user-guide/map/)

## Visualization
A web based Visualizer based on `SBGNviz`, `pvjs` and `Cytoscape`, provide interactively visualize experience.

Using `draw()` method of each pathway object, pypathway will present a plotting of pathway in the output area of IPython notebook. 