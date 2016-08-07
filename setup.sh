#!/bin/sh

# Presetup
sudo apt-get install git jackd2 python-yaml python-bluez python-cffi
sudo adduser onebutton

# Build guitarix
wget -O guitarix-0.35.1.tar.xz 'https://sourceforge.net/projects/guitarix/files/guitarix/guitarix2-0.35.1.tar.xz/download'
tar xvf guitarix-0.35.1.tar.xz
cd guitarix-0.35.1
sudo apt-get build-dep guitarix
./waf configure
./waf build
sudo ./waf install

# Setup onebutton system

# Sudo access for onebutton user to run button GPIO plugin
echo "onebutton ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/50-onebutton

# Add onebutton to audio & dialout groups to use soundcards & ttyUSB devices (displays)
sudo usermod -aG audio,dialout onebutton

# Lowering latencies to usb audio
echo "options snd-usb-audio nrpacks=1" | sudo tee -a /etc/modprobe.d/alsa-base.conf

# Adding moar inotify reads
echo "fs.inotify.max_user_watches = 524288" | sudo tee -a /etc/sysctl.conf

# Set defaults for the Maya22 sound device on connect
echo 'KERNEL=="hidraw*", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="2573", ATTRS{idProduct}=="0017", GROUP="onebutton", MODE="0660", RUN+="/srv/bin/maya22-control -d"' | sudo tee /etc/udev/rules.d/50-esi-maya22.rules

# Set rtc access to audio
if [ -e /dev/rtc0 ]; then
    echo 'KERNEL=="rtc0", MODE="0660", GROUP="audio"' | sudo tee /etc/udev/rules.d/51-rtc-audio.rules

    # Also you need to add next line in /etc/rc.local: "echo 3072 >/sys/class/rtc/rtc0/max_user_freq"
fi
