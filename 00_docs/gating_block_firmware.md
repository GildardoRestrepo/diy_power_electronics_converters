---
title: "Gating block firmware specification"
type: reference
---
# Gating block firmware specification

> [!NOTE]
> What the ESP32 firmware of the gating block must do so that the box behaves like PSIM's gating block: operating modes, menu, safety behaviour and the pin map of the PCB. Target: Arduino IDE (ESP32 core 3.x, MCPWM driver) or ESP-IDF.

## 1. Pin map (ESP32-DevKitC V4 on the gating block PCB)

| Function | GPIO | Direction | Note |
| -------- | ---- | --------- | ---- |
| PWM1 … PWM6 | 25, 26, 27, 14, 13, 23 | out | to 74HCT541 A0…A5; pairs (1,2), (3,4), (5,6) are legs A, B, C |
| EN (bus) | 4 | out | high while outputs are active; through the buffer to the boxes |
| SYNC | 32 | out | one pulse at the start of each fundamental period (scope trigger) |
| FAULT | 34 | in (interrupt, falling) | open-collector from the boxes, 4.7 kΩ pull-up; also disables the buffer in hardware |
| RUN_SW | 35 | in | panel RUN/STOP switch (low = RUN); it also drives the buffer enable in hardware |
| ENC_A, ENC_B, ENC_SW | 18, 19, 5 | in | rotary encoder with push button |
| BTN1 (BACK), BTN2 (RESET) | 33, 36 | in | active low |
| SDA, SCL | 21, 22 | I2C | 0.96" OLED, SSD1306 at 0x3C |
| LED_RUN, LED_FLT | 2, 16 | out | front-panel LEDs |
| SPARE | 17 | — | header J6 |

The buffer's output enables are hardware-gated: with RUN_SW open or FAULT low, no firmware state can turn a channel on.

---
## 2. Operating modes

| Mode | Channels | Parameters | Behaviour |
| ---- | -------- | ---------- | --------- |
| **PWM** (buck / boost) | PWM1 | $f_{sw}$ 0.1 Hz–200 kHz, $D$ 0–100 %, soft-start time | Single channel; $D$ ramps from 0 to the set value over the soft-start time (default 0.5 s) |
| **Half bridge** | PWM1, PWM2 | $f_{sw}$, $D$, dead time | Complementary pair with dead time on both edges |
| **Three-phase SPWM** | PWM1…6 | $f_1$ 0.1–400 Hz, $f_{sw}$, $m_a$ 0–1.15, dead time, $V/f$ ramp | Three sine references 120° apart, asynchronous carrier; above $m_a = 1$ overmodulation |
| **Six-step** | PWM1…6 | $f_1$, dead time | 180° conduction, each switch on for half a period |
| **120° square** | PWM1…6 | $f_1$ | 120° conduction, two switches on at any time |
| **Gating table** (PSIM style) | any | $f_1$, list of switching angles per channel | Each channel toggles at the listed angles (0–360°), repeated every fundamental period: reproduces PSIM's *Gating Block* file format |

Common limits: minimum pulse width 1 µs, dead time 0.2–5 µs (defaults 1.5 µs IGBT / 0.8 µs MOSFET), parameter changes applied at the next carrier period without glitches.

---
## 3. State machine

```
POWER_ON -> IDLE (outputs off, EN low)
IDLE --[RUN_SW closed + encoder "Start"]--> SOFT_START -> RUNNING (EN high, LED_RUN on)
RUNNING --[RUN_SW opened]--> IDLE
RUNNING --[FAULT low]--> FAULT_LATCHED (outputs off, EN low, LED_FLT on, display shows cause)
FAULT_LATCHED --[BTN2 RESET with FAULT high]--> IDLE
```

- The FAULT interrupt stops the MCPWM timers and forces all PWM pins low in < 10 µs; the hardware path has already tri-stated the buffer.
- Changing mode is only allowed in IDLE. Changing $D$, $m_a$ or frequencies is allowed while RUNNING (live tuning, the purpose of the box).
- On every start the duty cycle or modulation index ramps from zero (soft start) unless the operator disables it in the setup menu.

---
## 4. User interface

OLED 128×64 with a three-line layout: mode and state on line 1, the parameter being edited on line 2 (large font), and the remaining parameters on lines 3–4. Encoder rotation changes the highlighted value with acceleration; push selects or enters; BACK returns one level. Long press on the encoder opens *Setup* (dead-time default, soft-start time, display units, save as default). Parameters persist in NVS (flash) and are restored at boot, except the RUN state, which always starts in IDLE.

---
## 5. Implementation notes

- Use the MCPWM peripheral: timer per leg, two generators per leg for the complementary pair, dead-time module for both edges, sync between the three timers for the three-phase modes. 80 MHz timer clock gives 12.5 ns resolution.
- Sine table of 256 entries in flash; the duty update runs in the timer-period interrupt (three multiplies per carrier period).
- The gating-table mode uses a hardware timer at 1 µs resolution and a sorted event list; angles are quantised to the fundamental period divided by 65 536.
- Watchdog: a task watchdog of 1 s; on expiry the outputs are disabled before the reset.
- Serial console (115200 baud) mirrors the display and accepts the same parameters as text commands, so a PC script can run a sweep (e.g. duty from 0.2 to 0.6 in 0.05 steps while a scope captures).

---
## Links
- [Gating block signal budget](../05_gating_block/10_math/51_signal_budget.md)
- [Gate bus interface](gate_bus_interface.md)
- [Project README](../README.md)
