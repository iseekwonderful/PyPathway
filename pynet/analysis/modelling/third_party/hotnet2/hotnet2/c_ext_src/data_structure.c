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
    if (*queue == NULL) {
        *queue = initQueue(val);
        return;
    }
    struct QueueNode* source = *queue;
    struct QueueNode* node = (struct QueueNode*)malloc(sizeof(struct QueueNode));
    node->value = val;
    node->next = NULL;
    while ((*queue)->next) {
        *queue = (*queue)->next;
    }
    (*queue)->next = node;
    *queue = source;
}

int queuePopLeft(struct QueueNode** queue){
    int left_val = (*queue)->value;
    *queue = (*queue)->next;
    return left_val;
}

int queuePopRight(struct QueueNode** queue){
    if (*queue == NULL) {
        return -1;
    }else if ((*queue)->next == NULL) {
        int val = (*queue)->value;
        *queue = NULL;
        return val;
    }else{
        struct QueueNode* op = *queue;
        while (op->next->next) {
            op = op->next;
        }
        int value = op->next->value;
        op->next = NULL;
        return value;
    }
}

int queuePeakLeft(struct QueueNode* queue){
    return queue->value;
}

int queuePeakRight(struct QueueNode* queue){
    while (queue->next) {
        queue = queue->next;
    }
    return queue->value;
}

struct QueueNode* initQueue(int val){
    struct QueueNode* node = (struct QueueNode*)malloc(sizeof(struct QueueNode));
    node->next = NULL;
    node->value = val;
    return node;
}

// The structure representation of the graph node




