//
//  heap.h
//  link_node_test
//
//  Created by Yang Xu on 2017/6/30.
//  Copyright © 2017年 Yang Xu. All rights reserved.
//

#ifndef heap_h
#define heap_h

#include <stdio.h>


struct Swap {
    int node1;
    int node2;
    int node3;
    int node4;
    struct Swap * next;
    struct Swap * perious;
};

struct Swap * init_heap();

int add_swap(int node1, int node2, int node3, int node4);

struct Swap * get_swap();

#endif /* heap_h */
