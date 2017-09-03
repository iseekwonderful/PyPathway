//
//  data_structure.h
//  color_coding
//
//  Created by sheep on 2017/8/2.
//  Copyright © 2017年 sheep. All rights reserved.
//

#ifndef data_structure_h
#define data_structure_h

#include <stdio.h>

struct SubQueue {
    struct QueueNode* queue;
    struct SubQueue* next;
};

struct MatrixDes {
    char * matrix;
    int length;
};

struct Node {
    int id;
    int degree;
    int* neighbours;
};

struct Graph {
    int node_count;
    struct Node * nodes;
};

struct GraphSet {
    int graph_count;
    struct Graph * graphs;
};

struct CompactGraph {
    int* node_index;
    int* edge_list;
    int node_count;
    int edge_count;
};

struct State {
    int id;
    struct Node* node;
    struct State* perious;
    int color;
    int score;
    int depth;
};

struct TodoNode {
    int id;
    struct Node* node;
    struct TodoNode* perious;
    struct State* state;
};

struct QueueNode {
    int value;
    struct QueueNode* next;
    struct QueueNode* end;
    struct QueueNode* perious;
};

struct QueueNode* initQueue(int val);

int queuePeakLeft(struct QueueNode* queue);

int queuePeakRight(struct QueueNode* queue);

int queuePopRight(struct QueueNode** queue);

int queuePopLeft(struct QueueNode** queue);

void queueAppend(struct QueueNode** queue, int val);

#endif /* data_structure_h */
