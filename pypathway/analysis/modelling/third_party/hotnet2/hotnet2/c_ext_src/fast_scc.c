#include <Python.h>
#include <numpy/arrayobject.h>
#include <stdlib.h>
#include "data_structure.h"
#include "graphic.h"
#include "test_data.h"
#include "basic.h"
#include <time.h>


/* Docstrings */
static char module_docstring[] =
    "This module provides an interface for calculating chi-squared using C.";
static char fast_scc_docstring[] =
    "Calculate the chi-squared of some data given a model.";

/* Available functions */
static PyObject *fast_scc_scc(PyObject *self, PyObject *args);

/* Module specification */
static PyMethodDef module_methods[] = {
    {"scc", fast_scc_scc, METH_VARARGS, fast_scc_docstring},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "fast_scc",
    module_docstring,
    -1,
    module_methods,
    NULL,
    NULL,
    NULL,
    NULL,
};

/* Initialize the module */
PyObject *PyInit_fast_scc(void)
{
    PyObject *module = PyModule_Create(&moduledef);
    if (module == NULL)
        return NULL;
    
    /* Load `numpy` functionality. */
    import_array();
    
    return module;
}

static PyObject *fast_scc_scc(PyObject *self, PyObject *args)
{
    clock_t cstart = clock();
    clock_t cend = 0;


    double m;
    PyObject *x_obj;

    /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "dO", &m, &x_obj))
        return NULL;

    /* Interpret the input objects as numpy arrays. */
    PyObject *x_array = PyArray_FROM_OTF(x_obj, NPY_BOOL, NPY_IN_ARRAY);

    /* If that didn't work, throw an exception. */
    if (x_array == NULL) {
        Py_XDECREF(x_array);
        return NULL;
    }

    /* How many data points are there? */
    int N = (int)PyArray_DIM(x_array, 0);
    // int M = (int)PyArray_DIM(x_array, 1);

    // if (N != M) {
    //     printf("ToDo: raise exception");
    // }

    /* Get pointers to the data as C-types. */
    char *x    = (char*)PyArray_DATA(x_array);

    /* Call the external C function to compute the chi-squared. */
    // struct MatrixDes* md = generateTestMatrix(x, N);
    struct MatrixDes* md = (struct MatrixDes*)malloc(sizeof(struct MatrixDes));
    md->length = N;
    md->matrix = x;
    cend = clock();
    printf ("%.6f cpu sec\n", ((double)cend - (double)cstart)* 1.0e-6);
    cstart = clock();
    cend = 0;
    struct Graph* G = DiGraphFromMatrix(md);
    cend = clock();
    printf ("%.6f cpu sec\n", ((double)cend - (double)cstart)* 1.0e-6);
    cstart = clock();
    // freeMatrixDes(md);
    struct SubQueue* sq = stronglyConnectedComponent(G);
    cend = clock();
    printf ("%.6f cpu sec\n", ((double)cend - (double)cstart)* 1.0e-6);
    int * result = (int *)malloc(sizeof(int) * N * 3);
    memset(result, 0, sizeof(int) * N * 3);
    int curpos = 0;
    while (sq) {
        int start_pos = curpos + 1;
        while (sq->queue) {
            // printf("%i, ", sq->queue->value);
            result[curpos] += 1;
            result[start_pos] = sq->queue->value;
            start_pos += 1;
            sq->queue = sq->queue->next;
        }
        // printf("\n");
        sq = sq->next;
        curpos = start_pos;
        // printf("curpos: %i\n", curpos);
    }

    /* Clean up. */
    Py_DECREF(x_array);

    npy_intp Dims[1];
    Dims[0] = curpos;

    // int res[3] = {1, 2, 3};
    // int* r = (int *)malloc(sizeof(int) * 3);
    // memcpy(r, res, sizeof(int) * 3);

    PyObject* mat = PyArray_SimpleNewFromData(1, Dims, NPY_INT, result);

    return mat;
}