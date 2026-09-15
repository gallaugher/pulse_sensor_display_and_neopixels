# Heart-rate monitor: PulseSensor + 4-digit display + NeoPixel heartbeat
# Board: YD-ESP32-S3 N16R8, CircuitPython 10.x
# Wiring: display G->GND, V->3V3, SDA->GPIO8, SCL->GPIO9
#         sensor  - ->GND, + ->3V3, S->GPIO2
#         pixels  red->5V, white->GND, green->GPIO15 (data-in end)
# Library: adafruit_ht16k33 folder in /lib (neopixel is built in)

import time
import board, busio, analogio, neopixel
from adafruit_ht16k33.segments import Seg7x4

# --- display ---
i2c = busio.I2C(board.GPIO9, board.GPIO8)      # SCL, SDA
display = Seg7x4(i2c, address=0x70)
display.brightness = 0.5
display.print("----")

# --- NeoPixel strand ---
NUM_PIXELS = 100
PIX_BRIGHT = 0.3          # 0.3 max on USB power; 0.5 is fine on the 5V 4A brick
pixels = neopixel.NeoPixel(board.GPIO15, NUM_PIXELS,
                           brightness=PIX_BRIGHT, auto_write=False)

pixels.fill((0, 0, 0)); pixels.show()
glow = 0.0                # 0..1, current red level
FADE = 0.90               # per-frame decay; lower = faster fade

# --- pulse sensor ---
pulse = analogio.AnalogIn(board.GPIO2) 

MIN_SWING  = 2200         # below this peak-to-peak, treat as "no finger"
REFRACTORY = 0.40         # seconds; ignores anything faster than ~150 bpm
HYST       = 0.12         # fraction of swing used as the hysteresis band

def read_raw(samples=8):
    total = 0
    for _ in range(samples):
        total += pulse.value
    return total // samples

# state
filt = read_raw()
sig_min, sig_max = filt, filt
armed = True
last_beat = 0.0
ibis = []
last_status = 0.0
last_display = 0.0
last_pixels = 0.0

while True:
    now = time.monotonic()
    raw = read_raw()
    if raw < 500 or raw > 65000:           # ADC glitch; skip this sample
        time.sleep(0.005)
        continue

    filt = (filt * 3 + raw) // 4

    sig_min = min(sig_min, filt); sig_min += (filt - sig_min) // 200
    sig_max = max(sig_max, filt); sig_max -= (sig_max - filt) // 200
    swing = sig_max - sig_min
    mid   = sig_min + swing // 2
    band  = int(swing * HYST)

    if swing >= MIN_SWING:
        if armed and filt > mid + band and (now - last_beat) > REFRACTORY:
            armed = False
            if last_beat:
                ibi = now - last_beat
                ok = 0.4 <= ibi <= 1.5
                if ok and len(ibis) >= 3:
                    avg = sum(ibis) / len(ibis)
                    ok = abs(ibi - avg) < 0.35 * avg
                if ok:
                    ibis.append(ibi)
                    ibis = ibis[-8:]
                    glow = 1.0                 # flash the strand on this beat
                    print(f"BEAT  ibi={ibi:.3f}s  inst={60/ibi:3.0f} bpm")
                else:
                    print(f"      (rejected ibi={ibi:.3f}s)")
            last_beat = now
        elif not armed and filt < mid - band:
            armed = True

    # NeoPixel throb: ~50 frames/s, red fades after each beat
    if now - last_pixels > 0.02:
        last_pixels = now
        if glow > 0.01:
            glow *= FADE
            pixels.fill((int(255 * glow), 0, 0))
        else:
            glow = 0.0
            pixels.fill((0, 0, 0))
        pixels.show()

    if now - last_status > 1.0:
        last_status = now
        print(f"raw={raw:5d} filt={filt:5d} min={sig_min:5d} max={sig_max:5d} "
              f"swing={swing:5d} armed={armed} beats={len(ibis)}")

    if now - last_display > 0.5:
        last_display = now
        if now - last_beat > 3:
            ibis = []
            display.print("----")
        elif len(ibis) < 4:
            display.print("----")
        else:
            bpm = int(60 / (sum(ibis) / len(ibis)))
            display.print(f"{bpm:4d}")
            print(f"        >>> BPM {bpm}")

    time.sleep(0.005)