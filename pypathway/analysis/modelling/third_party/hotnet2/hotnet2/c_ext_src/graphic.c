//
//  graphic.c
//  color_coding
//
//  Created by sheep on 2017/8/2.
//  Copyright © 2017年 sheep. All rights reserved.
//

#include "graphic.h"
#include "data_structure.h"
#include "string.h"
#include "stdlib.h"
#include "time.h"

struct TodoNode** todoList;
struct TodoNode** nextTodo;
struct State** states;

// the score/color-coding related function
void init_graph_variable(int parallel_length, struct Graph* G, int* scores){
    // init the space for the two variable, todoList and the states
    todoList = (struct TodoNode**)malloc(sizeof(struct TodoNode*) * parallel_length);
    states = (struct State**)malloc(sizeof(struct State*) * parallel_length);
    nextTodo = (struct TodoNode**)malloc(sizeof(struct TodoNode*) * parallel_length);
    //memset(nextTodo, 0, sizeof(struct TodoNode*) * parallel_length);
    for (int i = 0; i < parallel_length; i++) {
        nextTodo[i] = NULL;
    }
    // first do not consider the situation
    for (int i = 0; i < G->node_count; i ++) {
        struct State* node_state = (struct State*)malloc(sizeof(struct State));
        struct TodoNode* todo_node = (struct TodoNode*)malloc(sizeof(struct State));
        node_state->node = G->nodes + i;
        node_state->id = G->nodes[i].id;
        node_state->perious = NULL;
        // fix me if necessary
        node_state->color = 0;
        node_state->score = scores[i];
        node_state->depth = 0;
        // init todo node
        todo_node->node = G->nodes + i;
        todo_node->perious = NULL;
        todo_node->state = node_state;
        todo_node->id = G->nodes[i].id;
        todoList[i] = todo_node;
        states[i] = node_state;
    }
}

void reinit_graph_variable(int parallel_length) {
    todoList = nextTodo;
    nextTodo = (struct TodoNode**)malloc(sizeof(struct TodoNode*) * parallel_length);
}

int simulate_GPU(int parallel_length, struct Graph* G, int terminate_depth, int* max_score, int* scores){
    int remain = 0;
    // simulate the GPU running state, undependent threads
    for (int i = 0; i < parallel_length; i ++) {
        struct TodoNode* todo = todoList[i];
        while (todo != NULL) {
            if (todo->state->depth == terminate_depth) {
                // the path has ended
                if (todo->state->score > *max_score) {
                    printf("The high score now is %i\n", todo->state->score);
                    *max_score = todo->state->score;
                }
                todo = todo->perious;
                continue;
            } else {
                printf("current score is %i, depth is %i\n", todo->state->score, todo->state->depth);
            }
            for (int nei = 0; nei < todo->node->degree; nei ++) {
                // neighbour node
                struct Node* neighbour_node = G->nodes + todo->node->neighbours[nei];
                // init a state
                struct State* node_state = (struct State*)malloc(sizeof(struct State));
                node_state->perious = todo->state;
                node_state->depth = todo->state->depth + 1;
                node_state->id = neighbour_node->id;
                node_state->color = 0;
                node_state->score = todo->state->score + scores[neighbour_node->id];
                node_state->node = neighbour_node;
                // init a todoNode
                struct TodoNode* todo_node = (struct TodoNode*)malloc(sizeof(struct TodoNode));
                todo_node->id = neighbour_node->id;
                todo_node->node = neighbour_node;
                todo_node->state = node_state;
                todo_node->perious = NULL;
                if (nextTodo[i] == NULL) {
                    nextTodo[i] = todo_node;
                }else{
                    struct TodoNode* last = nextTodo[i];
                    while (last->perious) {
                        last = last->perious;
                    }
                    last->perious = todo_node;
                }
                remain ++;
            }
            todo = todo->perious;
        }
    }
    return remain;
}

void simulate_loop(struct Graph* G, int parallel_length, int* scores){
    int terminate_length = 2;
    int* max_score = (int *)malloc(sizeof(int));
    *max_score = 0;
    init_graph_variable(parallel_length, G, scores);
    while (1) {
        int remain = simulate_GPU(parallel_length, G, terminate_length, max_score, scores);
        if (remain == 0) {
            printf("max score is %i\n", *max_score);
            break;
        }
        reinit_graph_variable(parallel_length);
    }
}

// Basic graphic function
void display_graphic(struct Graph* G){
    printf("This graphic contains %i nodes\n", G->node_count);
    for (int i = 0; i < G->node_count; i++) {
        printf("Node %i: \n", G->nodes[i].id);
        for (int j = 0; j < G->nodes[i].degree; j ++) {
            printf("\t\t%i -- %i\n", G->nodes[i].id, G->nodes[i].neighbours[j]);
        }
    }
}

struct Graph* init_10_node_test_graph(){
    struct Graph* graph = (struct Graph*)malloc(sizeof(struct Graph));
    graph->nodes = (struct Node*)malloc(sizeof(struct Node) * 10);
    graph->node_count = 10;
    for (int i = 0; i < 10; i++) {
        struct Node* node = (struct Node*)malloc(sizeof(struct Node));
        node->id = i;
        node->degree = 2;
        node->neighbours = (int *)malloc(sizeof(int));
        if (i == 0) {
            node->neighbours[0] = 1;
            node->neighbours[1] = 9;
        }else if (i == 9){
            node->neighbours[0] = 8;
            node->neighbours[1] = 0;
        }else{
            node->neighbours[0] = i - 1;
            node->neighbours[1] = i + 1;
        }
        graph->nodes[i] = *node;
    }
    return graph;
}




