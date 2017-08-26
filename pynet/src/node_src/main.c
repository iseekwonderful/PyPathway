//
//  main.c
//  graph
//
//  Created by Yang Xu on 2017/5/30.
//  Copyright © 2017年 Yang Xu. All rights reserved.
//

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "randpick.h"
#include "heap.h"
#include <math.h>
#include <string.h>


int tagged(int* list, int list_length, int id, int max_id);

struct Node2 {
    int node_id;
    int neighbour_count;
};


// test function 2
void hello(){
    printf("hello ctypes\n");
}

// test function 3

void hello_list(int * a, int length){
    for (int i = 0; i < length; i ++) {
        printf("%i\n", a[i]);
    }
}

// test function 1
struct Node * view_node(struct Node * node, int node_length){
    for (int j = 0; j < node_length; j++) {
        printf("Node id: %i, neighbours: %i\n", node[j].node_id, node[j].neighbour_count);
        for (int i = 0; i < node[j].neighbour_count; i ++) {
            printf("%i, ", node[j].neighbours[i]);
        }
        printf("\n");
    }
    return node;
}

int is_two_node_connected(struct Node* n1, struct Node* n2){
    for (int i = 0; i < n1->neighbour_count; i++) {
        if (n1->neighbours[i] == n2->node_id) {
            return 1;
        }
    }
    return 0;
}

int has_path_between_two_nodes(struct Node ** id2Node, int max_node, int node1, int node2, int * mark){
    struct Node * start = id2Node[node1];
    mark[start->node_id] = 1;
    // if direct neighbour
    for (int i = 0; i < start->neighbour_count; i++) {
        if (start->neighbours[i] == node2) {
            return 1;
        }
    }
    // else find by neighbour
    for (int i = 0; i < start->neighbour_count; i++) {
        if (mark[start->neighbours[i]] == 1) {
            continue;
        }
        int r = has_path_between_two_nodes(id2Node, max_node, start->neighbours[i], node2, mark);
        if (r > 0) {
            return 1;
        }
    }
    return 0;
}

int is_2_node_connected(struct Node ** id2None, int max_node, int node1, int node2){
    int * mark = (int *)malloc(sizeof(int) * max_node);
    for (int i = 0; i < max_node; i ++) {
        mark[i] = 0;
    }
    free(mark);
    return has_path_between_two_nodes(id2None, max_node, node1, node2, mark);
}


int is_graph_connected(struct Node* G, int node_count, struct Node** id2Node, int max_node_id);

void check_child(struct Node** G, int node_count, int current_id, int * sign, int max_id);

void display_graph(struct Node * nodes, int node_count){
    printf("------------------------\n");
    for (int i = 0; i < node_count; i ++) {
        printf("Node id: %i, neighbour: %i\nEdges: ", nodes[i].node_id, nodes[i].neighbour_count);
        for (int j = 0; j < nodes[i].neighbour_count; j ++) {
            printf("%i, ", nodes[i].neighbours[j]);
            if (nodes[i].neighbours[j] < 0 || nodes[i].neighbours[j] > node_count) {
                // int a = 1;
            }
        }
        printf("\b\b\n");
    }
    printf("------------------------\n");
}
void display_graph2(struct Node ** nodes, int node_count){
    printf("------------------------\n");
    for (int i = 0; i < node_count; i ++) {
        if (nodes[i] == NULL) {
            continue;
        }
        printf("Node id: %i, neighbour: %i\nEdges: ", nodes[i]->node_id, nodes[i]->neighbour_count);
        for (int j = 0; j < nodes[i]->neighbour_count; j ++) {
            printf("%i, ", nodes[i]->neighbours[j]);
            if (nodes[i]->neighbours[j] < 0 || nodes[i]->neighbours[j] > node_count) {
                // int a = 1;
            }
        }
        printf("\b\b\n");
    }
    printf("------------------------\n");
}


// pick a neighbour from a node
int pick_neighbour(struct Node * N, int * rand_num){
    // fix me
//    printf("%i\n", N->neighbour_count);
    int node_num = rand() % N->neighbour_count;
    if (node_num == N->neighbour_count) {
        // may be the range limit;
        printf("Error while pick node");
    }else if (node_num < 0 || node_num >= N->neighbour_count) {
        // of cource issue, let it crash
        printf("ERROR\n pickneighbour: %i\n", node_num);
        exit(1);
    }
    *rand_num = node_num;
    // issue check it
    return N->neighbours[node_num];
}

// get the node from a node list using node's id
struct Node * get_node_from_graph(struct Node* G, int node_count, int target_id){
    for (int i = 0; i < node_count; i++) {
        if (G[i].node_id == target_id) {
            return G + i;
        }
    }
    return NULL;
}

// delete a edge between 2 nodes
int delete_edge(struct Node* n1, struct Node * n2){
    int * n1_neighbour = (int *)malloc(sizeof(int) * (n1->neighbour_count - 1));
    int * n2_neighbour = (int *)malloc(sizeof(int) * (n2->neighbour_count - 1));
    int i, j;
    for (i = j = 0; i < n1->neighbour_count; i++) {
        if (n1->neighbours[i] != n2->node_id) {
            n1_neighbour[j] = n1->neighbours[i];
            j += 1;
        }
    }
    for (i = j = 0; i < n2->neighbour_count; i++) {
        if (n2->neighbours[i] != n1->node_id) {
            n2_neighbour[j] = n2->neighbours[i];
            j += 1;
        }
    }
    free(n1->neighbours);
    free(n2->neighbours);
    n1->neighbours = n1_neighbour;
    n2->neighbours = n2_neighbour;
    n1->neighbour_count -= 1;
    n2->neighbour_count -= 1;
    return 1;
}

// add a edge between 2 nodes
int add_edge(struct Node* n1, struct Node * n2){
    int * n1_neighbour = (int *)malloc(sizeof(int) * (n1->neighbour_count + 1));
    int * n2_neighbour = (int *)malloc(sizeof(int) * (n2->neighbour_count + 1));
    for (int i = 0; i < n1->neighbour_count; i++) {
        n1_neighbour[i] = n1->neighbours[i];
    }
    for (int i = 0; i < n2->neighbour_count; i++) {
        n2_neighbour[i] = n2->neighbours[i];
    }
    n1_neighbour[n1->neighbour_count] = n2->node_id;
    n2_neighbour[n2->neighbour_count] = n1->node_id;
    free(n1->neighbours);
    free(n2->neighbours);
    n1->neighbours = n1_neighbour;
    n2->neighbours = n2_neighbour;
    n1->neighbour_count += 1;
    n2->neighbour_count += 1;
    return 1;
}

int* build_adjacency_matrix(struct Node* nodes, int node_count){
    int* id2Node = (int *)malloc(sizeof(int) * node_count);
    for (int i = 0; i < node_count; ++i)
    {
        id2Node[i] = nodes[i].node_id;
    }
    int* matrix = (int *)malloc(sizeof(int) * node_count * node_count);
    memset(matrix, 0, node_count * node_count);
    for (int i = 0; i < node_count; ++i)
    {
        for (int j = 0; j < nodes[i].neighbour_count; ++j)
        {
            // get the index:
            for (int k = 0; k < node_count; ++k)
            {
                if (id2Node[k] == nodes[i].neighbours[j])
                {
                    // printf("There are a edge between: %i, %i\n", i, k);
                    matrix[node_count * i + k] = 1;
                }
            }

        }
    }
    return matrix;
}

struct Node* parse_adjacency_matrix(int * id_list, int * matrix, int length){
    struct Node * nodes = (struct Node *)malloc(sizeof(struct Node) * length);
    for (int i = 0; i < length; ++i)
    {
        nodes[i].node_id = id_list[i];
        int neighbours = 0;
        for (int j = 0; j < length; ++j)
        {
            if (matrix[length * i + j] == 1)
            {       
                neighbours += 1;
            }
        }
        nodes[i].neighbour_count = neighbours;
        int * neighbours_matrix = (int *)malloc(sizeof(int) * neighbours);
        neighbours = 0;
        for (int j = 0; j < length; j++){
            if (matrix[length * i + j] == 1){
                neighbours_matrix[neighbours] = id_list[j];
                neighbours += 1;
            }
        }
        nodes[i].neighbours = neighbours_matrix;
    }
    display_graph(nodes, length);
    return nodes;
}

struct Node* connected_double_edge_swap(struct Node* G, int node_count, int nswap, int windows_threhold){
    // this version implement the windows size.
    srand((unsigned int)time(NULL));
    int i;
    struct Node* node1;
    struct Node* node2;
    struct Node* n1_rel;
    struct Node* n2_rel;
    int max_id = 0;
    // copy G
    // directly copy may be dingerous
    for (int i = 0; i < node_count; i++) {
        struct Node * n = malloc(sizeof(struct Node));
        n->node_id = G[i].node_id;
        if (n->node_id > max_id) {
            max_id = n->node_id;
        }
        n->neighbour_count = G[i].neighbour_count;
        n->neighbours = (int *)malloc(sizeof(int) * n->neighbour_count);
        for (int j = 0; j < n->neighbour_count; j ++) {
            n->neighbours[j] = G[i].neighbours[j];
        }
        G[i] = *n;
    }
    struct Node ** id2Node = malloc(sizeof(struct Node) * (max_id + 1));
    for (int i = 0; i < max_id + 1; i ++) {
        id2Node[i] = NULL;
    }
    for (int i = 0; i < node_count; i ++) {
        id2Node[G[i].node_id] = G + i;
    }
    i = 0;
    struct CDF * cdf = generate_cdf(G, node_count);
    windows_threhold = 3;
    int windows = 1;
    printf("\nStArT\n");
    while (i < nswap) {
        int wcount = 0;
        init_heap();
        if (windows < windows_threhold) {
            // do check every time
//            printf("low windows count\n");
            int fail = 0;
            while (wcount < windows && i < nswap) {
                if (i % 100000 == 0) {
                    printf("done: %i\n", i);
                }
//                printf("Low: i: %i, wcount: %i, windows: %i\n", i, wcount, windows);
                int * picked = choose_node_from_cdf(cdf, (float)(rand()) / (float)(RAND_MAX), (float)(rand()) / (float)(RAND_MAX));
                int n1 = picked[0];
                int n2 = picked[1];
                if (n1 == n2) {
                    continue;
                }
                // the node may be empty?
                node1 = get_node_from_graph(G, node_count, n1);
                node2 = get_node_from_graph(G, node_count, n2);
                if (node1 == NULL || node2 == NULL) {
                    printf("Oops node empty %i, %i\n", n1, n2);
                    continue;
                }
                int ri, rj;
                int n_id_1 = pick_neighbour(node1, &ri);
                int n_id_2 = pick_neighbour(node2, &rj);
                n1_rel = get_node_from_graph(G, node_count, n_id_1);
                n2_rel = get_node_from_graph(G, node_count, n_id_2);
                // any NULL error and continue
                if (node1 == NULL || node2 == NULL || n1_rel == NULL || n2_rel == NULL) {
                    // printf("node1 %llx, node2 %llx, n1_rel %llx n2_rel %llx\n", node1, node2, n1_rel, n2_rel);
                    continue;
                }
                if (node1->node_id == n2_rel->node_id || node2->node_id == n1_rel->node_id || n1_rel->node_id == n2_rel->node_id) {
                    continue;
                }
                if (is_two_node_connected(node1, node2) || is_two_node_connected(n1_rel, n2_rel)) {
                    continue;
                }
                // now let us do the exchage
                // before:   node1 -- n1_rel        after:   node1   n1_rel
                //                                             |       |
                //           node2 -- n2_rel                 node2   n2_rel
                // delete edge
                delete_edge(node1, n1_rel);
                delete_edge(node2, n2_rel);
                // add edge
                add_edge(node1, node2);
                add_edge(n1_rel, n2_rel);
                i += 1;
                add_swap(node1->node_id, node2->node_id, n1_rel->node_id, n2_rel->node_id);
                //        if (! is_graph_connected(G, node_count, id2Node, max_id)) {
                if (! is_2_node_connected(id2Node, max_id, node1->node_id, n1_rel->node_id)) {
                    // oops let us redo
//                    printf("Oops not connected, retry~\n");
                    add_edge(node1, n1_rel);
                    add_edge(node2, n2_rel);
                    // add edge
                    delete_edge(node1, node2);
                    delete_edge(n1_rel, n2_rel);
                    fail = 1;
                } else{
                    wcount += 1;
                }
            }
            if (fail == 1){
                windows = ceilf((float)windows / 2);
            }else{
                windows += 1;
            }
        }else{
//            printf("high windows count\n");
            // do check at end
            while (wcount < windows && i < nswap) {
                if (i % 100000 == 0) {
                    printf("done: %i\n", i);
                }
//                printf("High: i: %i, wcount: %i, window: %i\n", i, wcount, windows);
                int * picked = choose_node_from_cdf(cdf, (float)(rand()) / (float)(RAND_MAX), (float)(rand()) / (float)(RAND_MAX));
                int n1 = picked[0];
                int n2 = picked[1];
                if (n1 == n2) {
                    continue;
                }
                // the node may be empty?
                node1 = get_node_from_graph(G, node_count, n1);
                node2 = get_node_from_graph(G, node_count, n2);
                if (node1 == NULL || node2 == NULL) {
//                    printf("Oops node empty %i, %i\n", n1, n2);
                    continue;
                }
                int ri, rj;
                int n_id_1 = pick_neighbour(node1, &ri);
                int n_id_2 = pick_neighbour(node2, &rj);
                n1_rel = get_node_from_graph(G, node_count, n_id_1);
                n2_rel = get_node_from_graph(G, node_count, n_id_2);
                // any NULL error and continue
                if (node1 == NULL || node2 == NULL || n1_rel == NULL || n2_rel == NULL) {
                    // printf("node1 %llx, node2 %llx, n1_rel %llx n2_rel %llx\n", node1, node2, n1_rel, n2_rel);
                    continue;
                }
                if (node1->node_id == n2_rel->node_id || node2->node_id == n1_rel->node_id || n1_rel->node_id == n2_rel->node_id) {
                    continue;
                }
                if (is_two_node_connected(node1, node2) || is_two_node_connected(n1_rel, n2_rel)) {
                    continue;
                }
                // now let us do the exchage
                // before:   node1 -- n1_rel        after:   node1   n1_rel
                //                                             |       |
                //           node2 -- n2_rel                 node2   n2_rel
                // delete edge
                delete_edge(node1, n1_rel);
                delete_edge(node2, n2_rel);
                // add edge
                add_edge(node1, node2);
                add_edge(n1_rel, n2_rel);
                i += 1;
                add_swap(node1->node_id, node2->node_id, n1_rel->node_id, n2_rel->node_id);
                wcount += 1;
            }
            if (is_graph_connected(G, node_count, id2Node, max_id)) {
                windows += 1;
            }else{
                // then redo all
//                printf("Oops not connected, retry~\n");
                while (1) {
//                    printf("redo\n");
                    struct Swap* s = get_swap();
                    if (s == NULL) {
                        break;
                    }
                    struct Node * reN1 = get_node_from_graph(G, node_count, s->node1);
                    struct Node * reN2 = get_node_from_graph(G, node_count, s->node2);
                    struct Node * reN1_rel = get_node_from_graph(G, node_count, s->node3);
                    struct Node * reN2_rel = get_node_from_graph(G, node_count, s->node4);
                    add_edge(reN1, reN1_rel);
                    add_edge(reN2, reN2_rel);
                    // add edge
                    delete_edge(reN1, reN2);
                    delete_edge(reN1_rel, reN2_rel);
                }
                windows = ceilf((float)windows / 2.0);
            }
        }
    }
    return G;
}

int is_graph_connected(struct Node* G, int node_count, struct Node** id2Node, int max_node_id){
//    printf("in connecttion");
//    display_graph2(id2Node, max_node_id + 1);
//    exit(2);
    int* sign = (int *)malloc(sizeof(int) * (max_node_id + 1));
    for (int i = 0; i < max_node_id + 1; i++) {
        sign[i] = 0;
    }
    // start with a certain node, if all node visited, so that the graph is connected
    int start_id = G[0].node_id;
    tagged((int *)sign, node_count, start_id, max_node_id);
//    display_graph2(id2Node, max_node_id + 1);
    check_child(id2Node, node_count, start_id, sign, max_node_id);
    for (int i = 0; i < node_count; i ++) {
        if (sign[G[i].node_id] == 0) {
            free(sign);
            return 0;
        }
    }
    free(sign);
    return 1;
}

void check_child(struct Node** G, int node_count, int current_id, int * sign, int max_id){
//    display_graph2(G, max_id + 1);
    struct Node* current_node = G[current_id];
//    printf("check %i has %i children should have id: %i\n", current_node->node_id, current_node->neighbour_count, current_id);
    for (int j = 0; j < current_node->neighbour_count; j ++) {
        int child_id = current_node->neighbours[j];
//        printf("!!!!!!!\n");
//        if (child_id == 0) {
//            display_graph2(G, max_id);
//        }
//        printf("index is %i the child id is %i\n", j, child_id);
        int in = tagged(sign, node_count, child_id, max_id);
        if (in == 1) {
            check_child(G, node_count, child_id, sign, max_id);
        }
    }
}

// 1: not exist and added, 0: exist
int tagged(int* list, int list_length, int id, int max_id){
//    if (id >= max_id || id < 0) {
//        printf("error, max id overflow %i\n", id);
//    }
    if (list[id] == 1) {
        return 0;
    }else{
        list[id] = 1;
        return 1;
    }
}


// int test(){
//     struct Node * Graph = (struct Node *)malloc(sizeof(struct Node) * 10);
//     struct Node ** id2Node = (struct Node **)malloc(sizeof(struct Node *) * 10);
//     for (int i = 0; i < 10; i++) {
//         struct Node* n = (struct Node *)malloc(sizeof(struct Node));
//         n->node_id = i;
//         n->neighbour_count = 2;
//         n->neighbours = (int *)malloc(sizeof(int) * n->neighbour_count);
//         if (i == 9) {
//             n->neighbours[0] = 0;
//             n->neighbours[1] = 8;
//         } else if (i == 0){
//             n->neighbours[0] = 1;
//             n->neighbours[1] = 9;
//         }
//         else{
//             n->neighbours[0] = i - 1;
//             n->neighbours[1] = i + 1;
//         }
//         Graph[i] = *n;
//         id2Node[i] = n;
//     }
// //    view_node(Graph);
//     int res = connected_double_edge_swap(Graph, 10, 10000000, 2);
// //    int id2Node = (int *)malloc(sizeof(int) * 10);
// //    int res = is_graph_connected(Graph, 10, id2Node, 10);
// //    printf("is connected ?: %i\n", res);
//     return 0;
// }

int perform_test(){
    // First read the test graph
    char * path = "/Volumes/Data/hotnet2/paper/data/networks/hint+hi2012/hint+hi2012_edge_list";
    FILE * fp;
    fp = fopen(path, "r");
    int geneNameLen = 50;
    int * index2num = (int *)malloc(sizeof(int) * 10000);
    memset(index2num, 0, sizeof(int) * 10000);
    // indicate the neighbour index
    int * neighbour_index = (int *)malloc(sizeof(int) * 10000);
    memset(neighbour_index, 0, sizeof(int) * 10000);
    char geneName1[geneNameLen], geneName2[geneNameLen], noneSence[geneNameLen];
    while (fscanf(fp, "%s %s %s\n", geneName1, geneName2, noneSence)!=EOF) {
        int n1 = atoi(geneName1);
        int n2 = atoi(geneName2);
        index2num[n1] += 1;
        index2num[n2] += 1;
    }
    struct Node ** id2Node = malloc(sizeof(struct Node *) * 10000);
    int max = 0;
    for (int i = 1; i < 10000; i++) {
        if (index2num[i] == 0) {
            printf("max is %i\n", i);
            max = i;
            break;
        }else{
            struct Node * n = (struct Node *)malloc(sizeof(struct Node));
            n->node_id = i;
            n->neighbour_count = index2num[i];
            n->neighbours = (int *)malloc(sizeof(int) * index2num[i]);
            memset(n->neighbours, 0, sizeof(int) * index2num[i]);
            id2Node[i] = n;
        }
    }
    fseek(fp, 0, SEEK_SET);
    int n = 0;
    while (fscanf(fp, "%s %s %s\n", geneName1, geneName2, noneSence)!=EOF) {
        int n1 = atoi(geneName1);
        int n2 = atoi(geneName2);
        int n1_index = neighbour_index[n1];
        struct Node nn1 = *id2Node[n1];
        nn1.neighbours[n1_index] = n2;
        if (nn1.neighbour_count != index2num[n1]) {
            printf("Error\n");
        }
        neighbour_index[n1] += 1;
        id2Node[n2]->neighbours[neighbour_index[n2]] = n1;
        neighbour_index[n2] += 1;
        n ++;
    }
    printf("count: %i\n", id2Node[9859]->neighbour_count);
    for (int i = 0; i < id2Node[100]->neighbour_count; i++) {
        printf("%i\t", id2Node[100]->neighbours[i]);
    }
    struct Node * G = (struct Node *)malloc(sizeof(struct Node) * (max - 1));
    for (int i = 1; i < max; i += 1) {
        G[i - 1] = *id2Node[i];
    }
    // struct Node nn = G[max - 2];
    connected_double_edge_swap(G, max - 1, 100000, 3);
    return 0;
}

int main(int argc, const char * argv[]) {
    perform_test();
    return 0;
}
