#include <Python.h>
#include "clustering.h"

/* Docstrings */
static char module_docstring[] =
    "cluster exec warper of magi.";
static char chi2_docstring[] =
    "cluster exec warper of magi.";

/* Available functions */
static PyObject *cluster_cluster(PyObject *self, PyObject *args);

/* Module specification */
static PyMethodDef module_methods[] = {
    {"cluster", cluster_cluster, METH_VARARGS, chi2_docstring},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_cluster",
    module_docstring,
    -1,
    module_methods,
    NULL,
    NULL,
    NULL,
    NULL,
};

/* Initialize the module */
PyObject *PyInit__cluster(void)
{
    PyObject *module = PyModule_Create(&moduledef);
    if (module == NULL)
        return NULL;

    /* Load `numpy` functionality. */
    return module;
}

static PyObject *cluster_cluster(PyObject *self, PyObject *args)
{
    /* Parse the input tuple */
    char* p;    //ppi
    char* c;    //case/control
    char* h;    //coexpression id
    char* e;    //coexpression matrix
    char* s;    //seed
    int m;      //upper bound
    int l;      //lower bound
    int u;      //up size
    char* a;    //minimum ratio of seed score
    char* id;   //run id
    char* outdir;

    // null able
    char* minCoExpr = "0.01";
    char* avgCoExpr = "0.415";
    char* avgDensity = "0.08";


    if (!PyArg_ParseTuple(args, "sssssiiissssss", &p, &c, &h, &e, &s,
     &m, &l, &u, &a, &id, &minCoExpr, &avgCoExpr, &avgDensity, &outdir)) {
        return NULL;
    }
    if (strcmp(minCoExpr, "none") == 0)
    {
        minCoExpr = "0.01";
    }
    if (strcmp(avgCoExpr, "none") == 0){
        avgCoExpr = "0.415";
    }
    if (strcmp(avgDensity, "none") == 0){
        avgDensity = "0.08";
    }
    clustering(p, c, h, e, s, m, l, u, a, id,
     minCoExpr, avgCoExpr, avgDensity, outdir);
    // int value = hi();

    /* Build the output tuple */
    PyObject *ret = Py_BuildValue("i", 1);
    return ret;
}