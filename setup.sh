#!/bin/sh
# Setup onebutton system

# Lowering latencies to usb audio
echo "options snd-usb-audio nrpacks=1" | sudo tee -a /etc/modprobe.d/alsa-base.conf

# Set defaults for the Maya22 sound device on connect
echo 'KERNEL=="hidraw*", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="2573", ATTRS{idProduct}=="0017", GROUP="onebutton", MODE="0660", RUN+="/srv/bin/maya22-control -d"' | sudo tee /etc/udev/rules.d/50-esi-maya22.rules
