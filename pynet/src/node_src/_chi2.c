#include <Python.h>
#include "main.h"


/* Docstrings */
static char module_docstring[] =
    "edge swap between node";
static char node_docstring[] =
    "edge swap between node";

/* Available functions */
static PyObject *swap_swap(PyObject *self, PyObject *args);

/* Module specification */
static PyMethodDef module_methods[] = {
    {"swap", swap_swap, METH_VARARGS, node_docstring},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_node",
    module_docstring,
    -1,
    module_methods,
    NULL,
    NULL,
    NULL,
    NULL,
};

/* Initialize the module */
PyObject *PyInit__node(void)
{
    PyObject *module = PyModule_Create(&moduledef);
    if (module == NULL)
        return NULL;
    
    /* Load `numpy` functionality. */    
    return module;
}

static PyObject *swap_swap(PyObject *self, PyObject *args)
{
    /* Parse the input tuple */
    int node_count;
    int repeats;
    int windows_threholds;

    int * id_list;
    int id_size;
    int * adjacency;
    int adjacency_size;

    if (!PyArg_ParseTuple(args, "s#s#iii", &id_list, &id_size, &adjacency,
     &adjacency_size, &node_count, &repeats, &windows_threholds)) {
        return NULL;
    }

    // printf("%i, %i, %i\n", id_size, adjacency_size, node_count);

    struct Node* r = parse_adjacency_matrix(id_list, adjacency, node_count);

    struct Node* res = connected_double_edge_swap(r, node_count, repeats, windows_threholds);

    int* matrix = build_adjacency_matrix(res, node_count);

    int* id2node = (int *)malloc(sizeof(int) * node_count);

    for (int i = 0; i < node_count; ++i)
    {
        id2node[i] = res[i].node_id;
    }

    /* Build the output tuple */
    PyObject *ret = Py_BuildValue("y#y#i", id2node, sizeof(int) * node_count, matrix, sizeof(int) * node_count * node_count, node_count);
    return ret;
}