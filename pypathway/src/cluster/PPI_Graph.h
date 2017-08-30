#ifndef _PPI_GRAPH
#define _PPI_GRAPH

#include <stdio.h>
#include <stdlib.h>

#define maxNumNode 50000

const int geneNameLen=50;
const float minCoExpresThreshold=0.37;
extern int numNodes;
extern int coExpresGeneNum;
extern int totalSevereMutInCases;
extern int totalMissenseMutInCases;
extern int totalSevereMutInControl;
extern int totalLengthGenes;
extern float allNodeMeanValue;
extern float allNodesSTD;
extern int totalNodesWithScoreAssigned;
extern float coexpressionPValue[102];// [0, 0.01, 0.02, ..., 0.99, 1]: the co-expression p-value for every edge (for very coExpresionValue > x 
extern float meanCoExpression;
extern float varianceCoExpression;

#define bool int
#define true 1
#define false 0


typedef struct PPI_Node{
	int nodeId;
	char nodeName[geneNameLen]; // protein/gene name

	int numSevereMutInCases;
	int numMissenseMutInCases;
	int numSevereMutInControl;
	
	double prob;
	double weightCases;// The weight assigned for the cases I assume is double
	int weightControl;//The weight assigned to control I assume is integer
	int degree; //number of connections in the PPI network
	double log_length;
	int length;
	int *neighbours; // id of list of nodes each node is connected to
}PPI_Node;

typedef struct coExpresionGeneHash{
	int nodeId;// The gene id in the PPI network table
	char geneName[geneNameLen];
	int hashId; // The coexpression table Id
}coExpresionGeneHash;

extern coExpresionGeneHash coExpresionGeneHashTable[maxNumNode];

extern PPI_Node listNodes[maxNumNode];
extern float coExpresionMatrix[maxNumNode][maxNumNode];

int createPPI_Graph(FILE *); 
//int assignScoreCases(FILE *);
//int assignScoreControls(FILE *);
int createCoExpresionMatix(FILE *);
int assignScoreToBothControlandCases(FILE *, FILE *, FILE *, FILE *, FILE *, bool);
int assignScorePrecalculated(FILE *);
int createCoExpresionGeneHash(FILE *);
int isConnectedPPI(int, int);
double log_N_Choose_M(int , int);
bool isSubGraphConnectedComponent(int *, int); // a list of node Ids and the number of noces
bool isSubGraphConnectedComponenti_WithCoExpr(int *, int);
#endif
