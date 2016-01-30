#include <Python.h>

#include <wiringPi.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

#define MAX_BUTTONS 10

typedef struct {
    int8_t pin;
    uint8_t value;
    PyObject *callback;
} Button;

Button buttons[MAX_BUTTONS];
uint8_t buttons_num = 0;

static void interrupt(void) {
    PyObject *arglist;
    PyObject *result = NULL;

    PyGILState_STATE state = PyGILState_Ensure();
    for( int i=0; i<MAX_BUTTONS; i++ ) {
        if( buttons[i].pin < 0 )
            continue;

        uint8_t val = digitalRead(buttons[i].pin);
        if( buttons[i].value != val ) {
            buttons[i].value = val;
            arglist = Py_BuildValue("(b)", val);

            // To call it from non-python thread you need PyGILState_* & PyEval_InitThreads
            // https://gist.github.com/liuyu81/3473376
            result = PyObject_CallObject(buttons[i].callback, arglist);

            Py_XDECREF(result);
            Py_DECREF(arglist);
        }
    }
    PyGILState_Release(state);
}

static PyObject* setup(PyObject* self, PyObject* args)
{
    if( wiringPiSetup() < 0 ) {
        printf("Unable to setup wiringPi\n");
        return NULL;
    }
    for( int i=0; i<MAX_BUTTONS; i++ ) {
        buttons[i].pin = -1;
        buttons[i].callback = NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* addButton(PyObject* self, PyObject* args)
{
    uint8_t pin = 0;
    PyObject *temp;
    PyObject *result = NULL;

    if( (buttons_num + 1) >= MAX_BUTTONS ) {
        PyErr_SetString(PyExc_TypeError, "too much buttons registered here");
        return NULL;
    }

    if( !PyArg_ParseTuple(args, "bO", &pin, &temp) ) {
        PyErr_SetString(PyExc_TypeError, "wrong parameters (uchar, func)");
        return NULL;
    }

    if( !PyCallable_Check(temp) ) {
        PyErr_SetString(PyExc_TypeError, "second parameter should be callable");
        return NULL;
    }
    // Get first empty buttons slot
    long num;
    for( num = 0; num<MAX_BUTTONS; num++ ) {
        if( buttons[num].pin < 0 )
            break;
    }

    buttons_num++;
    Py_XINCREF(temp);
    pinMode(pin, INPUT);
    buttons[num].pin = pin;
    buttons[num].value = digitalRead(pin);
    buttons[num].callback = temp;

    if( wiringPiISR(pin, INT_EDGE_FALLING, &interrupt) < 0 ) {
        PyErr_SetString(PyExc_TypeError, "unable to setup ISR");
        return NULL;
    }

    Py_INCREF(Py_None);
    result = Py_None;

    return result;
}

static PyObject* delButton(PyObject* self, PyObject* args)
{
    uint8_t pin = 0;

    if( !PyArg_ParseTuple(args, "b"), &pin )
        return NULL;

    long num;
    for( num = 0; num<MAX_BUTTONS; num++ ) {
        if( buttons[num].pin == pin )
            break;
    }

    if( num >= MAX_BUTTONS )
        return NULL;

    buttons[num].pin = -1;
    Py_XDECREF(buttons[num].callback);
    buttons[num].callback = NULL;
    buttons_num--;
    pinMode(pin, OUTPUT);
    pinMode(pin, INPUT);
}

static PyMethodDef ButtonMethods[] =
{
     {"setup", setup, METH_NOARGS, "Setup wiringpi to process buttons"},
     {"addButton", addButton, METH_VARARGS, "Add button to the list of processing buttons with interrupt args:(pin, callback)"},
     {"delButton", delButton, METH_VARARGS, "Remove button from the list of processing buttons args:(pin)"},
     {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initbuttonmodule(void)
{
     (void) Py_InitModule("buttonmodule", ButtonMethods);
     PyEval_InitThreads();
}
