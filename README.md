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
For sure you can use any number of buttons that you wish.

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

Managing presets is carried out using Guitarix GUI interface or WEB interface. Later I think about preparing Qt+Bluetooth interface to manage everything.

Reference hardware
------------------
Right now I use the following hardware:
* ODROID-C1+
* ESI Maya22 usb audio (connected to OTG, due to streaming issue with usb1.1 on odroid)
* 8x8 RGB led matrix & Rainbowduino
* Momentary soft-touch footswitch
* 3D printed case

But, you can ignore that, because RaspberryPI & any usb card with high-z input and line out can do the same thing.

Also GPIO is not required - just write small plugin python script and use any USB/UART/(interface)-driven buttons or controller for input/output interfaces.

Support
-------
If you great R&R man, you can support my open-source development by a small Bitcoin donation.

Bitcoin wallet: `15phQNwkVs3fXxvxzBkhuhXA2xoKikPfUy`
