## Network process

APIs for querying and retrieval interaction network from public database. The return object are stored in networkx graph object.

## APIs
### STRING
**Single or list molecular**
To search interaction network related to STRING database, use staticmethod `STRING.search(name, organism)` .

![](/Users/sheep/Desktop/Figures/process/string_search.png)

and each search result could be retrieved using its `load` method; the result of `load` method is a `networkx.Graph` with a additional `plot` method. Use the plot method to draw the graph.

![](/Users/sheep/Desktop/Figures/process/string_draw.png)

**Entire network**
Also, download the total interaction network is available for certain organism. use `STRING.overall_network(organism)` to retrieve the total interaction network to a networkx object.

```
# This function returns a nx.Graph object G contain the entire network from string for species hsa.
G = STRING.overall_graph("hsa")
```
### BioGRID
**Single or list of molecular**

Similar to STRING, single or list molecular search is implemented in `BioGRID.search`, supports three type of id: [`Symbol`, `Extrez`, `pubmed`].
![](/Users/sheep/Desktop/Figures/process/BioGrid.png)

The result is the `networkx.Graph` object with additional plot object.
![](/Users/sheep/Desktop/Figures/process/plot.png)
**Entire networks**

Using `BioGRID.overall_network(organism)` to retrieve the entire network.

## KEGG
To search and retrieve pathway from KEGG


## Reactome