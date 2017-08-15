//
//  randpick.h
//  graph
//
//  Created by Yang Xu on 2017/6/5.
//  Copyright © 2017年 Yang Xu. All rights reserved.
//

#ifndef randpick_h
#define randpick_h

#include <stdio.h>

struct Node {
    int node_id;
    int * neighbours;
    int neighbour_count;
};


struct CDF {
    int node_count;
    int* node_list;
    // take care that the cdf has +1 length than node_list
    float* cdf;
};

struct CDF * generate_cdf(struct Node * G, int node_count);

int* choose_node_from_cdf(struct CDF* cdf, float randnum1, float randnum2);

int bi_find(float * seq, int count, float target);

#endif /* randpick_h */
