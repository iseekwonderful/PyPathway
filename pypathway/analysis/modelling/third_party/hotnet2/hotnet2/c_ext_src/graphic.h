//
//  graphic.h
//  color_coding
//
//  Created by sheep on 2017/8/2.
//  Copyright © 2017年 sheep. All rights reserved.
//

#ifndef graphic_h
#define graphic_h

#include <stdio.h>
#include "data_structure.h"

struct Graph* init_10_node_test_graph();

void display_graphic(struct Graph* G);

void init_graph_variable(int parallel_length, struct Graph* G, int* scores);

void simulate_loop(struct Graph* G, int parallel_length, int* scores);

#endif /* graphic_h */
