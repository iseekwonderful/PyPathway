# Implementation correctness

Here we will demonstrate the implementation correctness by comparing the result to exist implementation in R or C lang.

## ORA and SPIA
The SPIA method including the result of ORA analysis thus we check the implementation of SPIA and ORA together in this section.
### The result from R package SPIA
The code below could be found in [SPIA's docs](https://bioconductor.org/packages/release/bioc/vignettes/SPIA/inst/doc/SPIA.pdf).

``` R
> library(SPIA)
> library(hgu133plus2.db)
> x <- hgu133plus2ENTREZID
> top$ENTREZ<-unlist(as.list(x[top$ID]))
> top<-top[!is.na(top$ENTREZ),]
> top<-top[!duplicated(top$ENTREZ),]
> tg1<-top[top$adj.P.Val<0.1,]
> DE_Colorectal=tg1$logFC
> names(DE_Colorectal)<-as.vector(tg1$ENTREZ)
> ALL_Colorectal=top$ENTREZ

> res=spia(de=DE_Colorectal,all=ALL_Colorectal,organism="hsa",nB=2000,plots=FALSE,beta=NULL,combine="fisher",verbose=FALSE)
```

And the top10 result is listed in the table below. (`Id`, `pSize`, `NDE` is removed for the space consideration)

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Name</th>
      <th>pNDE</th>
      <th>pPERT</th>
      <th>pG</th>
      <th>pGFdr</th>
      <th>pGFWER</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Focal adhesion</td>
      <td>1.009186e-07</td>
      <td>0.000005</td>
      <td>1.479215e-11</td>
      <td>2.026525e-09</td>
      <td>2.026525e-09</td>
      <td>Activated</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Alzheimer's disease</td>
      <td>2.503714e-11</td>
      <td>0.221000</td>
      <td>1.489554e-10</td>
      <td>1.020344e-08</td>
      <td>2.040688e-08</td>
      <td>Inhibited</td>
    </tr>
    <tr>
      <th>2</th>
      <td>ECM-receptor interaction</td>
      <td>4.058570e-06</td>
      <td>0.000005</td>
      <td>5.199181e-10</td>
      <td>2.374293e-08</td>
      <td>7.122878e-08</td>
      <td>Activated</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Parkinson's disease</td>
      <td>6.435720e-10</td>
      <td>0.062000</td>
      <td>9.953264e-10</td>
      <td>3.408993e-08</td>
      <td>1.363597e-07</td>
      <td>Inhibited</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Pathways in cancer</td>
      <td>4.194045e-05</td>
      <td>0.003000</td>
      <td>2.124922e-06</td>
      <td>5.822286e-05</td>
      <td>2.911143e-04</td>
      <td>Activated</td>
    </tr>
  </tbody>
</table>

### The Result from PyPathway

``` python
from pypathway import *
c = ColorectalCancer()
r2 = SPIA.run(c.deg, c.background, organism="hsa")
```

The top5 result is list in the table below. 

* the `seed` in the SPIA package can not be settled so in the result of `pG`, `pGfdr` and `pGFWER` there are some deviation but still in same order of magnitude。
* the result of `pNDE` indicate that the implementation of `ORA` is correct (In `PyPathway`, the `SPIA` and `ORA` use same implementation of `ORA`).

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>pNDE</th>
      <th>pPERT</th>
      <th>pG</th>
      <th>pGfdr</th>
      <th>pGFWER</th>
      <th>status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>04510</th>
      <td>Focal adhesion</td>
      <td>1.00919e-07</td>
      <td>5e-06</td>
      <td>1.47922e-11</td>
      <td>2.02653e-09</td>
      <td>2.02653e-09</td>
      <td>Activated</td>
    </tr>
    <tr>
      <th>05010</th>
      <td>Alzheimer's disease</td>
      <td>2.50371e-11</td>
      <td>0.232</td>
      <td>1.56087e-10</td>
      <td>1.0692e-08</td>
      <td>2.1384e-08</td>
      <td>Inhibited</td>
    </tr>
    <tr>
      <th>04512</th>
      <td>ECM-receptor interaction</td>
      <td>4.05857e-06</td>
      <td>5e-06</td>
      <td>5.19918e-10</td>
      <td>2.37429e-08</td>
      <td>7.12288e-08</td>
      <td>Activated</td>
    </tr>
    <tr>
      <th>05012</th>
      <td>Parkinson's disease</td>
      <td>6.43572e-10</td>
      <td>0.058</td>
      <td>9.33601e-10</td>
      <td>3.19758e-08</td>
      <td>1.27903e-07</td>
      <td>Inhibited</td>
    </tr>
    <tr>
      <th>05200</th>
      <td>Pathways in cancer</td>
      <td>4.19405e-05</td>
      <td>0.007</td>
      <td>4.7094e-06</td>
      <td>0.000129038</td>
      <td>0.000645188</td>
      <td>Activated</td>
    </tr>
  </tbody>
</table>

## GSEA
We use the Java implementation from board institute to check the implementation correctness.
## Enrichnet
### Result of the Enrichnet we interface
### Result of PyPathway
## Propagation
### Heat diffuse
We use [Cytoscape Diffusion APP](http://apps.cytoscape.org/apps/diffusion) to check the correctness of the heat diffusion.
#### Result of Diffusion APP

** Image here

#### Result of PyPathway

* code

``` python
from pypathway import diffusion_kernel
G = nx.Graph([[1, 2], [2, 3], [3, 5], [2, 5], [1, 4], [4, 5]])
h = np.array([0, 1, 0, 1, 0])
diffusion_kernel(G, h, rp=0.7, n=100).node
```

* result

```
{1: {'heat': 0.41720485133090102},
 2: {'heat': 0.39506307105908312},
 3: {'heat': 0.30896131580088793},
 4: {'heat': 0.49570801546580717},
 5: {'heat': 0.38306274634330961}}
```


## MAGI

### Pathway select

#### original
We compile MAGI source code in Ubuntu 14.04 and run pathway select with following CMD. (Note that `/Volumes/Data/magi` is the location of official example file dir).

``` shell
./Pathway_Select -p /Volumes/Data/magi/StringNew_HPRD.txt -c /Volumes/Data/magi/ID_2_Autism_4_Severe_Missense.Clean_WithNew.txt -h /Volumes/Data/magi/GeneCoExpresion_ID.txt -e /Volumes/Data/magi/adj1.csv.Tab.BinaryFormat -d /Volumes/Data/magi/New_ESP_Sereve.txt -l /Volumes/Data/magi/Gene_Name_Length.txt -i 1
```

For **BestPaths.Length8.Control4.Run0** we find 430 identical
Candidate of best path.

#### PyPathway
We use following code to run pathway select in pypathway

``` python
path = "/Volumes/Data/magi/"
MAGI.select_pathway(
    path + 'StringNew_HPRD.txt', 
    path + 'ID_2_Autism_4_Severe_Missense.Clean_WithNew.txt', 
    path + 'GeneCoExpresion_ID.txt', path + 'adj1.csv.Tab.BinaryFormat', 
    path + 'New_ESP_Sereve.txt',
    path + 'Gene_Name_Length.txt'
)
```

For **BestPaths.Length8.Control4.Run0** we also find 430 identical Candidate of best path and is identical to the original result.

### Cluster
