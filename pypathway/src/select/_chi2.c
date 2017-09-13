#include <Python.h>
#include "color_coding.h"

/* Docstrings */
static char module_docstring[] =
    "This module provides an interface for calculating chi-squared using C.";
static char chi2_docstring[] =
    "Calculate the chi-squared of some data given a model.";

/* Available functions */
static PyObject *select_select(PyObject *self, PyObject *args);

/* Module specification */
static PyMethodDef module_methods[] = {
    {"select", select_select, METH_VARARGS, chi2_docstring},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_select",
    module_docstring,
    -1,
    module_methods,
    NULL,
    NULL,
    NULL,
    NULL,
};

/* Initialize the module */
PyObject *PyInit__select(void)
{
    PyObject *module = PyModule_Create(&moduledef);
    if (module == NULL)
        return NULL;
    
    /* Load `numpy` functionality. */    
    return module;
}

static PyObject *select_select(PyObject *self, PyObject *args)
{
    /* Parse the input tuple */
    char* fileName;
    char* p;
    char* c;
    char* h;
    char* e;
    char* d;
    char* f = NULL;
    char* l;
    char* i;
    int color;
    int mut;
    if (!PyArg_ParseTuple(args, "ssssssssii|s", &fileName, &p, &c, &h, &e,
     &d, &l, &i, &color, &mut, &f)) {
        return NULL;
    }

    int value = pathway_select(p, c, h, e, d, f, l, i, color, mut, fileName);
    // int value = hi();
    /* Build the output tuple */
    printf("letus return a value\n");
    PyObject *ret = Py_BuildValue("i", 1);
    return ret;
}