# Network Propagation
This module implements three algorithms: `random walk`, `random walk with restart` and `heat kernel`. The 
implementation of these modules based on the paper
> Network propagation: a universal amplifier of genetic associations

All these method start with a vector = |V| and simulate the heat diffuse process in the network.
the difference between these methods are list in the following table (figure from above paper).

![](images/propagation/propagation_overview.png)

## Example Notebook

The example notebook exists in `$project_root/examples/analysis/propagation.ipynb` or view at [Github](https://github.com/iseekwonderful/PyPathway/blob/master/examples/analysis/propagation.ipynb)

## Random Walk

### API
```python
def random_walk(G: nx.Graph, heat: dict, n: int = -1, threshold: float = 1e-6) -> nx.Graph
```

### Arguments:
* `G: nx.Graph` : the input graph.
* `heat` : the heat dict, should have same length with G, contain the node name and the heat value
* `n: int = -1` : the time random walk repeats, if n==-1, the loop will stop when the
    threshold is reached.
* `threshold`: the threshold check whether the steady state is reached.

### Return value
nx.Graph (copied) with node property `heat` with the result heat of each node.

### Example

```
# the graph
In [3]: G = nx.Graph([[1, 2], [2, 3], [3, 5], [2, 5], [1, 4], [4, 5]])
# the heat
In [4]: h = {1: 0, 2: 1, 3: 0, 4: 1, 5: 0}
In [5]: dict(random_walk(G, h).node)

Out [5]: 
{1: {'heat': 0.33333342635070995},
 2: {'heat': 0.49999990698262176},
 3: {'heat': 0.3333333333333327},
 4: {'heat': 0.3333332403159554},
 5: {'heat': 0.50000009301737625}}
```

## Random Walk with Restart (RWR)

### API
```
def random_walk_with_restart(G: nx.Graph, heat: dict, rp: float, n: int = -1, threshold: float = 1e-6) -> nx.Graph:
```

### Arguments:
* `G: nx.Graph` : the input graph.
* `heat` : the heat dict, should have same length with G, contain the node name and the heat value
* `n: int = -1` : the time random walk with restart repeats, if n==-1, the loop will stop when the
    threshold is reached.
* `rp`: restart probability.
* `threshold`: the threshold check whether the steady state is reached.

### Return value
nx.Graph (copied) with node property `heat` with the result heat of each node

### Example

```
# the graph
In [3]: G = nx.Graph([[1, 2], [2, 3], [3, 5], [2, 5], [1, 4], [4, 5]])
# the heat
In [4]: h = {1: 0, 2: 1, 3: 0, 4: 1, 5: 0}
In [5]: dict(random_walk_with_restart(G, h, rp=0.7, n=-1).node)

Out [5]: 
{1: {'heat': 0.18859903381642515},
 2: {'heat': 0.76309178743961337},
 3: {'heat': 0.096618357487922704},
 4: {'heat': 0.74859903381642512},
 5: {'heat': 0.20309178743961354}}
```

## Heat kernel

### API
```
def diffusion_kernel(G: nx.Graph, heat: dict, rp: float, n: int, threshold: float = 1e-6) -> nx.Graph:
```

### Arguments:
* `G: nx.Graph` : the input graph.
* `heat` : the heat dict, should have same length with G, contain the node name and the heat value
* `n: int = -1` : the time random walk with restart repeats.
* `rp`: restart probability.

### Return value
nx.Graph (copied) with node property `heat` with the result heat of each node

### Example

```
# the graph
In [3]: G = nx.Graph([[1, 2], [2, 3], [3, 5], [2, 5], [1, 4], [4, 5]])
# the heat
In [4]: h = {1: 0, 2: 1, 3: 0, 4: 1, 5: 0}
In [5]: dict(diffusion_kernel(G, h, rp=0.8, n=100).node)

Out [5]: 
{1: {'heat': 0.42138736822730222},
 2: {'heat': 0.38934416321338194},
 3: {'heat': 0.32359870881215813},
 4: {'heat': 0.47852257848932078},
 5: {'heat': 0.38714718125782877}}
```

