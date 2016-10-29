OneButton
=========
It is portable guitar processor, based on Guitarix, Jackd and Linux.

| BoneButton | TankButton |
| ---------- | ---------- |
| <img src="/doc/bonebutton-body-3d.jpg" width="200"> | <img src="/doc/tankbutton-body-3d.jpg" width="200"> |
| <img src="/doc/bonebutton-body-live.jpg" width="200"> | na |

Main idea
---------
DIY opensource guitar processor with one button, simple display and infinity ways for customization.

One footswitch can control each element in your stompbox, simple config for ex:
```
Init (switch to Rythm preset & display "R" letter) --> Click (switch to Solo preset & show "Skull" animation) --> Click (goto Init)
Init (Tuner off) --> Longpush (Tuner on & Mute output) --> Longpush (goto Init)
```
If you'd like to use additional buttons - just connect it (GPIO, USB, etc) and change hw configuration of pedal.

And any action can be used as a part of step in this live graph:
* Enable looper rec
* Change effect value
* Switch graph for click/longpush
* Go to specific graph position or back
* Any custom action that you can imagine!

About display: to show some info about current state you can use number of options:
* Led line with > 2 leds
* Led matrix
* Text display
* Graphical display
* Etc...

Managing presets is carried out using Guitarix GUI interface or WEB interface.

Additional features
-------------------
* Flexible audio mapping - you can control multiple audio interfaces and manage effects for a number of instruments
* Delayed actions - click and run sequence of actions with controllable delays
* Switch presets without pause and clicking
* No cut-off when swiching presets (for ex. delay & reverb processing last output)

Target platform
---------------
It is possible to run on any linux distributive, but current target platform is Ubuntu 16.04.

Reference hardware
------------------
Right now I use the following hardware:
* Platform:
  * ODROID-C2
    + CPU: 4x 2GHz 64bit
    + RAM: 2GB
    + eMMC + MicroSD
    + 4x USB + OTG
* Audio:
  * ESI UGM96
  * ESI Maya22
* USB Bluetooth 4.0 dongle
* Rainbowduino 8x8 RGB led matrix
* Momentary soft-touch footswitch
* 3D printed case

But, you can ignore that, because RaspberryPI & any usb card with high-z input and line out can do the same thing.

Also GPIO is not required - just write small plugin python script and use any USB/UART/(interface)-driven buttons or controller for input/output interfaces.

Not recommended
---------------
* Platforms:
  * ODROID-C1+ - buggy USB (but OTG ok) can cause kernel freezes
    + CPU: 4x 1.5GHz 32bit
    + RAM: 1GB
    + eMMC + MicroSD
    + 4x USB + OTG

Installation
------------
* Clone onebutton repo
* Install guitarix & made some changes from setup.sh
* Prepare your system to use realtime settings: http://github.com/raboof/realtimeconfigquickscan
* Change config.yaml to suit your HW configuration
* Go to plugins directory and build required plugins
* Run `./onebutton config.yaml` and check logs that everything fine
* Rock & Roll!
* Optional: copy init script (upstart.conf, systemd.service) to run onebutton on system start

Bluetooth
---------
You can manage your onebutton by using the OneControl application, but make sure that you're use bluez>=5.40 - dbus bluez profiles working properly with it.
OneControl you can find here: http://github.com/rabits/onecontrol

Guitarix WEB UI
---------------
To manage Guitarix OneButton support webui interface, that placed in guitarix-webui folder. It will be used after Guitarix startup.

TODO
----
* Platforms:
  * Banana Pi M3
    + CPU: 8x 1.8GHz
    + RAM: 2GB
    + 2 USB + OTG
    + SATA + int eMMC 8Gb + MicroSD
    + WiFi(n)
    + Bluetooth(4.0)
  * Banana Pi M2+
    + CPU: 4x 1.2GHz
    + RAM: 1GB
    + 2 USB + OTG
    + int eMMC 8Gb + MicroSD
    + WiFi(n)
    + Bluetooth(4.0)
  * Raspberry Pi 3B
    + CPU: 4x 1.2GHz 64bit
    + RAM: 1GB
    + 4 USB + OTG
    + WiFi(n)
    + Bluetooth(4.1+BLE)

Donation
--------
If you are great R&R man, you can support my open-source development by a small Bitcoin donation.

Bitcoin wallet: `15phQNwkVs3fXxvxzBkhuhXA2xoKikPfUy`
