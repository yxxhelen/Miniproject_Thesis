# main.py — Pico 2W: Terminal-controlled light trigger with single GREEN LED + melody
# Commands in Thonny Shell:  on | off | cal | quit
#
# Behavior:
#   - OFF: LED off, buzzer silent, baseline slowly updated to ambient.
#   - ON : If light rises above baseline by TRIGGER_DELTA, play a RANDOM melody.
#          Each note varies the GREEN LED brightness (PWM on GP13).

import sys, time
from machine import Pin, PWM, ADC
import uselect
try:
    import urandom as _rnd  # MicroPython
except:
    import random as _rnd   # fallback

# ---------- Pins ----------
ADC_PIN    = 28  # GP28 (ADC2) — LDR divider midpoint
BUZZER_PIN = 16  # GP16 PWM — piezo
GREEN_PIN  = 13  # GP13 PWM — GREEN LED via ~330Ω to anode, cathode to GND

# ---------- Hardware ----------
adc = ADC(ADC_PIN)

pwm_buzz = PWM(Pin(BUZZER_PIN)); pwm_buzz.freq(440); pwm_buzz.duty_u16(0)
#pwm_g = PWM(Pin(GREEN_PIN)); pwm_g.duty_u16(0)
pwm_g = PWM(Pin(GREEN_PIN)); pwm_g.freq(1000); pwm_g.duty_u16(0)


# ---------- Helpers ----------
def _clip01(x):
    try: x = float(x)
    except: return 0.0
    if x < 0: return 0.0
    if x > 1: return 1.0
    return x

def _rand01():
    try:
        return (_rnd.getrandbits(10) / 1023.0)
    except:
        return _rnd.random()

def set_green(bright01):
    """Set GREEN LED brightness (0..1)."""
    pwm_g.duty_u16(int(_clip01(bright01) * 65535))

def led_off():
    set_green(0.0)

def read_norm():
    raw = adc.read_u16() & 0xFFFF
    return raw / 65535.0

def set_silence():
    pwm_buzz.duty_u16(0)

def play_freq(freq_hz, duty01=0.5):
    if freq_hz <= 0 or duty01 <= 0:
        set_silence(); return
    pwm_buzz.freq(int(freq_hz))
    pwm_buzz.duty_u16(int(_clip01(duty01) * 65535))

def play_tone_ms(freq, ms, duty=0.45):
    play_freq(freq, duty)
    time.sleep_ms(max(0, int(ms)))
    set_silence()

# ---------- Melodies to pick randomly ----------
MELODY_REDish = [   # (names kept, but all use green LED now)
    {"freq": 392, "ms": 200}, {"freq": 392, "ms": 200},
    {"freq": 349, "ms": 200}, {"freq": 523, "ms": 340}
]
MELODY_GREEN  = [
    {"freq": 523, "ms": 180}, {"freq": 659, "ms": 180},
    {"freq": 784, "ms": 220}, {"freq": 659, "ms": 180}, {"freq": 523, "ms": 260}
]
MELODY_BLUEish = [
    {"freq": 494, "ms": 220}, {"freq": 587, "ms": 220},
    {"freq": 659, "ms": 320}, {"freq": 494, "ms": 300}
]
MELODY_ARP = [
    {"freq": 523, "ms": 180}, {"freq": 659, "ms": 180}, {"freq": 784, "ms": 300}
]
MELODIES = [MELODY_REDish, MELODY_GREEN, MELODY_BLUEish, MELODY_ARP]

def random_green_brightness(min_b=0.2, max_b=0.95):
    # avoid too dim; pick a visible random brightness
    return _clip01(min_b + (max_b - min_b) * _rand01())

def play_melody_with_green_pulses(notes, gap_ms=25, duty=0.45):
    for n in notes:
        f = int(n.get("freq", 0)); d = int(n.get("ms", 0))
        set_green(1.0)
        if f > 0 and d > 0:
            play_tone_ms(f, d, duty=duty)
        else:
            set_silence(); time.sleep_ms(max(0, gap_ms))
        time.sleep_ms(max(0, gap_ms))
    led_off()
    set_silence()

# ---------- Trigger logic ----------
TRIGGER_DELTA    = 0.05   # how much above baseline to count as "light detected"
BASELINE_ALPHA   = 0.02   # baseline update speed while OFF
IDLE_ALPHA       = 0.005  # baseline update speed while ON
COOLDOWN_MS      = 400    # wait after a melody
CHECK_PERIOD_MS  = 40     # sensor poll rate

# ---------- Terminal input (non-blocking) ----------
poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)
def read_cmd():
    if poll.poll(0):
        line = sys.stdin.readline()
        if line is None: return None
        return line.strip().lower()
    return None

print("\nPico 2W — Terminal-controlled GREEN LED + Melody on light")
print("Commands: on | off | cal | quit\n")

# Initialize baseline to ambient
baseline = read_norm()
state_on = False
last_trigger_ms = 0

def calibrate_baseline(samples=40, delay_ms=20):
    global baseline
    acc = 0.0
    for _ in range(samples):
        acc += read_norm()
        time.sleep_ms(delay_ms)
    baseline = acc / samples
    print("Baseline set to:", round(baseline, 3))

try:
    calibrate_baseline(samples=25, delay_ms=20)

    while True:
        # --- commands ---
        cmd = read_cmd()
        if cmd:
            if cmd in ("on", "start"):
                state_on = True
                print("[ON] light trigger active. Baseline:", round(baseline, 3))
            elif cmd in ("off", "stop"):
                state_on = False
                led_off(); set_silence()
                print("[OFF] idle; updating baseline slowly.")
            elif cmd in ("cal", "recal", "calibrate"):
                calibrate_baseline()
            elif cmd == "13":
                set_green(1.0)
                print("GP13 LED ON (100%)")
            elif cmd in ("13off", "0"):
                led_off()
                print("GP13 LED OFF")
            elif cmd in ("quit", "exit"):
                print("Exiting…")
                break
            else:
                print("Unknown command. Use: on | off | cal | 13 | 13off | quit")

        # --- sensor read ---
        norm = read_norm()

        if not state_on:
            baseline = (1 - BASELINE_ALPHA) * baseline + BASELINE_ALPHA * norm
            time.sleep_ms(CHECK_PERIOD_MS)
            continue

        # ON: compute delta vs baseline & adapt baseline slowly
        delta = norm - baseline
        baseline = (1 - IDLE_ALPHA) * baseline + IDLE_ALPHA * norm

        # cooldown
        now = time.ticks_ms()
        in_cooldown = time.ticks_diff(now, last_trigger_ms) < COOLDOWN_MS

        if (delta >= TRIGGER_DELTA) and not in_cooldown:
            last_trigger_ms = now
            mel = MELODIES[int(_rand01() * len(MELODIES)) % len(MELODIES)]
            play_melody_with_green_pulses(mel, gap_ms=25, duty=0.48)
            time.sleep_ms(80)  # settle
        else:
            # idle ON: LED off, no sound
            led_off()
            set_silence()
            time.sleep_ms(CHECK_PERIOD_MS)

except KeyboardInterrupt:
    print("\nKeyboardInterrupt")
finally:
    led_off()
    set_silence()



