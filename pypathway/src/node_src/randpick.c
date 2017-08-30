//
//  randpick.c
//  graph
//
//  Created by Yang Xu on 2017/6/5.
//  Copyright © 2017年 Yang Xu. All rights reserved.
//

#include "randpick.h"
#include <stdlib.h>

struct CDF * generate_cdf(struct Node * G, int node_count){
    // generate a cdf of node degree
    int * node_list = (int *)malloc(sizeof(int) * node_count);
    float * cdf = (float *)malloc(sizeof(float) * node_count);
    cdf[0] = 0;
    int j = 1;
    int sum = 0;
    for (int i = 0; i < node_count; i ++) {
        sum += G[i].neighbour_count;
    }
    for (int i = 0; i < node_count; i ++) {
        node_list[i] = G[i].node_id;
        cdf[j] = cdf[j - 1] + (float)(G[i].neighbour_count) / (float)(sum);
        j += 1;
    }
    struct CDF* c = (struct CDF*)malloc(sizeof(struct CDF));
    c->cdf = cdf;
    c->node_list = node_list;
    c->node_count = node_count;
    return c;
}

int* choose_node_from_cdf(struct CDF* cdf, float randnum1, float randnum2){
    int* a = (int *)malloc(sizeof(int) * 2);
    int i, j;
    i = bi_find(cdf->cdf, cdf->node_count, randnum1) - 1;
    j = bi_find(cdf->cdf, cdf->node_count, randnum2) - 1;
//    if (i >= cdf->node_count || i < 0 || j >= cdf->node_count || j < 0) {
//        printf("Exception of error %i or %i at %i\n", i, j, cdf->node_count);
//    }
    a[0] = cdf->node_list[i];
    a[1] = cdf->node_list[j];
//    if (a[0] == 0 || a[1] == 0) {
//        printf("I and J is %i, %i\n", i, j);
//    }
    return a;
}

int bi_find(float * seq, int count, float target){
    int lo = 0;
    int hi = count;
    while (lo < hi){
//        printf("lo: %i, hi: %i\n", lo, hi);
        if (seq[(int)((hi + lo) / 2)] < target) {
            lo = (int)((hi + lo) / 2) + 1;
        }else{
            hi = (int)((hi + lo) / 2);
        }
    }
    return lo;
}

