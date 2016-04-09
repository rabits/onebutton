#!/bin/sh

destroy() {
    trap '' INT TERM
    pkill guitarix
    sleep 2
    pkill jackd
    echo destruction done
}

export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/dbus/system_bus_socket

jackd -R -P89 -dalsa -dhw:1 -r44100 -p128 -n3 &

sleep 1
guitarix --nogui -p 8888 &

trap 'destroy' INT TERM

cat
