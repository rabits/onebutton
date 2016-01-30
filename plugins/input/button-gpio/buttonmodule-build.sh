#!/bin/sh

gcc -std=c11 -c buttonmodule.c -fPIC -I/usr/include/python2.7/
gcc -shared buttonmodule.o -L/usr/lib/python2.7 -lpython2.7 -lwiringPi -lpthread -o buttonmodule.so
rm -f buttonmodule.o
