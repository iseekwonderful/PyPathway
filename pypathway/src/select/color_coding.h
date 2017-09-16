#ifndef _color_coding
#define _color_coding
#include "PPI_Graph.h"

#define maxNumColor 20
#define weightContorl 100

// thread-identical
extern int numColor; // the is the length of the path we are looking to find(colors start from 1)
// const int maxNumColor=20;
// const int weightContorl=100; // maximum weight of control allowd (maximum size of knapsack
//const float coExpressHardCut=0.37;

// thread-identical
extern double ****DPMatrix;
// thread-identical
extern int colorAssigned[30000];
// thread-identical
extern int colorBinaryRep[21];//color 0 is not there. Starts by color1

int pathway_select(char* ppi_network, char* case_list, char* co_expression_id,
    char* co_expression_matrix, char* control_list, char* filter_list,
    char* length, char* run_id, int num_color, int num_mut, char * file_name);

extern int controlServMutAllowed;

void initialize();
bool hasColor(int, int); // given the color list A (an integer which repersents the color set). check if a partocular color B is there or not.
int addColor(int, int);// given the color list A, add color B. return the new list
int removeColor(int, int);// given the color list A, remove color B. return the new list
void randomColor();
#endif
