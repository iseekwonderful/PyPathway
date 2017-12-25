#ifndef _PPI_GRAPH
#define _PPI_GRAPH

#include <stdio.h>
#include <stdlib.h>

#define maxNumNode 30000
#define geneNameLen 50
#define minCoExpresThreshold 0.37

// const int geneNameLen=50;

// const float minCoExpresThreshold=0.37;
extern int numNodes;
extern int coExpresGeneNum;
extern int totalSevereMutInCases;
extern int totalMissenseMutInCases;
extern int totalSevereMutInControl;
extern int totalLengthGenes;
extern float allNodeMeanValue;
extern float allNodesSTD;
extern int totalNodesWithScoreAssigned;
// extern float coexpressionPValue[102];// [0, 0.01, 0.02, ..., 0.99, 1]: the co-expression p-value for every edge (for very coExpresionValue > x
extern float* coexpressionPValue;
extern float meanCoExpression;
extern float varianceCoExpression;

#define bool int
#define true 1
#define false 0


typedef struct PPI_Node{
	int nodeId;
	char nodeName[50]; // protein/gene name
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
	char geneName[50];
	int hashId; // The coexpression table Id
}coExpresionGeneHash;

// extern coExpresionGeneHash coExpresionGeneHashTable[30000];

// extern PPI_Node listNodes[30000];

extern coExpresionGeneHash* coExpresionGeneHashTable;
extern PPI_Node* listNodes;

extern float** coExpresionMatrix;

void freeCoExpresionGeneMatrix();
void freeCoExpresionGeneHash();
void freePPI_Graph();
int createPPI_Graph(FILE *);
//int assignScoreCases(FILE *);
//int assignScoreControls(FILE *);
int createCoExpresionMatix(FILE *);
int assignScoreToBothControlandCases(FILE *, FILE *, FILE *, FILE *, FILE *, bool, int);
int assignScorePrecalculated(FILE *);
int createCoExpresionGeneHash(FILE *, int);
int isConnectedPPI(int, int);
double log_N_Choose_M(int , int);
bool isSubGraphConnectedComponent(int *, int); // a list of node Ids and the number of noces
bool isSubGraphConnectedComponenti_WithCoExpr(int *, int);
void init_vars();
#endif
