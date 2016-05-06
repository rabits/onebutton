OneButton
=========
It is portable guitar processor, based on Guitarix, Jackd and Linux.

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

Managing presets is carried out using Guitarix GUI interface or WEB interface. Later I think about preparing Qt+Bluetooth interface to manage everything with your PC or smartphone.

Additional features
-------------------
* Flexible audio mapping - you can control multiple audio interfaces and manage effects for a number of instruments
* Delayed actions - click and run sequence of actions with controllable delays
* Switch presets without pause and clicking
* No cut-off when swiching presets (for ex. delay & reverb processing last output)

Reference hardware
------------------
Right now I use the following hardware:
* Platform:
  * ODROID-C1+
  * ODROID-C2
* Audio:
  * ESI UGM96
  * ESI Maya22
* Rainbowduino 8x8 RGB led matrix
* Momentary soft-touch footswitch
* 3D printed case

But, you can ignore that, because RaspberryPI & any usb card with high-z input and line out can do the same thing.

Also GPIO is not required - just write small plugin python script and use any USB/UART/(interface)-driven buttons or controller for input/output interfaces.

Installation
------------
* Prepare your system to use realtime settings: http://github.com/raboof/realtimeconfigquickscan
* Clone onebutton repo
* Change config.yaml to suit your HW configuration
* Run `./onebutton config.yaml` and check logs that everything fine
* Rock & Roll!
* Optional: copy init script (upstart.conf) to run onebutton on system start

Donation
--------
If you great R&R man, you can support my open-source development by a small Bitcoin donation.

Bitcoin wallet: `15phQNwkVs3fXxvxzBkhuhXA2xoKikPfUy`
