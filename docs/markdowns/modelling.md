## MAGI

MAGI ( Merge Affected Genes into Integrated networks ) is originally published in the paper [The discovery of integrated gene networks for autism and related disorders](http://genome.cshlp.org/content/early/2014/11/05/gr.178855.114.abstract). Which combines the interactive network and the co-expression network to find functional modules.

### Original C Implementation
[https://eichlerlab.gs.washington.edu/MAGI/](https://eichlerlab.gs.washington.edu/MAGI/) The source and example files are available in this website.

### Overview
The C implementation only use one thread and lacks exception handling. We provide the Python interface with modified multi-process model and File IO exception handler. The `MAGI` class including the `pathway_select` and the `clustring` module. The visualization methods are provided to plot the `module`'s network.

### pathway_select
The static method `MAGI.select_pathway` are used to generate the seed pathway use color-coding algorithm.
```
select_pathway(ppi, case, coExpId, coExpMat, ctrl, length, filter=None, process=4)
```

**Parameter**

* `ppi`: the Protein-protein interaction network, example: `StringNew_HPRD`.
* `case`: the case denote mutation list, example: `ID_2_Autism_4_Severe_Missense.Clean_WithNew`
* `coExpId`: The input gives the order of each gene appearing in the coExpression matrix. example `GeneCoExpresion_ID`
* `coExpMat`: the Pairwise gene coexpression values, example: `adj1.csv.Tab.BinaryFormat`.
* `ctrl`: The number of mutations in each gene in controls. example: `New_ESP_Sereve`
* `filter`: optional, remove set of the gene in PPI.
* `length`: the length of each genes, example: `Gene_Name_Length`

**Example**

*note*: put the [example assets](https://eichlerlab.gs.washington.edu/MAGI/) to the path folder.

```
# path is the path to the assets file.
MAGI.select_pathway(path + 'StringNew_HPRD.txt', path + 'ID_2_Autism_4_Severe_Missense.Clean_WithNew.txt',
                   path + 'GeneCoExpresion_ID.txt', path + 'adj1.csv.Tab.BinaryFormat', path + 'New_ESP_Sereve.txt',
                   path + 'Gene_Name_Length.txt')
```

Output file in this step including the seed file and the random list file will be written to the `cache` dir.

### Clustering
This step cluster the seeds pathway we get in the previous step to a functional module.the static method `MAGI.clustering` are used to do this job.

```python
def cluster(ppi, coExpId, coExpMat, upper_mutation_on_control,
                min_size_of_module, max_size_of_module, min_ratio_of_seed,
                minCoExpr=None, avgCoExpr=None, avgDensity=None, seed=None, score=None):

```

**Parameter**

* `ppi`: the Protein-protein interaction network, example: `StringNew_HPRD`.
* `coExpId`: The input gives the order of each gene appearing in the coExpression matrix. example `GeneCoExpresion_ID`
* `coExpMat`: the Pairwise gene coexpression values. example: `adj1.csv.Tab.BinaryFormat`.
* `upper_mutation_on_control`: The total number of mutations in control's allowed.
* `min_size_of_module`: 	The minimum number of genes in the module
* `max_size_of_module`: 	The maximum number of genes in the module
* `min_ratio_of_seed`: For each seed type the top percentage of the score from maximum score of the seed allowed (in the paper `0.5` was used)
* `minCoExpr`: The minimum pair-wise coexpression value per gene allowed (the default is 0.01, i.e. `r^2>0.01`, which is the median coexpression value in the input `adj1.csv.Tab.BinaryFormat`)
* `avgCoExpr`: The minimum average coexpression of the modules allowed (the default is `0.415`)
* `avgDensity`: 		The minimum avergae PPI density of the modules allowed (the default is 0.08)
* `seed`: if the `MAGI.select_pathway` is called before, than ignore this. is the seed is generate by CLI PathwaySelect, use the seed file path here
* `score`: similar to `seed`, input CLI generate score file path else None;

**Example**

```python
result = MAGI.cluster(path + 'StringNew_HPRD.txt', path + 'GeneCoExpresion_ID.txt', path + 'adj1.csv.Tab.BinaryFormat', 2, 5, 100, 0.5)
```

The result a list of `MAGIResult` class.

```python
# plot the result
result[0].plot()
```

## Export result
Use `MAGIExport.export` method to export the result of a clustering result.

```
MAGIExport.export(result)
```

Which generates a HTML page displaying the modules and its visualization.