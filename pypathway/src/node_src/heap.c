//
//  heap.c
//  link_node_test
//
//  Created by Yang Xu on 2017/6/30.
//  Copyright © 2017年 Yang Xu. All rights reserved.
//

#include "heap.h"
#include <stdlib.h>

struct Swap * heap;

struct Swap * init_heap(){
//    while (heap) {
//        struct Swap * p = heap->perious;
//        if (p == NULL){
//            break;
//        }
//        free(p->next);
//    }
    heap = NULL;
    return heap;
}

int add_swap(int node1, int node2, int node3, int node4){
    struct Swap *s = (struct Swap *)malloc(sizeof(struct Swap));
    s->node1 = node1;
    s->node2 = node2;
    s->node3 = node3;
    s->node4 = node4;
    s->next = NULL;
    s->perious = NULL;
    if (heap == NULL) {
        heap = s;
    }else{
        heap->next = s;
        s->perious = heap;
        heap = s;
    }
    return 1;
}

struct Swap * get_swap(){
    if (heap == NULL) {
        return NULL;
    }
    struct Swap * p = heap->perious;
    if (p == NULL){
        p = heap;
        heap=NULL;
        return p;
    }else{
        p = heap;
        heap = heap->perious;
        return p;
    }
}
