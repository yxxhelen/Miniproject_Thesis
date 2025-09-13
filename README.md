# 2025 Fall ECE Senior Design Miniproject

# Raspberry Pi Pico 2W — Light Orchestra (Terminal-Controlled)

## Overview

The Light Orchestra utilizes a Raspberry Pi Pico 2W along with a resistor, green LED (currently for testing), a photoresistor, and a buzzer. The photoresistor recognizes a change in lighting, and the Pico sends respective PWM signals to the green LED and buzzer to turn the led on and play a melody. 

System is controlled in the Thonny terminal utilizing micropython. Has 'on', 'off', and '13' (this is for LED test purposes).
---

## Hardware Setup

* **Pico 2W Pins:**

  * Photoresistor → voltage divided with 1kohm resistance. Midpoint connected to **GP28 (ADC2)**
  * Piezo buzzer → **GP16 (PWM)**
  * Green LED → **GP13 (PWM capable)**, cathode to **GND**.

---

## Firmware Features

* **Calibration**: Determines the ambient light levels on startup.
* **Trigger logic**: When light detected by photoresistor, play melody and turn on LED.
* **Melody playback**: Plays random melody per activation (supposedly, sounds the same to us currently. will be worked on)

---

## Terminal Commands in Thonny

* `on` → Begins detecting light.
* `off` → Stop detecting light.
* `cal` → Recalibrate light baseline.
* `quit` → Halt program.
* `13` → Force **LED ON** at full brightness (debug).
* `13off` or `0` → Force **LED OFF** (debug).

---

## Operation

1. Save and Run `main.py` on the Pico 2W microcontroller.
2. System calibrates, then type 'on' in **Thonny** terminal.
   * If photoresistor detects a change in light, melody plays and LED lights up.
3. Use `off` to stop.

---

## Future Extensions

* Add RGB LED for different colors.
* Add distinct melodies for each color (?)


________________________________________________________________________________________________________________________________________________
[Project definition](./Project.md)

This project uses the Raspberry Pi Pico 2WH SC1634 (wireless, with header pins).

Each team must provide a micro-USB cable that connects to their laptop to plug into the Pi Pico.
The cord must have the data pins connected.
Splitter cords with multiple types of connectors fanning out may not have data pins connected.
Such micro-USB cords can be found locally at Microcenter, convenience stores, etc.
The student laptop is used to program the Pi Pico.
The laptop software to program and debug the Pi Pico works on macOS, Windows, and Linux.

This miniproject focuses on using
[MicroPython](./doc/micropython.md)
using
[Thonny IDE](./doc/thonny.md).
Other IDE can be used, including Visual Studio Code or
[rshell](./doc/rshell.md).

## Hardware

* Raspberry Pi Pico WH [SC1634](https://pip.raspberrypi.com/categories/1088-raspberry-pi-pico-2-w) (WiFi, Bluetooth, with header pins)
* Freenove Pico breakout board [FNK0081](https://store.freenove.com/products/fnk0081)
* Piezo Buzzer SameSky CPT-3095C-300
* 10k ohm resistor
* 2 [tactile switches](hhttps://www.mouser.com/ProductDetail/E-Switch/TL59NF160Q?qs=QtyuwXswaQgJqDRR55vEFA%3D%3D)

### Photoresistor details

The photoresistor uses the 10k ohm resistor as a voltage divider
[circuit](./doc/photoresistor.md).
The 10k ohm resistor connects to "3V3" and to ADC2.
The photoresistor connects to the ADC2 and to AGND.
Polarity is not important for this resistor and photoresistor.

The MicroPython
[machine.ADC](https://docs.micropython.org/en/latest/library/machine.ADC.html)
class is used to read the analog voltage from the photoresistor.
The `machine.ADC(id)` value corresponds to the "GP" pin number.
On the Pico W, GP28 is ADC2, accessed with `machine.ADC(28)`.

### Piezo buzzer details

PWM (Pulse Width Modulation) can be used to generate analog signals from digital outputs.
The Raspberry Pi Pico has eight PWM groups each with two PWM channels.
The [Pico WH pinout diagram](https://datasheets.raspberrypi.com/picow/PicoW-A4-Pinout.pdf)
shows that almost all Pico pins can be used for multiple distinct tasks as configured by MicroPython code or other software.
In this exercise, we will generate a PWM signal to drive a speaker.

GP16 is one of the pins that can be used to generate PWM signals.
Connect the speaker with the black wire (negative) to GND and the red wire (positive) to GP16.

In a more complete project, we would use additional resistors and capacitors with an amplifer to boost the sound output to a louder level with a bigger speaker.
The sound output is quiet but usable for this exercise.

Musical notes correspond to particular base frequencies and typically have rich harmonics in typical musical instruments.
An example soundboard showing note frequencies is [clickable](https://muted.io/note-frequencies/).
Over human history, the corresspondance of notes to frequencies has changed over time and location and musical cultures.
For the question below, feel free to use musical scale of your choice!


## Notes

Pico MicroPython time.sleep() doesn't error for negative values even though such are obviously incorrect--it is undefined for a system to sleep for negative time.
Duty cycle greater than 1 is undefined, so we clip the duty cycle to the range [0, 1].


## Reference

* [Pico 2WH pinout diagram](https://datasheets.raspberrypi.com/picow/pico-2-w-pinout.pdf) shows the connections to analog and digital IO.
* Getting Started with Pi Pico [book](https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf)
