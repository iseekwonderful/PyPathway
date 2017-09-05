#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "PPI_Graph.h"

// thread-shared
PPI_Node listNodes[maxNumNode];
int numNodes=0;
int coExpresGeneNum=0;
int totalSevereMutInCases=0;
int totalMissenseMutInCases=0;
int totalSevereMutInControl=0;
int totalLengthGenes=0;
float allNodeMeanValue=0;
float allNodesSTD=0;
int totalNodesWithScoreAssigned=0;
float coexpressionPValue[102];
float meanCoExpression, varianceCoExpression;
coExpresionGeneHash coExpresionGeneHashTable[maxNumNode];
// thread-shared
float** coExpresionMatrix;// The node is is the same as PPI node id. The nodes which are not in PPI network are discarded.


int createCoExpresionMatix(FILE *fpCoExpresionMatrix)
{
    // the file are binary fromat, but we can image what it is
    /* First we have to convert the geneNames in each instance of coexpression matrix into the id used in the PPI_Node.
     * Assuming that the coExpressionMatrix is orderd by the ids in coExpresionGeneHasTable.*/

    coExpresionMatrix = (float **)malloc(sizeof(float *) * maxNumNode);
    for (int i = 0; i < maxNumNode; i++){
        coExpresionMatrix[i] = (float* )malloc(sizeof(float) * maxNumNode);
    }

	int firstGeneCount=0, secondGeneCount=0;
	char geneName1[geneNameLen], geneName2[geneNameLen], prevGeneName[geneNameLen];
	float geneCoExpr;
	while(fscanf(fpCoExpresionMatrix, "%s %s %f\n", geneName1, geneName2, &geneCoExpr)!=EOF)
	{
		geneCoExpr=pow(geneCoExpr, 0.3333333);
		if (strcmp(geneName1, prevGeneName)!=0)
		{
			strcpy(prevGeneName, geneName1);
			firstGeneCount++;// Each new gene (first gene that comes) we increase the count for the id. The second gene starts exactly after that//
			secondGeneCount=firstGeneCount+1;
		}else{
			secondGeneCount++;
		}

		// assuing the gene number of gene1 and gene2 in coexpression gene list is firstGeneCount and secondGeneCount using the coExpresionGeneHashTable we can find their respected id in PPI_Node//

		if (coExpresionGeneHashTable[firstGeneCount].nodeId>-1 && coExpresionGeneHashTable[secondGeneCount].nodeId>-1)
		{
			coExpresionMatrix[coExpresionGeneHashTable[firstGeneCount].nodeId][coExpresionGeneHashTable[secondGeneCount].nodeId]=geneCoExpr;
			coExpresionMatrix[coExpresionGeneHashTable[secondGeneCount].nodeId][coExpresionGeneHashTable[firstGeneCount].nodeId]=geneCoExpr;
		}
		//	printf("%s %s %s %s\n", geneName1, geneName2, listNodes[coExpresionGeneHashTable[firstGeneCount].nodeId].nodeName, listNodes[coExpresionGeneHashTable[secondGeneCount].nodeId].nodeName);

	}
    return -1;
}

int isConnectedPPI(int node1, int node2)
{
	for (int count=0; count<listNodes[node1].degree; count++)
	{
		
		if (listNodes[node1].neighbours[count]==node2)
			return 1;
	} 
return 0;
}

// manage a list of node, name id and neighbours
// the node list: list node
// the count: numNodes.
int createPPI_Graph(FILE *inputPPI_FP)
{
    char geneName1[geneNameLen], geneName2[geneNameLen];
    int nodeId1, nodeId2;
	while (fscanf(inputPPI_FP, "%s\t%s\n", geneName1, geneName2)!=EOF)
	{
		//printf("%s %s\n", geneName1, geneName2);
		if (strcmp(geneName1, geneName2)!=0)
		{
			nodeId1=-1;
			nodeId2=-1;
		
			for (int count=0; count<numNodes; count++)
			{
				if (strcmp(geneName1, listNodes[count].nodeName)==0)
					nodeId1=count;
				if (strcmp(geneName2, listNodes[count].nodeName)==0)
					nodeId2=count;
			}
            // gaben is unhappy, create a new node
			if (nodeId1==-1)
			{
				listNodes[numNodes].nodeId=numNodes;
				strcpy(listNodes[numNodes].nodeName, geneName1);
				listNodes[numNodes].degree=0;
				listNodes[numNodes].weightCases=0;
				listNodes[numNodes].weightControl=0;
				nodeId1=numNodes;
				numNodes++;
			}
            // JW is sad and throw his AWP.
			if (nodeId2==-1)
			{
			
				listNodes[numNodes].nodeId=numNodes;
				strcpy(listNodes[numNodes].nodeName, geneName2);
				listNodes[numNodes].degree=0;
				listNodes[numNodes].weightCases=0;
				listNodes[numNodes].weightControl=0;
				nodeId2=numNodes;
				numNodes++;
			}
		
			listNodes[nodeId1].degree++;
			listNodes[nodeId2].degree++;
			listNodes[nodeId1].neighbours=(int *)realloc(listNodes[nodeId1].neighbours, listNodes[nodeId1].degree*sizeof(int));
			listNodes[nodeId2].neighbours=(int *)realloc(listNodes[nodeId2].neighbours, listNodes[nodeId2].degree*sizeof(int));
			listNodes[nodeId1].neighbours[listNodes[nodeId1].degree-1]=nodeId2;
			listNodes[nodeId2].neighbours[listNodes[nodeId2].degree-1]=nodeId1;
		}

	}
    return -1;
}


double log_N_Choose_M(int n, int m)
{
double val=0;


	for (int count=n-m+1; count<=n; count++)
	{
		val=val+log(count);
	}
	for (int count=1; count<=m; count++)
	{
		val=val-log(count);
	}

return val;

}


double calNewProbValue(int nodeId)
{
	

	listNodes[nodeId].weightCases=log_N_Choose_M(totalSevereMutInCases, listNodes[nodeId].numSevereMutInCases) + listNodes[nodeId].numSevereMutInCases * log(listNodes[nodeId].prob) + (totalSevereMutInCases-listNodes[nodeId].numSevereMutInCases)*log(1-listNodes[nodeId].prob);
	listNodes[nodeId].weightCases=listNodes[nodeId].weightCases+log_N_Choose_M(totalMissenseMutInCases, listNodes[nodeId].numMissenseMutInCases)+ listNodes[nodeId].numMissenseMutInCases * log(listNodes[nodeId].prob)+(totalMissenseMutInCases-listNodes[nodeId].numMissenseMutInCases)*log(1-listNodes[nodeId].prob);
	
	listNodes[nodeId].weightCases=-1*listNodes[nodeId].weightCases;
	if (listNodes[nodeId].numSevereMutInCases + listNodes[nodeId].numMissenseMutInCases==0)
		listNodes[nodeId].weightCases=0;
	//printf("%lf\n", listNodes[nodeId].weightCases);
    return -1;
}


int assignScorePrecalculated(FILE *fpPredefined)
{
char geneName[geneNameLen];
float weight;
int numSevereMutInCases, numMissenseInCases;
int controlCount;
float length;
totalLengthGenes=0;
	while(fscanf(fpPredefined,"%s %f %i %i %i %f\n", geneName, &weight, &numSevereMutInCases, &numMissenseInCases, &controlCount, &length)!=EOF)
	{
		for (int count=0; count<numNodes; count++)
		{
			if (strcmp(geneName, listNodes[count].nodeName)==0)
			{
				listNodes[count].numSevereMutInCases=numSevereMutInCases;
				listNodes[count].weightCases=weight;
				listNodes[count].numMissenseMutInCases=numMissenseInCases;
				listNodes[count].numSevereMutInControl=controlCount;
				listNodes[count].length=(int)length;
				totalLengthGenes=totalLengthGenes+(int)length;
				totalSevereMutInCases=totalSevereMutInCases+numSevereMutInCases;
				totalMissenseMutInCases=totalMissenseMutInCases+numMissenseInCases;
				totalNodesWithScoreAssigned++;
			///THE CONTROL MUTATIONS IS NOT ADDED YET (YOU SHOULD ADD IT)	
				allNodeMeanValue=allNodeMeanValue+weight;
			}
		}
	
	}



	
	allNodeMeanValue=(float)allNodeMeanValue/(float)totalNodesWithScoreAssigned;
	for (int count=0; count<numNodes; count++)
	{
		allNodesSTD=allNodesSTD+(listNodes[count].weightCases-allNodeMeanValue)*(listNodes[count].weightCases-allNodeMeanValue);
	}
	allNodesSTD=sqrt((float)allNodesSTD/(float)totalNodesWithScoreAssigned);



/*	while(fscanf(fpControl,"%s\t%i\n", geneName, &controlCount)!=EOF)
	{
		for (int count=0; count<numNodes; count++)
		{
			if (strcmp(geneName, listNodes[count].nodeName)==0)
			{
				//printf("added control %s %i\n", geneName,controlCount);
				listNodes[count].numSevereMutInControl=controlCount;
				//printf("added control %s %i\n", listNodes[count].nodeName, listNodes[count].weightControl);
			}
		}	
	}
*/
    return -1;
}


int assignScoreToBothControlandCases(FILE *fpCases, FILE *fpControl, FILE *fpGeneLen, FILE *filterFile, FILE *fpOutputGeneScore, bool filter)
{
    char geneName[geneNameLen];
    int numTruncatingControl;
    double variantScoreCases;
    char variantSubtype[20];
    int countTotal=0, randId;
    double len;
    double temp;
    srand(time(NULL));

	while(fscanf(fpCases, "%s\t%i\t%lf%s\n", geneName, &numTruncatingControl, &variantScoreCases, variantSubtype)!=EOF)
	{
		for (int count=0; count<numNodes; count++)
		{
			if (strcmp(geneName, listNodes[count].nodeName)==0 && (strcmp(variantSubtype,"3n-non-frameshifting")==0 || strcmp(variantSubtype,"frameshift")==0 || strcmp(variantSubtype,"nonsense")==0 || strcmp(variantSubtype,"splice")==0 || strcmp(variantSubtype,"splice-indel")==0 || strcmp(variantSubtype,"3n-non-frameshifting-stop")==0 || strcmp( variantSubtype,"frameshift-near-splice")==0  || strcmp(variantSubtype, "stop_gained")==0 || strcmp(variantSubtype,"splice_acceptor")==0 || strcmp(variantSubtype,"splice_donor")==0))
			{
				listNodes[count].numSevereMutInCases++;
				listNodes[count].weightCases=listNodes[count].weightCases+1;
				countTotal++;
				totalSevereMutInCases++;
			}else if(strcmp(geneName, listNodes[count].nodeName)==0 && strcmp(variantSubtype,"missense")==0)
			{
				listNodes[count].numMissenseMutInCases++;
				listNodes[count].weightCases=listNodes[count].weightCases+1;
				countTotal++;
				totalMissenseMutInCases++;
			}
		}		
	}

	//printf("%i %i\n", totalSevereMutInCases, totalMissenseMutInCases);

	while(fscanf(fpControl, "%s\t%i\n", geneName, &numTruncatingControl)!=EOF)
	{
		
		for (int count=0; count<numNodes; count++)
		{
			if (strcmp(geneName, listNodes[count].nodeName)==0)
			{
				//listNodes[count].numSevereMutInControl++;
				listNodes[count].weightControl=numTruncatingControl;
				totalSevereMutInControl++;
			}
		}		
	}
	while(fscanf(fpGeneLen, "%s\t%lf\n", geneName, &len)!=EOF)
	{
		for (int count=0; count<numNodes; count++)
		{
			if (strcmp(geneName, listNodes[count].nodeName)==0)
			{
				//listNodes[count].weightCases = ((double)listNodes[count].weightCases/(double)len)-(double)listNodes[count].weightControl/(double)len;
				listNodes[count].log_length=len;
				listNodes[count].length=len;
				totalLengthGenes=totalLengthGenes+len;
			}
		}
	}

/* IF WE DON"T HAVE THE LENGTH OF A GENE ASSUME THE LENGTH IS AVERGAGE OF LENGTHS WHICH IS 3300bp*/
	for (int count=0; count<numNodes; count++)
	{
		if (listNodes[count].log_length==0)
		{
			listNodes[count].log_length=3300;
			//listNodes[count].weightCases=((double)listNodes[count].weightCases/((double)listNodes[count].log_length));//+(double)listNodes[count].weightControl));
			//listNodes[count].weightCases = listNodes[count].weightCases-((double)listNodes[count].weightControl/(double)listNodes[count].log_length);
			listNodes[count].length=3300;
			totalLengthGenes=totalLengthGenes+3300;
		}
	}


    for (int count=0; count<numNodes; count++)
    {
        listNodes[count].prob=(double)listNodes[count].length/(double)totalLengthGenes;
        //printf("%lf %i\n", log(listNodes[count].prob), listNodes[count].numMissenseMutInCases);
        listNodes[count].weightCases=0;
        calNewProbValue(count);
	
    }
    
    // while go through the case ignore the filter
    
    if (filter==true)
    {
        while(fscanf(filterFile,"%s\n", geneName)!=EOF)
        {
            for (int count=0; count<numNodes; count++)
            {
                if (strcmp(geneName, listNodes[count].nodeName)==0)
                {
                    listNodes[count].weightCases=0;
                    listNodes[count].weightControl=1000;
                }
            }
        }
    }

    // AUKidding me?
    for (int count=0; count<numNodes; count++)
    {
        fprintf(fpOutputGeneScore,"%s %lf %i %i %i %i\n", listNodes[count].nodeName, listNodes[count].weightCases, listNodes[count].numSevereMutInCases, listNodes[count].numMissenseMutInCases, listNodes[count].weightControl, listNodes[count].length);
    }
	
    fclose(fpOutputGeneScore);
    //printf("%i\n", countTotal);
    return -1;
}


int createCoExpresionGeneHash(FILE *fp)
{
    srand((unsigned int)time(NULL));
    int hashId;
    coExpresGeneNum=0;
    int coExprId=0;
    char ensName[100];
    char geneName[geneNameLen];
	while (fscanf(fp, "%i\t%s\t%s\n", &coExprId, ensName, geneName)!=EOF)
	{
		coExpresGeneNum++;
		hashId=-1;
		for (int count=0; count<numNodes; count++)
		{
			if (strcmp(listNodes[count].nodeName, geneName)==0)
			{
				hashId=count;
			}
		} 
		strcpy(coExpresionGeneHashTable[coExprId].geneName, geneName);
		coExpresionGeneHashTable[coExprId].hashId=coExprId;
		coExpresionGeneHashTable[coExprId].nodeId=hashId;
	}
    return -1;
}


bool includesTheNode(int nodeId, int *listNodes, int sizeList)
{
	for (int count=0; count<sizeList; count++)
	{
		if (listNodes[count]==nodeId)
			return true;
	}
return false;
}

bool isSubGraphConnectedComponenti_WithCoExpr(int *listSubgraphNodes, int sizeSubgraph)
{
	int *listNodesCovered;
	int indexQueue, endOfQueue;
	listNodesCovered= (int *) malloc(sizeSubgraph * sizeof(int));
	listNodesCovered[0]=listSubgraphNodes[0];

	indexQueue=0;
	endOfQueue=1;

	do{
			for (int count2=0; count2<listNodes[listNodesCovered[indexQueue]].degree; count2++)
			{
				if (coExpresionMatrix[listNodesCovered[indexQueue]][listNodes[listNodesCovered[indexQueue]].neighbours[count2]]>minCoExpresThreshold)
				{
					if (includesTheNode(listNodes[listNodesCovered[indexQueue]].neighbours[count2], listNodesCovered, endOfQueue)==false && includesTheNode(listNodes[listNodesCovered[indexQueue]].neighbours[count2], listSubgraphNodes, sizeSubgraph)==true)
                                        {
						listNodesCovered[endOfQueue]=listNodes[listNodesCovered[indexQueue]].neighbours[count2];
						endOfQueue++;
					}
				}
			}
			indexQueue++;


	}while(indexQueue!=endOfQueue);

	free(listNodesCovered);
if (endOfQueue==sizeSubgraph)
	return true;
else return false;

}





bool isSubGraphConnectedComponent(int *listSubgraphNodes, int sizeSubgraph)
{
	int *listNodesCovered;
	int indexQueue, endOfQueue;
	listNodesCovered= (int *) malloc(sizeSubgraph * sizeof(int));
	listNodesCovered[0]=listSubgraphNodes[0];
	
	indexQueue=0;
	endOfQueue=1;

	do{
			for (int count2=0; count2<listNodes[listNodesCovered[indexQueue]].degree; count2++)
			{
				if (includesTheNode(listNodes[listNodesCovered[indexQueue]].neighbours[count2], listNodesCovered, endOfQueue)==false && includesTheNode(listNodes[listNodesCovered[indexQueue]].neighbours[count2], listSubgraphNodes, sizeSubgraph)==true)
				{
					listNodesCovered[endOfQueue]=listNodes[listNodesCovered[indexQueue]].neighbours[count2];
					endOfQueue++;
				} 	
			}
			indexQueue++;	


	}while(indexQueue!=endOfQueue);

if (endOfQueue==sizeSubgraph)
	return true;
else return false;
	
}
/*
int main(int argv, char *argc[])
{
	FILE *fp=fopen(argc[1],"r");
	FILE *fp2=fopen(argc[2],"r");
	FILE *fp3=fopen(argc[3],"r");
	FILE *fp4=fopen(argc[4],"r");
	FILE *fp5=fopen(argc[5],"r");
	FILE *fp6=fopen(argc[6],"r");
	createPPI_Graph(fp);
	assignScoreToBothControlandCases(fp2, fp3, fp4);
	createCoExpresionGeneHash(fp5);	
	createCoExpresionMatix(fp6);	
}*/
