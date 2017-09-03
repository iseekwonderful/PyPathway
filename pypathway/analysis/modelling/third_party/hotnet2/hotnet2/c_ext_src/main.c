//
//  main.c
//  color_coding
//
//  Created by sheep on 2017/8/2.
//  Copyright © 2017年 sheep. All rights reserved.
//

#include <stdio.h>
#include "data_structure.h"
#include "graphic.h"
#include "test_data.h"
#include "basic.h"


void testQueue(){
    struct QueueNode* queue = initQueue(1);
    queuePopLeft(&queue);
    queueAppend(&queue, 2);
    queuePopRight(&queue);
    queueAppend(&queue, 3);
    queueAppend(&queue, 4);
    queueAppend(&queue, 5);
    printf("%i\n", queuePopRight(&queue));
    printf("%i\n", queuePopLeft(&queue));
    printf("%i\n", queuePopRight(&queue));
    printf("%i\n", queuePopLeft(&queue));
}

int main(int argc, const char * argv[]) {
//    struct Graph* test_graph = init_10_node_test_graph();
//    int score[10] = {2, 1, 4, 3, 2, 5, 6, 4, 2, 1};
//    simulate_loop(test_graph, test_graph->node_count, &score);
    int mt[7][7] = {{0, 1, 0, 0, 0, 0, 0},
        {0, 0, 1, 0, 0, 0, 0}, {0, 0, 0, 1, 0, 0, 0},
        {1, 0, 0, 0, 0, 0, 0}, {0, 0, 0, 0, 0, 1, 0},
        {0, 0, 0, 0, 0, 0, 1}, {0, 0, 0, 0, 1, 0, 0}};
    struct MatrixDes* md = generateTestMatrix(mt, 7);
    struct Graph* G = DiGraphFromMatrix(md);
    struct SubQueue* sq = stronglyConnectedComponent(G);
    while (sq) {
        while (sq->queue) {
            printf("%i, ", sq->queue->value);
            sq->queue = sq->queue->next;
        }
        printf("\n");
        sq = sq->next;
    }
//    testQueue();
}

