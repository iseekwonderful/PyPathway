//
//  data_structure.c
//  color_coding
//
//  Created by sheep on 2017/8/2.
//  Copyright © 2017年 sheep. All rights reserved.
//

#include "data_structure.h"
#include <stdlib.h>

void queueAppend(struct QueueNode** queue, int val){
    // if the queue is enpty
    if (*queue == NULL) {
        *queue = initQueue(val);
        return;
    }
    struct QueueNode* node = (struct QueueNode*)malloc(sizeof(struct QueueNode));
    node->value = val;
    node->next = NULL;
    node->end = node;
    struct QueueNode* perious_end = (*queue)->end;
    node->perious = perious_end;
    (*queue)->end->next = node;
    (*queue)->end = node;
}

int queuePopLeft(struct QueueNode** queue){
    if ((*queue)->next == NULL) {
        // only has one node
        int val = (*queue)->value;
        *queue = NULL;
        return val;
    }
    struct QueueNode* left = *queue;
    struct QueueNode* new_left = left->next;
    new_left->end = left->end;
    int left_val = left->value;
    *queue = new_left;
    return left_val;
}

int queuePopRight(struct QueueNode** queue){
    struct QueueNode* right = NULL;
    if (*queue == NULL) {
        return -1;
    }else if ((*queue)->next == NULL) {
        int val = (*queue)->value;
        right = *queue;
        free(right);
        *queue = NULL;
        return val;
    }else{
        struct QueueNode* cur_end = (*queue)->end;
        struct QueueNode* new_end = cur_end->perious;
        (*queue)->end = new_end;
        new_end->next = NULL;
        int val = cur_end->value;
        free(cur_end);
        return val;
    }
}

int queuePeakLeft(struct QueueNode* queue){
    return queue->value;
}

int queuePeakRight(struct QueueNode* queue){
    return queue->end->value;
}

struct QueueNode* initQueue(int val){
    struct QueueNode* node = (struct QueueNode*)malloc(sizeof(struct QueueNode));
    node->next = NULL;
    node->value = val;
    node->end = node;
    node->perious = NULL;
    return node;
}

// The structure representation of the graph node




