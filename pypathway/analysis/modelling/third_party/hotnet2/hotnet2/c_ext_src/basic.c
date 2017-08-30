//
//  basic.c
//  color_coding
//
//  Created by Yang Xu on 2017/8/16.
//  Copyright © 2017年 sheep. All rights reserved.
//

#include "basic.h"
#include "data_structure.h"
#include <string.h>
#include <stdlib.h>

struct Graph* DiGraphFromMatrix(struct MatrixDes* md) {
    struct Graph* G = (struct Graph*)malloc(sizeof(struct Graph));
    G->nodes = (struct Node*)malloc(sizeof(struct Node) * md->length);
    int * mt = md->matrix;
    for (int i = 0; i < md->length; i++) {
        G->nodes[i].degree = 0;
        G->nodes[i].id = i;
        for (int j = 0; j < md->length; j++) {
            if (*(mt + md->length * i + j) != 0) {
                if (G->nodes[i].degree == 0) {
                    G->nodes[i].neighbours = (int*)malloc(sizeof(int));
                    G->nodes[i].neighbours[0] = j;
                    G->nodes[i].degree++;
                }else{
                    G->nodes[i].neighbours = (int*)realloc(G->nodes[i].neighbours,
                                                           (G->nodes[i].degree + 1) * sizeof(int));
                    G->nodes[i].neighbours[G->nodes[i].degree] = j;
                    G->nodes[i].degree++;
                }
            }
        }
    }
    G->node_count = md->length;
    return G;
}


struct SubQueue* stronglyConnectedComponent(struct Graph* G) {
    // store the result
    struct SubQueue* result = (struct SubQueue*)malloc(sizeof(struct SubQueue));
    struct SubQueue* current = result;
    result->next = NULL;
    result->queue = NULL;
    int * preorder = (int *)malloc(sizeof(int) * G->node_count);
    memset(preorder, 0, sizeof(int) * G->node_count);
    int * lowlink = (int *)malloc(sizeof(int) * G->node_count);
    memset(lowlink, 0, sizeof(int) * G->node_count);
    int * scc_found = (int *)malloc(sizeof(int) * G->node_count);
    memset(scc_found, 0, sizeof(int) * G->node_count);
    struct QueueNode* scc_queue = NULL;
    int i = 0;
    for (int j = 0; j < G->node_count; j++) {
        if (G->nodes[j].degree == 0) {
            // this is an empty node
            continue;
        }
        if (scc_found[G->nodes[j].id]) {
            // already done
            continue;
        }
        struct QueueNode* queue = initQueue(j);
        // check if queue is empty while it should be empty
        while (queue) {
            int v = queuePeakRight(queue);
            if (preorder[v] == 0) {
                i += 1;
                preorder[v] = i;
            }
            int done = 1;
            // go through beighbours
            for (int k = 0; k < G->nodes[v].degree; k++) {
                int nei_id = G->nodes[v].neighbours[k];
                if (preorder[nei_id] == 0) {
                    queueAppend(&queue, nei_id);
                    done = 0;
                    break;
                }
            }
            if (done == 1) {
                lowlink[v] = preorder[v];
                for (int k = 0; k < G->nodes[v].degree; k++) {
                    int nei_id = G->nodes[v].neighbours[k];
                    if (scc_found[nei_id] == 0) {
                        if (preorder[nei_id] > preorder[v]) {
                            lowlink[v] = lowlink[v] < lowlink[nei_id] ? lowlink[v] : lowlink[nei_id];
                        }else{
                            lowlink[v] = lowlink[v] < preorder[nei_id] ? lowlink[v] : preorder[nei_id];
                        }
                    }
                }
                queuePopRight(&queue);
                if (lowlink[v] == preorder[v]) {
                    scc_found[v] = 1;
                    struct QueueNode* resultQueue = initQueue(v);
                    // printf("%i, ", v);
                    while (scc_queue && preorder[queuePeakRight(scc_queue)] > preorder[v]) {
                        int k = queuePopRight(&scc_queue);
                        scc_found[k] = 1;
                        // printf("%i, ", k);
                        queueAppend(&resultQueue, k);
                    }
                    // printf("\n");
                    if (result->queue == NULL) {
                        result->queue = resultQueue;
                    }else{
                        struct SubQueue* next = (struct SubQueue*)malloc(sizeof(struct SubQueue));
                        next->queue = resultQueue;
                        next->next = NULL;
                        current->next = next;
                        current=next;
                    }
                }else{
                    queueAppend(&scc_queue, v);
                }
            }
        }
    }
    return result;
}
