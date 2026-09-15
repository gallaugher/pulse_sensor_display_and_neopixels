# Heart-Rate Monitor with 7-Segment Display & NeoPixel Heartbeat (ESP32-S3, CircuitPython)

Rest a fingertip on a pulse sensor and your heart rate appears on a 4-digit LED display while a string of NeoPixels throbs red on every beat. The whole build runs from the ESP32-S3's 3.3 V pin over USB power: no soldering on the ESP32, no external power supply, no level shifter, and the only library is `adafruit_ht16k33`.
## Demo video

[![Heart-rate monitor demo — ESP32-S3, 7-segment display, and a NeoPixel heartbeat](https://img.youtube.com/vi/s4pY4Ej6lgY/maxresdefault.jpg)](https://youtu.be/s4pY4Ej6lgY)

*Click the image to watch on YouTube.*

The pulse sensor is a plain analog part. CircuitPython reads it with `analogio`, and the beat detection (an adaptive threshold with hysteresis, a refractory period, and outlier rejection) is about thirty lines of Python in `code.py`, so students can see exactly how a heartbeat becomes a number.

## Parts List

| Part | Notes | Where |
|---|---|---|
| ESP32-S3 DevKitC-1 N16R8 (YD-ESP32-S3 compatible) with headers, plus screw-terminal / socket expansion board | 2-pack; flash the "YD-ESP32-S3 N16R8" CircuitPython build once | [Amazon (QIQIAZI 2-pack)](https://a.co/d/02ooVs7D) |
| PulseSensor-style analog pulse sensor (3 wires: −, +, S) | Ships without headers; solder the included 3-pin header or three short wires to the −, +, S pads. Put tape over the solder side. | [Amazon (FainWan 3-pack)](https://a.co/d/00ApR3Hj) or [Adafruit 1093](https://www.adafruit.com/product/1093) |
| 4-digit 7-segment I2C display module, HT16K33 / VK16K33, address 0x70 | Has a 4-pin JST-PH socket and G / V / SDA / SCL pads | [Amazon (HT16K33 2-pack)](https://www.amazon.com/s?k=HT16K33+0.56+4+digit+7+segment+I2C+display+module) or [Adafruit 5599 (STEMMA QT)](https://www.adafruit.com/product/5599) |
| WS2811/WS2812 NeoPixel string, 100 pixels (or any length, edit `NUM_PIXELS`) | Seed/pebble string, 3 wires: red 5V, white GND, green data. Runs fine at 3.3 V. | [AliExpress (HarrisonTek seed string)](https://www.aliexpress.us/item/3256806860912354.html) or any WS2812B strip |
| Jumper wires: 4 M-M (display cable to adapter), 3 M-F (sensor), 3 for the strand | | [Amazon (Aypzuke 240-pc kit)](https://a.co/d/0h3WT8NL) |
| USB-A to USB-C **data** cable | Plug into the port labeled **USB** (native port), not COM | |

## Wiring

Everything runs from 3.3 V. The adapter's screw terminals and the socket row behind them are the same connections, so use whichever is handier; the two 3V3 terminals and 3V3 sockets are all one supply.

| Part | Pin on part | ESP32-S3 |
|---|---|---|
| Display | G | GND |
| | V | 3V3 |
| | SDA | GPIO8 |
| | SCL | GPIO9 |
| Pulse sensor | − | GND |
| | + | 3V3 |
| | S | GPIO2 |
| NeoPixel string | red | 3V3 |
| | white | GND |
| | green (data-in end) | GPIO15 |

Do not power the display from 5 V: its I2C pull-ups would lift SDA/SCL to 5 V, and the ESP32-S3 is not 5 V tolerant. (On a stock YD-ESP32-S3 the 5V pin is input-only anyway; it carries nothing on USB power unless the IN-OUT solder jumper is bridged.)

## Setup

1. Install CircuitPython 10.x (the "YD-ESP32-S3 N16R8" build) via the [circuitpython.org web installer](https://circuitpython.org/board/yd_esp32_s3_n16r8/): hold BOOT, tap RST, release BOOT, then run the installer. Plug into the **USB** port afterward; CIRCUITPY only appears there.
2. Copy the `adafruit_ht16k33` folder from the [CircuitPython library bundle](https://circuitpython.org/libraries) into `CIRCUITPY/lib/`. (`neopixel` is built into this board's firmware.)
3. Copy `code.py` from this repo to `CIRCUITPY/`.
4. Open a serial console (Mu, Thonny, or `screen`) to watch the detector.

## Using it

Put the sensor on the table, tape side down, green LED up. Rest the pad of your index finger on the LED with just the weight of the finger — don't press. Keep your hand flat and still. The display shows `----` for the first few seconds while the amplifier settles, then your heart rate appears and the NeoPixels flash red on each beat. Lift your finger and the display returns to `----` after three seconds.

Tips: pressing hard squeezes the blood out of the fingertip and kills the signal; bright room light leaking under the finger adds noise (cup your other hand over it); a strip of velcro or a hair tie holding the sensor to the fingertip gives the steadiest readings; an earlobe with a padded clip works too.

## What the console shows

```
raw=21045 filt=20490 min=20269 max=26431 swing= 6162 armed=True beats=5
BEAT  ibi=0.702s  inst= 85 bpm
        >>> BPM 85
```

`swing` is the peak-to-peak size of the pulse waveform: roughly 1,000 with no finger (ADC noise), 4,000–7,000 with good contact. `BEAT` lines are accepted beats with their inter-beat interval; `(rejected ...)` lines are beats that didn't fit the recent rhythm. The displayed BPM is the average of the last eight accepted beats.

## Tuning knobs (top of `code.py`)

| Constant | Default | What it does |
|---|---|---|
| `NUM_PIXELS` | 100 | Length of your string |
| `PIX_BRIGHT` | 0.2 | Pixel brightness. 100 pixels on the 3.3 V regulator: keep ≤ 0.2 (0.15 if the board resets on a beat). Fewer pixels can go brighter. |
| `FADE` | 0.90 | How fast the red fades after each beat (0.95 = longer glow) |
| `MIN_SWING` | 2200 | Below this peak-to-peak, treat as "no finger". Set it between your no-finger and with-finger `swing` values. |
| `REFRACTORY` | 0.40 | Minimum seconds between beats (~150 bpm max) |
| `HYST` | 0.12 | Hysteresis band as a fraction of swing; raise toward 0.18 if you see double-triggers |

## Extensions

- Color by rate: blue below 60, green 60–100, red above 100.
- Send the BPM over Wi-Fi to Adafruit IO or a webhook.
- Swap the 7-segment display for the 2.4" ILI9341 TFT and draw the waveform.
- Add the `adafruit_ht16k33` colon blink as a second heartbeat indicator.

## Files

- `code.py` — the full program
- `strand-test.py` — lights the onboard RGB LED and the string red/blue to check wiring before running the monitor
