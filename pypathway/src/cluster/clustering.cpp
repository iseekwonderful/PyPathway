#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "PPI_Graph.h"
#include "clustering.h"
#include <time.h>
#include <unistd.h>


//0.467581 0.16842
float minAvgExpr=0.415;
float minAvgExpr2=0.01;
//float minAvgEdgeDensity=0.116734;
float minAvgEdgeDensity=0.085;
int upperLimitSize; // we don't want clusters bigger than this size (it is an upper limit)
int lowerLimitSize;
float minAvgExprPerSize[100];
float minAvgEdgeDensityPerSize[100];
FILE* output;

const int maxClusterSize=50000;
int minClusterWeight;
typedef struct clustersSelected{
	int nodeId[200];
	//int nodeIdCount[200];
	int sizeCluster;
	float totalScore;//-log(p) : for each set of nodes you calculate it 
	float seedScore; // thr -log(P) score form seeds (summation of -log(p))
	float averageCoexpresion;//average pairwise coexpresion
	float averageEdgeDensity;
	
	int numSevereMutInCases;
	int numMissenseMutInCases;
	int numServeMutInControl;
	bool used;
}clustersSelected;

typedef struct adjClusterList{
	int *adjClusterIds;
	int numberAdjClusters;
}adjClusterList;

adjClusterList *clusterGraphAdjRep;

int **clusterGraphMatrixRep;

clustersSelected listClusterSelected[maxClusterSize];
int totalClusters;
char potNewPath[100][geneNameLen];


float clusMaxScore=0;
clustersSelected *bestCluster;
float pathAlpha;
float highestScorePath[10]; // highestScorePath[LengthPath][editDistance]
int copyClusToAnotherClus(clustersSelected *, clustersSelected *);
int greedyIncremeant(clustersSelected *);
int greedyRemoveNodes(clustersSelected *);
int localSearch(clustersSelected *);

float calAvgCoExpr(clustersSelected *tempCluster)
{

int totalGenes=0, repeatedGene=0;
float sumCoExpr=0;



        for (int count1=0; count1<tempCluster->sizeCluster; count1++)
        {
                for (int count2=0; count2<tempCluster->sizeCluster; count2++)
                {
                        if (count1!=count2)
                        {
                                sumCoExpr=sumCoExpr+coExpresionMatrix[tempCluster->nodeId[count1]][tempCluster->nodeId[count2]];
                        }
                }

        }
        if ((float)sumCoExpr/(float)(tempCluster->sizeCluster*(tempCluster->sizeCluster-1))>1)
                printf("EROROROROROROORORORORORRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n");
        return (float)sumCoExpr/(float)(tempCluster->sizeCluster*(tempCluster->sizeCluster-1));
}





float calAvgEdgeDensity(clustersSelected *tempCluster)
{
int totalGenes=0, repeatedGene=0;
float sumEdges=0;


        for (int count1=0; count1<tempCluster->sizeCluster; count1++)
        {
                for (int count2=0; count2<tempCluster->sizeCluster; count2++)
                {

                        if (count1!=count2)
                        {
                                sumEdges=sumEdges+isConnectedPPI(tempCluster->nodeId[count1], tempCluster->nodeId[count2]);
                        }
                }
        }
return (float)sumEdges/(float)(tempCluster->sizeCluster*(tempCluster->sizeCluster-1));

}


int calNumSevereMutInCases(clustersSelected *tempCluster)
{
int totalSevereMut=0;
	for (int count=0; count<tempCluster->sizeCluster; count++)
	{
		totalSevereMut=totalSevereMut+listNodes[tempCluster->nodeId[count]].numSevereMutInCases;
	}
return totalSevereMut;
}



int calNumMissenseMutIncases(clustersSelected *tempCluster)
{
int totalMissenseMut=0;
	for (int count=0; count<tempCluster->sizeCluster; count++)
	{
		totalMissenseMut=totalMissenseMut+listNodes[tempCluster->nodeId[count]].numMissenseMutInCases;
	}
return totalMissenseMut;
}




int calSereveMutInControl(clustersSelected *tempCluster)
{
int totalSevereMutInControl=0;
	for (int count=0; count<tempCluster->sizeCluster; count++)
	{
		totalSevereMutInControl=totalSevereMutInControl+listNodes[tempCluster->nodeId[count]].numSevereMutInControl;
	}
return totalSevereMutInControl;
}





float calTotalScore(clustersSelected *tempCluster)
{
float returnValue=0;
float avgTotalScore=0;
for (int count=0; count<tempCluster->sizeCluster; count++)
{
	avgTotalScore=avgTotalScore+listNodes[tempCluster->nodeId[count]].weightCases;
}

avgTotalScore=(float)avgTotalScore/(float)tempCluster->sizeCluster;
returnValue = avgTotalScore - allNodeMeanValue;
returnValue = (float)returnValue/(float)allNodesSTD;

return returnValue*sqrt(tempCluster->sizeCluster); 



}


int outputCluster2(clustersSelected *clus)
{
int totalClusterLength=0;
if (clus->sizeCluster<lowerLimitSize  || clus->sizeCluster>upperLimitSize)
	return 0;
fprintf(output, "%i\n", clus->sizeCluster);	
	for (int count=0; count<clus->sizeCluster; count++)
	{
		totalClusterLength=totalClusterLength+listNodes[clus->nodeId[count]].length;
        PPI_Node n = listNodes[clus->nodeId[count]];
        fprintf(output, "%s, %i, %i, %i, %f, %f, %i\n", n.nodeName, n.numSevereMutInCases, n.numMissenseMutInCases,
               n.numSevereMutInControl, n.prob, n.weightCases, n.weightControl);
        for (int j = 0; j < clus->sizeCluster; j ++) {
            if (j == count) {
                continue;
            }
            PPI_Node n2 = listNodes[clus->nodeId[j]];
            fprintf(output, "%s, %s, %f\n", n.nodeName, n2.nodeName, coExpresionMatrix[n.nodeId][n2.nodeId]);
        }
    }
fprintf(output, "%i %i %i %i %f %f %f\n", totalClusterLength, clus->numMissenseMutInCases, clus->numSevereMutInCases, clus->numServeMutInControl, clus->averageCoexpresion, clus->averageEdgeDensity, clus->totalScore);
return 1;
}


clustersSelected *createATempCluster(int clusterSize, char** tempListNodeName) // Creater a new cluster with the nodes in listNodeName if it satisfies the conditions 
{
clustersSelected *tempCluster;
tempCluster = (clustersSelected *) malloc(sizeof(clustersSelected));

	for (int count=0; count<clusterSize; count++)
	{
		for (int count2=0; count2<numNodes; count2++)
		{
			if (strcmp(listNodes[count2].nodeName, tempListNodeName[count])==0)
			{
				tempCluster->nodeId[count]=count2;
			}
		}
	}

	tempCluster->sizeCluster=clusterSize;
	tempCluster->averageCoexpresion=calAvgCoExpr(tempCluster);
	tempCluster->averageEdgeDensity=calAvgEdgeDensity(tempCluster);
	tempCluster->numSevereMutInCases=calNumSevereMutInCases(tempCluster);
	tempCluster->numMissenseMutInCases=calNumMissenseMutIncases(tempCluster);
	tempCluster->totalScore=calTotalScore(tempCluster);
	tempCluster->numServeMutInControl=calSereveMutInControl(tempCluster);
	tempCluster->used=false;
return tempCluster;
}


int copyClusterToList(clustersSelected *clus, int idToAdd)
{


	listClusterSelected[idToAdd].sizeCluster=clus->sizeCluster;
	listClusterSelected[idToAdd].averageCoexpresion=clus->averageCoexpresion;
	listClusterSelected[idToAdd].averageEdgeDensity=clus->averageEdgeDensity;
	listClusterSelected[idToAdd].numSevereMutInCases=clus->numSevereMutInCases;
	listClusterSelected[idToAdd].numMissenseMutInCases=clus->numMissenseMutInCases;
	listClusterSelected[idToAdd].totalScore=clus->totalScore;
	listClusterSelected[idToAdd].numServeMutInControl=clus->numServeMutInControl;
	listClusterSelected[idToAdd].seedScore=clus->seedScore;
	for (int count=0; count<clus->sizeCluster; count++)
	{
		listClusterSelected[idToAdd].nodeId[count]=clus->nodeId[count];
	}
    return 0;
}



bool sameClusters(clustersSelected *clus1, int clusterSize, clustersSelected *clus2) //Checks if the a given cluster clus1 is the same as the clus2 when both have the same size clusterSize
{
int numGeneMatch=0;
        for (int count=0; count<clusterSize; count++)
        {
                for (int count2=0; count2<clusterSize; count2++)
                {
                        if (clus1->nodeId[count]==clus2->nodeId[count2])
                       	{
                                numGeneMatch++;
                        }
                }
        }
if (numGeneMatch==clusterSize)
        return true;
else return false;

}


bool clusterHasBeenAddedBefore(int clusterSize, clustersSelected *clus1)
{
if (totalClusters==0)
	return false;

	for (int count=0; count<totalClusters; count++)
	{
		if ((clus1->sizeCluster == listClusterSelected[count].sizeCluster) && sameClusters(clus1, clus1->sizeCluster, &(listClusterSelected[count])))
			return true;	
	}	
return false;
}



float minCoExprValueInClus(clustersSelected *clus)
{
float minCoExprValue=1;
	for (int count=0; count<clus->sizeCluster; count++)
	{
		for (int count2=count+1; count2<clus->sizeCluster; count2++)
		{
			if (minCoExprValue>coExpresionMatrix[clus->nodeId[count]][clus->nodeId[count2]])
			{
				minCoExprValue=coExpresionMatrix[clus->nodeId[count]][clus->nodeId[count2]];
			}	
		}
	}
return minCoExprValue;
}



bool isValidCluster(clustersSelected *clus)
{
	if (clus->numServeMutInControl<minClusterWeight && clus->averageEdgeDensity>minAvgEdgeDensity && clus->averageCoexpresion>minAvgExpr && isSubGraphConnectedComponenti_WithCoExpr(clus->nodeId, clus->sizeCluster)==true && clus->sizeCluster<=upperLimitSize && minCoExprValueInClus(clus)>=minAvgExpr2)
	{
		return true;
	}
return false;
}	

int readInitClusters(FILE *fp, int numPaths, int pathLength)
{
float score;
char geneName[geneNameLen];
float avgCoExprValue, avgEdgeDensity, FinalScore;
char **potNewPath;
clustersSelected *tempCluster;
int startClusterId=totalClusters;
int tempInt;
int tempFloat;
startClusterId=0;

potNewPath = (char **) malloc(100*sizeof(char *));
	for (int count=0; count<100; count++)
	{
		potNewPath[count]=(char *) malloc(geneNameLen*sizeof(char *));
	}
        for (int countP=startClusterId; countP<startClusterId+numPaths; countP++)
        {
                for (int countL=0; countL<pathLength; countL++)
                {
                        fscanf(fp,"%f %s\n", &score, geneName);
                        strcpy(potNewPath[countL], geneName);
                }
		fscanf(fp,"recolor %i\n", &tempInt);
		fscanf(fp,"%i %i %i %f\n",&tempInt, &tempInt, &tempInt, &tempFloat);
                fscanf(fp,"Avg CoExpr:%f %f %f\n", &avgCoExprValue, &avgEdgeDensity, &FinalScore);
		if (highestScorePath[pathLength]<FinalScore)
			highestScorePath[pathLength]=FinalScore;
        	tempCluster=createATempCluster(pathLength, potNewPath);
		tempCluster->seedScore=FinalScore;
		tempCluster->used=false;
		if (isValidCluster(tempCluster)==true &&  clusterHasBeenAddedBefore(pathLength, tempCluster)==false)
		{
			// printf("%s\n", "This is isValidCluster");
			copyClusterToList(tempCluster, totalClusters);			
			totalClusters++;
			free(tempCluster);
		}
		else
		{
			// printf("%s\n", "WTF invalid cluster");
			free(tempCluster);
		}
        }
    return 0;
}



clustersSelected *mergeClus (clustersSelected* clus1, clustersSelected *clus2)
{
clustersSelected *tempClust;
tempClust = (clustersSelected*) malloc(sizeof(clustersSelected));
tempClust->sizeCluster=0;
bool matched;
	for (int count=0; count<clus1->sizeCluster; count++)
	{
		tempClust->nodeId[tempClust->sizeCluster]=clus1->nodeId[count];
		tempClust->sizeCluster++;
	} 
	for (int count2=0; count2<clus2->sizeCluster; count2++)
	{
		matched=false;
		for (int count=0; count<clus1->sizeCluster; count++)
		{
			if (clus1->nodeId[count]==clus2->nodeId[count2])
				matched=true;
		}
		if (matched==false)
		{
			tempClust->nodeId[tempClust->sizeCluster]=clus2->nodeId[count2];
			tempClust->sizeCluster++;
		}
	}
	
	tempClust->numMissenseMutInCases=calNumMissenseMutIncases(tempClust);
	tempClust->numSevereMutInCases=calNumSevereMutInCases(tempClust);
	tempClust->numServeMutInControl=calSereveMutInControl(tempClust);
	tempClust->averageCoexpresion=calAvgCoExpr(tempClust);
	tempClust->averageEdgeDensity=calAvgEdgeDensity(tempClust);
	tempClust->totalScore=calTotalScore(tempClust);
tempClust->used=false;
return tempClust;
}


int readPathFiles(FILE *fp)
{
int numPaths=0;
char fileName[100];
FILE *fpInputPaths;
int pathLength;
        while(fscanf(fp,"%s %i %i\n", fileName, &numPaths, &pathLength)!=EOF)
        {
                // printf("%s\n", fileName);
                fpInputPaths=fopen(fileName, "r");
                readInitClusters(fpInputPaths, numPaths, pathLength);
        }
    return 0;
}


int createGraphOfPaths()
{
        clusterGraphMatrixRep=(int **)malloc(totalClusters * sizeof(int*));
        clustersSelected *tempNewClus;
        int degree=0;
      	clusterGraphAdjRep = (adjClusterList *) malloc(sizeof (adjClusterList)*totalClusters);
        for (int count=0; count<totalClusters; count++)
        {
                clusterGraphMatrixRep[count]=(int *) malloc(totalClusters*sizeof(int));
                for (int count1=0; count1<totalClusters; count1++)
                        clusterGraphMatrixRep[count][count1]=0;
        }


        for (int count=0; count<totalClusters; count++)
        {
        degree=0;
                for (int count1=0; count1<totalClusters; count1++)
                {
                        if (listClusterSelected[count].used==false && listClusterSelected[count1].used==false)
                        {
                                tempNewClus=mergeClus(&(listClusterSelected[count]), &(listClusterSelected[count1]));
                                if ((tempNewClus->sizeCluster < listClusterSelected[count1].sizeCluster+listClusterSelected[count].sizeCluster) && isValidCluster(tempNewClus)==true)
                                        {
                                                clusterGraphMatrixRep[count][count1]=1;
                                                clusterGraphMatrixRep[count1][count]=1;
                                                degree++;
                                        }
				free(tempNewClus);
                        }
                }
                        clusterGraphAdjRep[count].numberAdjClusters=0;
                        clusterGraphAdjRep[count].adjClusterIds=(int *) malloc((degree)*sizeof(int));
                for (int count1=0; count1<totalClusters; count1++)
                {
                        if (listClusterSelected[count].used==false && listClusterSelected[count1].used==false)
                        {
                                
                                tempNewClus=mergeClus(&(listClusterSelected[count]), &(listClusterSelected[count1]));
				if ((tempNewClus->sizeCluster < listClusterSelected[count1].sizeCluster+listClusterSelected[count].sizeCluster) && isValidCluster(tempNewClus)==true)
                                        {
                                                       	clusterGraphAdjRep[count].adjClusterIds[clusterGraphAdjRep[count].numberAdjClusters] = count1;
                                                        clusterGraphAdjRep[count].numberAdjClusters++;
							if (clusterGraphAdjRep[count].numberAdjClusters>degree)
								printf("ERORORORORORORO3 \n");
                                        }
				free(tempNewClus);
                        }
                }
        }
    return 0;
}


int localSearchProcedure(clustersSelected *cluster)
{
	
float clusScore=0;
	do
	{
		clusScore=cluster->totalScore;
		
		greedyIncremeant(cluster);
		greedyRemoveNodes(cluster);	
		localSearch(cluster);
	}while(cluster->totalScore>clusScore);
    return 0;
}

int randomWalkInGraph(int nodeId, clustersSelected *cluster)
{
clustersSelected *tempClus;
int potClusIdCanMergeToClus[5000];
int potClusIdCanMergeToClusCount=0;
int randomId;

	for (int count=0; count<clusterGraphAdjRep[nodeId].numberAdjClusters; count++)
	{
		tempClus = mergeClus(cluster,  &(listClusterSelected[clusterGraphAdjRep[nodeId].adjClusterIds[count]]));
		if (!clusterHasBeenAddedBefore(tempClus->sizeCluster, tempClus) && isValidCluster(tempClus) && tempClus->totalScore > cluster->totalScore)
		{
			potClusIdCanMergeToClus[potClusIdCanMergeToClusCount]=clusterGraphAdjRep[nodeId].adjClusterIds[count];
			potClusIdCanMergeToClusCount++;	
		}
		free(tempClus);
	}

if (potClusIdCanMergeToClusCount>0)
{
	randomId = rand()%potClusIdCanMergeToClusCount;
	tempClus = mergeClus(cluster,  &(listClusterSelected[potClusIdCanMergeToClus[randomId]]));
	randomWalkInGraph(potClusIdCanMergeToClus[randomId], tempClus);
	free(tempClus);
}else{

		if (cluster->sizeCluster>=lowerLimitSize && cluster->sizeCluster<=upperLimitSize)
		{
			localSearchProcedure(cluster);
			outputCluster2(cluster);
		} 
}		

	return 0;
}


int weightedRandomWalkInGraph(int nodeId, clustersSelected *cluster)
{
clustersSelected *tempClus;
int potClusIdCanMergeToClus[5000];
int potClusIdCanMergeToClusCount=0;
float potClusIdCanMergeToClusWeight[5000];
float totalWeights=0;
float randomWeight=0;
int randomId;

	for (int count=0; count<clusterGraphAdjRep[nodeId].numberAdjClusters; count++)
	{
		tempClus = mergeClus(cluster,  &(listClusterSelected[clusterGraphAdjRep[nodeId].adjClusterIds[count]]));
		if (!clusterHasBeenAddedBefore(tempClus->sizeCluster, tempClus) && isValidCluster(tempClus) && tempClus->totalScore > cluster->totalScore)
		{
			potClusIdCanMergeToClus[potClusIdCanMergeToClusCount]=clusterGraphAdjRep[nodeId].adjClusterIds[count];
			potClusIdCanMergeToClusWeight[potClusIdCanMergeToClusCount]=tempClus->totalScore;
			totalWeights=totalWeights+tempClus->totalScore;
			potClusIdCanMergeToClusCount++;	
		}
		free(tempClus);
	}

if (potClusIdCanMergeToClusCount>0)
{
	randomWeight=rand()%(int(floor(totalWeights)));
	randomId=0;
	while (randomWeight>0)
	{
		randomWeight=randomWeight-potClusIdCanMergeToClusWeight[randomId];
		randomId++;
	}
	randomId--;
	tempClus = mergeClus(cluster,  &(listClusterSelected[potClusIdCanMergeToClus[randomId]]));
	randomWalkInGraph(potClusIdCanMergeToClus[randomId], tempClus);
	free(tempClus);
}else{
		outputCluster2(cluster);	
		if (cluster->totalScore > clusMaxScore && cluster->sizeCluster>=lowerLimitSize && cluster->sizeCluster<=upperLimitSize)
		{
			clusMaxScore=cluster->totalScore;
			copyClusToAnotherClus(bestCluster, cluster);
		} 
}
    return 0;
}

	

int randomConnectedComponents(int randId)
{
int count=0;
srand(time(NULL)+randId);
for (int count2=0; count2<500; count2++)
{
	count = rand()%totalClusters;		
		{
			randomWalkInGraph(count, &listClusterSelected[count]);
		}
}
	return 0;
}

bool findBestSetToMerge(int *clusId1, int *clusId2)
{

clustersSelected *tempNewClus;
float maxScore=0;
bool nothingGood=false;
for (int count=0; count < totalClusters; count++)
{
	if (maxScore<listClusterSelected[count].totalScore)
	{
		maxScore=listClusterSelected[count].totalScore;
	}
}

for (int count1=0; count1 < totalClusters; count1++)
{

if (isSubGraphConnectedComponenti_WithCoExpr(listClusterSelected[count1].nodeId, listClusterSelected[count1].sizeCluster)==false)
	printf("NOT CONNECTED. HOW COME??? Double check. L573\n");

	for (int count2=count1+1; count2 < totalClusters; count2++)
	{
		tempNewClus = mergeClus(&(listClusterSelected[count1]), &(listClusterSelected[count2]));
		if ((tempNewClus->sizeCluster < listClusterSelected[count1].sizeCluster+listClusterSelected[count2].sizeCluster) && tempNewClus->sizeCluster > listClusterSelected[count1].sizeCluster && tempNewClus->sizeCluster > listClusterSelected[count2].sizeCluster && isValidCluster(tempNewClus)==true)
		{
			if (maxScore<tempNewClus->totalScore)
			{
				nothingGood=true;
				*clusId1=count1;
				*clusId2=count2;
				maxScore=tempNewClus->totalScore;
			}
		}
		free(tempNewClus);
	}
}

return nothingGood;
}

int outputCluster(int clusterId)
{
int totalClusterLength=0;
	
	for (int count=0; count<listClusterSelected[clusterId].sizeCluster; count++)
	{
		totalClusterLength=totalClusterLength+listNodes[listClusterSelected[clusterId].nodeId[count]].length;
        PPI_Node n = listNodes[listClusterSelected[clusterId].nodeId[count]];
		printf("%s, %i, %i, %i\n", n.nodeName, n.numSevereMutInCases, n.numMissenseMutInCases, n.numSevereMutInControl);
	}
printf("%i %i %i %i %f %f %f\n", totalClusterLength, listClusterSelected[clusterId].numMissenseMutInCases,listClusterSelected[clusterId].numSevereMutInCases, listClusterSelected[clusterId].numServeMutInControl, listClusterSelected[clusterId].averageCoexpresion, listClusterSelected[clusterId].averageEdgeDensity, listClusterSelected[clusterId].totalScore);
    return 0;
}



int greedySearch()
{
int clusId1, clusId2;
clustersSelected *tempNewClus;

while (findBestSetToMerge(&clusId1, &clusId2))
{
	tempNewClus = mergeClus(&(listClusterSelected[clusId1]), &(listClusterSelected[clusId2]));
	copyClusterToList(tempNewClus,totalClusters);
	totalClusters++;
	outputCluster(totalClusters-1);
	copyClusToAnotherClus(bestCluster, &(listClusterSelected[totalClusters-1]));
}
    return 0;
}


bool nodeInCluster(clustersSelected *clus, int nodeId)
{

	for (int count=0; count<clus->sizeCluster; count++)
	{
		if (nodeId==clus->nodeId[count])
			return true;
	}
return false;
}


clustersSelected *swapNodeInClus(clustersSelected *clus, int newNodeId, int oldNodeIndex)
{
clustersSelected *tempClus;
tempClus = (clustersSelected *) malloc(sizeof(clustersSelected));
tempClus->sizeCluster=clus->sizeCluster;

for (int count=0; count<clus->sizeCluster; count++)
{
	tempClus->nodeId[count]=clus->nodeId[count];
}

	tempClus->nodeId[oldNodeIndex]=newNodeId;
	tempClus->numMissenseMutInCases=calNumMissenseMutIncases(tempClus);
	tempClus->numSevereMutInCases=calNumSevereMutInCases(tempClus);
	tempClus->numServeMutInControl=calSereveMutInControl(tempClus);
	tempClus->averageCoexpresion=calAvgCoExpr(tempClus);
	tempClus->averageEdgeDensity=calAvgEdgeDensity(tempClus);
	tempClus->totalScore=calTotalScore(tempClus);
return tempClus;
}

clustersSelected *addNodeToCluster(clustersSelected *clus,  int newNodeId)
{
clustersSelected *tempClus;
tempClus = (clustersSelected *) malloc(sizeof(clustersSelected));
tempClus->sizeCluster=clus->sizeCluster+1;

for (int count=0; count<clus->sizeCluster; count++)
{
	tempClus->nodeId[count]=clus->nodeId[count];
}
	tempClus->nodeId[clus->sizeCluster]=newNodeId;
	

	tempClus->numMissenseMutInCases=calNumMissenseMutIncases(tempClus);
	tempClus->numSevereMutInCases=calNumSevereMutInCases(tempClus);
	tempClus->numServeMutInControl=calSereveMutInControl(tempClus);
	tempClus->averageCoexpresion=calAvgCoExpr(tempClus);
	tempClus->averageEdgeDensity=calAvgEdgeDensity(tempClus);
	tempClus->totalScore=calTotalScore(tempClus);
return tempClus;
	
}

clustersSelected *removeNodeFromClus(clustersSelected *clus, int nodeIdToRemove)
{
int index=0;
clustersSelected *tempClus;
tempClus = (clustersSelected *) malloc(sizeof(clustersSelected));
tempClus->sizeCluster=clus->sizeCluster-1;
for (int count=0; count<clus->sizeCluster; count++)
{
	if (clus->nodeId[count]!=nodeIdToRemove)
	{
		tempClus->nodeId[index]=clus->nodeId[count];
		index++;
	}
	
}

	tempClus->numMissenseMutInCases=calNumMissenseMutIncases(tempClus);
	tempClus->numSevereMutInCases=calNumSevereMutInCases(tempClus);
	tempClus->numServeMutInControl=calSereveMutInControl(tempClus);
	tempClus->averageCoexpresion=calAvgCoExpr(tempClus);
	tempClus->averageEdgeDensity=calAvgEdgeDensity(tempClus);
	tempClus->totalScore=calTotalScore(tempClus);
return tempClus;


}



int copyClusToAnotherClus(clustersSelected *clus, clustersSelected *clus2)
{
	clus->sizeCluster=clus2->sizeCluster;
	for (int count=0; count<clus->sizeCluster; count++)
	{
		clus->nodeId[count]=clus2->nodeId[count];
	}
	
	clus->numMissenseMutInCases=clus2->numMissenseMutInCases;
	clus->numSevereMutInCases=clus2->numSevereMutInCases;
	clus->numServeMutInControl=clus2->numServeMutInControl;
	clus->averageCoexpresion=clus2->averageCoexpresion;
	clus->averageEdgeDensity=clus2->averageEdgeDensity;
	clus->totalScore=clus2->totalScore;

    return 0;
}



bool repeation(clustersSelected *clus)
{
	for (int count=0; count<clus->sizeCluster; count++)
	{
		for (int count2=count+1; count2<clus->sizeCluster; count2++)
		{
			if (clus->nodeId[count]==clus->nodeId[count2])
				return true;
		}
	}
return false;
}




int greedyIncremeant(clustersSelected *clus)
{
clustersSelected *tempClus;
float bestScore=0;
int bestNewNode=0;
for (int count2=0; count2<10; count2++)
{
	bestScore=0;
	for (int count=0; count<numNodes; count++)
	{
		if (listNodes[count].weightCases>0 && nodeInCluster(clus, count)==false)
		{
			tempClus=addNodeToCluster(clus, count);
			if (isValidCluster(tempClus)==true && tempClus->totalScore>clus->totalScore)
			{
					if (tempClus->totalScore> bestScore)
					{
						bestScore=tempClus->totalScore;
						bestNewNode=count;
					}
			}
			free(tempClus);
		}
	}

	if (bestScore>clus->totalScore)
	{
	tempClus=addNodeToCluster(clus,bestNewNode);
	copyClusToAnotherClus(clus, tempClus);
	}
}
    return 0;
}

int greedyRemoveNodes(clustersSelected *clus)
{
float bestScore=0;
int bestNodeToRemove=0;
clustersSelected *tempClus;
	for (int count2=0; count2<10; count2++)
	{
		bestScore=0;
		for (int count=0; count<clus->sizeCluster; count++)
		{
			tempClus=removeNodeFromClus(clus, clus->nodeId[count]);
				if (isValidCluster(tempClus)==true && tempClus->totalScore>clus->totalScore && tempClus->sizeCluster>=lowerLimitSize)
				{
					if (bestScore<tempClus->totalScore)
					{
						bestScore=tempClus->totalScore;
						bestNodeToRemove=clus->nodeId[count];
					}
				}
	

		}
		if (bestScore>0)
		{
			tempClus=removeNodeFromClus(clus, bestNodeToRemove);
			copyClusToAnotherClus(clus, tempClus);
		}
	}
    return 0;
}

int localSearch(clustersSelected *clus)
{
clustersSelected *tempClus;
bool nodeAdded;
float bestScore=0;
int bestNodeToAdd=0;
int bestNodeToRemove=0;//Becareful: It is not the nodeId but the index of the nodeId in the Clus
for (int countIt=0; countIt<10; countIt++)
{
bestScore=0;
	for (int count=0; count<numNodes; count++)
	{
	nodeAdded=false;
		if (listNodes[count].weightCases>0 && nodeInCluster(clus, count)==false)
		{
			for (int count2=0; count2<clus->sizeCluster; count2++)
			{
				tempClus=swapNodeInClus(clus, count, count2);

					if (isValidCluster(tempClus)==true && tempClus->totalScore>clus->totalScore)
					{
						if (bestScore<tempClus->totalScore)
						{
							bestScore=tempClus->totalScore;
							bestNodeToAdd=count;
							bestNodeToRemove=count2;
						}
					
					}	
				free(tempClus);
			}
		}
	}

if(bestScore>0)
{
	tempClus=swapNodeInClus(clus, bestNodeToAdd, bestNodeToRemove);
	copyClusToAnotherClus(clus, tempClus);
}else return 0;
}
    return 0;
}


int markPathsNotToUse()
{

for (int count=0; count<totalClusters; count++)
{
	if (highestScorePath[listClusterSelected[count].sizeCluster]*pathAlpha>listClusterSelected[count].seedScore)
		listClusterSelected[count].used=true;
}
    return 0;

}

extern "C" int clustering(char* p, char* c, char* h, char* e, char* s, int m,
	int l, int u, char* aaa, char* i, char* minCoExpr, char* avgCoExpr, 
	char* avgDensity, char* outputFile)
{
	// printf("Aaaa is %s\n", aaa);
	bestCluster = (clustersSelected *) malloc(sizeof(clustersSelected));
	FILE *fp1, *fp2, *fp3, *fp4, *fp5, *fp6;
	int randomNum;
	int countNumParamters=0;
	fp1=fopen(p,"r");
	fp2=fopen(c,"r");
	fp3=fopen(h,"r");
	fp4=fopen(e,"r");
	fp5=fopen(s,"r");
	minClusterWeight = m;
	lowerLimitSize = l;
	upperLimitSize = u;
	pathAlpha = atof(aaa);
	randomNum=atoi(i);
	minAvgExpr2 = atof(minCoExpr);
	minAvgExpr = atof(avgCoExpr);
	minAvgEdgeDensity = atof(avgDensity);

	output = fopen(outputFile, "w");
	// printf("m:%i\nl:%i\nu:%i\na:%f\ni: %i\n", minClusterWeight, lowerLimitSize, upperLimitSize,
           // pathAlpha, randomNum);
	// exit(0);
	srand(time(NULL)+randomNum);
	createPPI_Graph(fp1);
        assignScorePrecalculated(fp2);
        createCoExpresionGeneHash(fp3);
	createCoExpresionMatix(fp4);
	readPathFiles(fp5);
	markPathsNotToUse();
	createGraphOfPaths();
	randomConnectedComponents(randomNum);
}
int main(int argv, char *argc[])
{
	bestCluster = (clustersSelected *) malloc(sizeof(clustersSelected));
	FILE *fp1, *fp2, *fp3, *fp4, *fp5, *fp6;
	int randomNum;
	int countNumParamters=0;
	/*fp1=fopen(argv[1],"r");//PPI network
	fp2=fopen(argv[2],"r");//cases
	fp3=fopen(argv[3],"r");//gene coexpresion name
	fp4=fopen(argv[4],"r");//gene coexpresion matrix
	fp5=fopen(argv[5],"r");// set of paths and their lengths;                
	fp6=fopen(argv[6],"r");// ESP/Control set of mutations
	minClusterWeight=atoi(argv[7]);
	lowerLimitSize=atoi(argv[8]);
	upperLimitSize=atoi(argv[9]);
	pathAlpha=atof(argv[10]);
	randomNum=atoi(argv[11]);

	minAvgExpr
	minAvgExpr2
	minAvgEdgeDensity
*/
	for (int count=0; count<argv; count++)
	{
		if (strcmp(argc[count], "-p")==0) //PPI
		{
			fp1=fopen(argc[count+1],"r");
			countNumParamters++;
		}
		if (strcmp(argc[count], "-c")==0)// Cases
		{
			fp2=fopen(argc[count+1],"r");
			countNumParamters++;			
		}
		if (strcmp(argc[count], "-h")==0) // gene coexpression hash
		{
			fp3=fopen(argc[count+1],"r");
			countNumParamters++;
		}
		if (strcmp(argc[count], "-e")==0) //
		{
			fp4=fopen(argc[count+1],"r");
			countNumParamters++;
		}
		if (strcmp(argc[count], "-s")==0) // Seed files
		{
			fp5=fopen(argc[count+1],"r");
			countNumParamters++;
		}
		if (strcmp(argc[count], "-m")==0) //min cluster control weight
		{
			minClusterWeight=atoi(argc[count+1]);
			countNumParamters++;
		}
		if (strcmp(argc[count], "-l")==0) //lowerbound size 
		{
			lowerLimitSize=atoi(argc[count+1]);
			countNumParamters++;
		}
		if (strcmp(argc[count], "-u")==0)
		{
			upperLimitSize=atoi(argc[count+1]);
			countNumParamters++;
		}
		if (strcmp(argc[count], "-a")==0)
		{
			pathAlpha=atof(argc[count+1]);
			countNumParamters++;
		}
		if (strcmp(argc[count], "-i")==0)
		{
			randomNum=atoi(argc[count+1]);
			countNumParamters++;
		}
		if (strcmp(argc[count], "-minCoExpr")==0)
		{
			minAvgExpr2=atof(argc[count+1]);
		}
		if (strcmp(argc[count], "-avgCoExpr")==0)
		{
			minAvgExpr=atof(argc[count+1]);
		}
		if (strcmp(argc[count], "-avgDensity")==0)
		{
			minAvgEdgeDensity=atof(argc[count+1]);
		}
	}


	if (countNumParamters!=10)
	{
		printf("usage:\n needs ten paramters to run\n -p <PPI Network> \n -c <cases/control mutaion list> \n -h <Gene CoExpression Id> \n -e <CoExpression Matrix> \n -s <Seed Fild> \n -m <upperbound on contorl mutations> \n -l <lower bound on the size of the module > \n -u <upper bound on the size of cluster> \n -a <minimum ratio of seed score allowed> \n -i <random run id> \n -minCoExpr <minimum pair-wise coexpression value (optional: defualt is set to 0.01) \n -avgCoExpr <minimum average coexpression of the module (optional: defualt is set at 0.415)> \n -avgDensity <average density of PPI (optional, defualt is set at 0.08)> \n");
		return 0;
	}

	srand(time(NULL)+randomNum);
	createPPI_Graph(fp1);
        assignScorePrecalculated(fp2);
        createCoExpresionGeneHash(fp3);
	createCoExpresionMatix(fp4);
	readPathFiles(fp5);
	markPathsNotToUse();
	createGraphOfPaths();
	randomConnectedComponents(randomNum);
}
