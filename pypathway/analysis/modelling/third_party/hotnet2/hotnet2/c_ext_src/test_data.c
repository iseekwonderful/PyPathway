//
//  test_data.c
//  color_coding
//
//  Created by sheep on 2017/8/3.
//  Copyright © 2017年 sheep. All rights reserved.
//

#include "test_data.h"
#include "data_structure.h"
#include <string.h>
#include <stdlib.h>

struct Graph* load_string_network(){
    return NULL;
}

struct Graph* load_biogrid_network(){
    return NULL;
}

struct Graph* load_hint_network(){
    return load_generate_tab_network("/Users/yangxu/submodule/raw_network/hint.txt");
}


struct Graph* load_generate_tab_network(char* path){
    FILE* fp = fopen(path, "r");
    int node1, node2;
    float weight;
    int* degree = (int*)malloc(sizeof(int) * 1000000);
    memset(degree, 0, sizeof(int) * 1000000);
    while (fscanf(fp, "%i\t%i\t%f\n", &node1, &node2, &weight) > 0) {
        // printf("%i -- %i : weight %f\n", node1, node2, weight);
        degree[node1] ++;
        degree[node2] ++;
    }
    int count = 0;
    for (int i = 0; i < 1000000; i ++) {
        if (degree[i] == 0) {
            count = i;
            break;
        }
    }
    struct Graph* graph = (struct Graph*)malloc(sizeof(struct Graph));
    graph->node_count = count;
    graph->nodes = (struct Node*)malloc(sizeof(struct Node) * graph->node_count);
    for (int i = 0; i < graph->node_count; i ++) {
        graph->nodes[i].degree = 0;
        graph->nodes[i].id = i;
        graph->nodes[i].neighbours = (int*)malloc(sizeof(int) * degree[i]);
    }
    free(degree);
    fseek(fp, 0, SEEK_SET);
    while (fscanf(fp, "%i\t%i\t%f\n", &node1, &node2, &weight) > 0) {
        graph->nodes[node1].neighbours[graph->nodes[node1].degree] = node2;
        graph->nodes[node2].neighbours[graph->nodes[node2].degree] = node1;
        graph->nodes[node1].degree ++;
        graph->nodes[node2].degree ++;
    }
    return graph;
}


struct MatrixDes* simpleTestMatrix(){
    int mt[3][3] = {{0, 1, 0}, {1, 0, 1}, {0, 1, 0}};
    int* matrix = (int *)malloc(sizeof(int) * 9);
    struct MatrixDes* md = malloc(sizeof(struct MatrixDes));
    memcpy(matrix, mt, sizeof(int) * 9);
    md->length = 3;
    md->matrix = matrix;
    return md;
}

void freeMatrixDes(struct MatrixDes* md){
    free(md->matrix);
    free(md);
}


struct MatrixDes* generateTestMatrix(int ** mat, int length){
    int * matrix = (int *)malloc(sizeof(int) * length * length);
    struct MatrixDes* md = malloc(sizeof(struct MatrixDes));
    memcpy(matrix, mat, length * length * sizeof(int));
    md->length = length;
    md->matrix = matrix;
    return md;
}

void printMatrix(struct MatrixDes* md) {
    for (int i = 0; i < md->length; i++) {
        for (int j = 0; j < md->length; j ++) {
            printf("%i, ", *(md->matrix + md->length * i + j));
        }
        printf("\b \b\b \b\n");
    }
}
