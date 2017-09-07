#include <Python.h>
#include "main.h"
#include <numpy/arrayobject.h>
#include <stdlib.h>


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

    import_array();
    
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
    char * adjacency;
    int adjacency_size;
    PyObject *adj_object;

//    if (!PyArg_ParseTuple(args, "s#s#iii", &id_list, &id_size, &adjacency,
//     &adjacency_size, &node_count, &repeats, &windows_threholds)) {
//        return NULL;
//    }

    if (!PyArg_ParseTuple(args, "s#Oiii", &id_list, &id_size, &adj_object, &node_count, &repeats, &windows_threholds)) {
        return NULL;
    }

    adjacency_size = (int)PyArray_DIM(adj_object, 0);
    adjacency = (char*)PyArray_DATA(adj_object);

    // Py_DECREF(adj_object);

    if (adjacency == NULL) {
        printf("adjacency null %i\n", adjacency_size);
        exit(1);
    }

    // printf("%i, %i, %i\n", id_size, adjacency_size, node_count);

    struct Node* r = parse_adjacency_matrix(id_list, adjacency, node_count);

    struct Node* res = connected_double_edge_swap(r, node_count, repeats, windows_threholds);

    char* matrix = build_adjacency_matrix(res, node_count);

    int* id2node = (int *)malloc(sizeof(int) * node_count);

    for (int i = 0; i < node_count; ++i)
    {
        id2node[i] = res[i].node_id;
    }

    npy_intp dims[2];
    dims[0] = adjacency_size;
    dims[1] = adjacency_size;

    PyObject* mat;
    mat = PyArray_SimpleNewFromData(2, dims, NPY_INT8, matrix);

    /* Build the output tuple */
    PyObject* ret = Py_BuildValue("y#Oi", id_list, sizeof(int) * node_count, mat, node_count);
    return ret;
}