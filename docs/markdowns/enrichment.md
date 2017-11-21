# Enrichment Analysis

## Overview
Enrichment analysis aim to find functional set which are over-represented in the large set of protein or genes. In this section, we will go through the supported
enrichment, demonstrate the definition and the usage of each method. 

## Basic class
All the class of enrichment analysis are inherited from `EnrichmentResult`. This class holds the 
 result of the enrichment analysis and the subclass should at least
 rewrite the statistic method `run` to perform the analysis.
 
### methods
* `run` : execute the enrichment analysis and return the instance of subclass contains
the analysis information

* `table` : return the result pandas.Dataframe

* `plot` : plot the bar chart in the output area

* `graph` : if the result set have certain relationship, this method return the graph of them.
for example, the Gene Ontology ORA subclass return the graph of GO DAG of significant sets.

## ORA
The over-representation analysis is the most widely used enrichment analysis method, It use
Fisher's exact test to check whether certain functional set is over-represented in a large set
of protein or genes.

### Implementation
The ORA methods is implemented in the `analysis.ora`

```python
# general ora method
ORA.run(study, pop, gene_set, adjust='fdr_bh')    
```

* `study`: `set` or `list` of significant differential expressed genes or proteins. E.g. `[A, B, C, D]`
* `pop` `set` or `list` of the total annotated genes or proteins. E.g. `[A, B, C, D, E, F, G]`
* `gene_set` is a dict contains. 
the gene set name and contained genes like 
```
{"B cell receptor pathway": {"CD22", "CD81"...}...}
```
. This information usually parsed from a GMT file use `GMTUtils`.

### Example
```python
# import necessary module
from pypathway.analysis.ora import KEGG, ORA
from pypathway.utils import ColorectalCancer, IdMapping, GMTUtils

# load a gene_set from a gmt file
gmt = GMTUtils.parse_gmt_file("../../tests/gmt_file/h.all.v6.0.entrez.gmt")

# load data set
c = ColorectalCancer()

# perform general ORA test
res_h = ORA.run(c.deg_list, c.background, gmt)

# view result table
res_h.table.head()
```
The result table (In IPython notebook):

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>mapped</th>
      <th>number in study</th>
      <th>p-value</th>
      <th>fdr</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>HALLMARK_GLYCOLYSIS</td>
      <td>184</td>
      <td>91</td>
      <td>9.956407e-08</td>
      <td>3.555860e-07</td>
    </tr>
    <tr>
      <th>1</th>
      <td>HALLMARK_APICAL_JUNCTION</td>
      <td>185</td>
      <td>97</td>
      <td>7.750142e-10</td>
      <td>3.748583e-09</td>
    </tr>
    <tr>
      <th>2</th>
      <td>HALLMARK_MYC_TARGETS_V1</td>
      <td>173</td>
      <td>48</td>
      <td>8.377692e-01</td>
      <td>9.106187e-01</td>
    </tr>
    <tr>
      <th>3</th>
      <td>HALLMARK_COAGULATION</td>
      <td>131</td>
      <td>64</td>
      <td>1.237516e-05</td>
      <td>3.093790e-05</td>
    </tr>
    <tr>
      <th>4</th>
      <td>HALLMARK_MTORC1_SIGNALING</td>
      <td>176</td>
      <td>90</td>
      <td>1.551015e-08</td>
      <td>5.965443e-08</td>
    </tr>
  </tbody>
</table>

```python
# barplot
res_h.plot()
```
![](img_https://github.com/iseekwonderful/PyPathway/blob/master/docs/markdowns/images/enrichment/enrichment_general_ora.png)

### Specific ORA
For KEGG, REACTOME and GO, there are specific class implement for them. This class preloaded the gene sets or the DEG file before the analysis are performed. 

#### The APIs
The input and output data structure are same as the basic ORA.

* `KEGG` 

```python
#rather than input specific gene set, organism is accepted and geneset will be retrieved.
r_kg = KEGG.run(c.deg_list, c.background, 'hsa')
```

* `Reactome`

```
# Reactome official API is used. note that the background is the whole Reactome
# library, if background set required, use Reactome GMT file and ORA class 
r = Reactome.run(sybs, organism='Homo sapiens')
```

* `Gene Ontology`

```python
# Gene ontology analysis require additional a assoc file.
# IdMapping class could be used to generate this file
# c.background is to background gene list of certain study
r = IdMapping.convert_to_dict(input_id=c.background, source='ENTREZID', target="GO", organism='hsa')
# and run the analysis
# [str(x) for x in c.deg_list]: study
# [str(x) for x in c.background]: background
# r: the assoc dict
# obo=path + 'go-basic.obo': the path to the obo file
rg = GO.run([str(x) for x in c.deg_list], [str(x) for x in c.background], r, obo=path + 'go-basic.obo')
```

The gene ontology enrichment analysis provide the graph overview of the analysis
![](https://github.com/iseekwonderful/PyPathway/blob/master/docs/markdowns/images/enrichment/GO%20graph%20plot.png)

## GSEA
The Gene Set Enrichment Analysis(GSEA) is a computational method that determines whether an a priori defined set of genes shows statistically 
significant, concordant differences between two biological states. is introduced in paper:
> Gene set enrichment analysis: A knowledge-based approach for interpreting genome-wide expression profiles

at [PNAS](http://www.pnas.org/content/102/43/15545.short)

This class is implement via [GSEApy](https://github.com/BioNinja/GSEApy)

### Usage

#### Input data structure
Differ to other analysis class, the GSEA need to do a phenotypic-based permutation test, so the original data is need.

* The gene_sets: receives both get dict or a library name in [Enrichr's library](http://amp.pharm.mssm.edu/Enrichr/#stats)

* The cls file, this file format defines phenotype (class or template) labels and associates each sample in the expression data with a label. The CLS file format uses spaces or tabs to separate the fields. For detail information, please refer to the [official documents](https://software.broadinstitute.org/cancer/software/gsea/wiki/index.php/Data_formats#CLS:_Categorical_.28e.g_tumor_vs_normal.29_class_file_format_.28.2A.cls.29)

![](https://software.broadinstitute.org/cancer/software/gsea/wiki/images/6/6d/Cls_format_snapshot.png)

* The expression file. A pandas data frame contains the expression  value (counts, TPM). e.g.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Name</th>
      <th>2965M patient's mucosa</th>
      <th>3216M patient's mucosa</th>
      <th>3335M patientüs mucosa</th>
      <th>3416M patient's mucosa</th>
      <th>3578M patientüs mucosa</th>
      <th>3798M patientüs mucosa</th>
      <th>3838M patientüs mucosa</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>A1BG-AS1</th>
      <td>1.618062</td>
      <td>1.631023</td>
      <td>1.751713</td>
      <td>1.942189</td>
      <td>1.389749</td>
      <td>1.620180</td>
      <td>1.222842</td>
    </tr>
    <tr>
      <th>A1CF</th>
      <td>2.029520</td>
      <td>3.323313</td>
      <td>3.315563</td>
      <td>2.795794</td>
      <td>3.209412</td>
      <td>2.805799</td>
      <td>1.633054</td>
    </tr>
    <tr>
      <th>A2M</th>
      <td>2.994217</td>
      <td>2.556958</td>
      <td>2.999796</td>
      <td>3.354563</td>
      <td>3.143560</td>
      <td>2.776570</td>
      <td>3.075487</td>
    </tr>
    <tr>
      <th>A2M-AS1</th>
      <td>2.233742</td>
      <td>1.709143</td>
      <td>1.968936</td>
      <td>2.648101</td>
      <td>2.353158</td>
      <td>2.346996</td>
      <td>2.903206</td>
    </tr>
  </tbody>
</table>

#### API

```python
# gene_exp is the expression dataframe
# class_vector is the define of the experiment
gs_res = gp.gsea(data=gene_exp, gene_sets='KEGG_2016', cls=class_vector, 
                 permutation_type='phenotype', #set permutation_type to phenotype when 
                 outdir='gsea_reprot', method='signal_to_noise', format='png')
```
more detail information is described in the `example/analysis/GSEA.ipynb`

### SPIA

The Signaling Pathway Impact Analysis, is introduced in paper:
> [A novel signaling pathway impact analysis](https://academic.oup.com/bioinformatics/article/25/1/75/302846/A-novel-signaling-pathway-impact-analysis#)

we implement this algorithm in Python.

#### Usage

```python
r = SPIA.run(de=c.deg, all=c.background)
```

* de: a python dict of DEGs. key: gene, value: fold-change. e.g. `{'A': 2.1, 'B': 3.0 ...}`
* all: a python list of total genes. the idtype is ENTREZ. If necessary, use IDMapping to convert other idtype to ENTREZ. e.g. `['A', 'B', 'C', 'D']`

### Enrichnet

The Enrichnet algorithm is introduced in paper
> [EnrichNet: network-based gene set enrichment analysis](https://academic.oup.com/bioinformatics/article/28/18/i451/247049/EnrichNet-network-based-gene-set-enrichment)

we implement the Python API for Enrichnet HTTP service.

#### Usage

```python
run(genesets, idtype='hgnc_symbol', pathdb='kegg', graph='string')
```
* genesets: the gene list used to run the analysis. E.g. `['A', 'B' ...]`
* idtype: input id type. Supports idtype: `['ensembl', 'hgnc_symbol', 'refseq_dna', 'uniprot_swissprot']`
* the pathlib: function set library. Supports pathdb: `['kegg', 'biocarta', 'reactome', 'wiki', 'nci', 'interpro', 'gobp', 'gomf', 'gocc']`
* graph: the graph database. Supports `['string', 'bossi']`.


