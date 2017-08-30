struct Node* connected_double_edge_swap(struct Node* G, int node_count, int nswap, int windows_threhold);

void display_graph(struct Node * nodes, int node_count);

struct Node* parse_adjacency_matrix(int * id_list, int * matrix, int length);

int* build_adjacency_matrix(struct Node* nodes, int node_count);

struct Node {
    int node_id;
    int * neighbours;
    int neighbour_count;
};