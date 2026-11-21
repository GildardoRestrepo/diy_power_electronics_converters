---
title: Gate bus interface specification
type: reference
---
# Gate bus interface specification

> [!NOTE]
> Electrical and mechanical definition of the cable that connects the gating block to any converter box (buck, boost, inverter). One connector, one pinout, one cable: a box works as soon as it is plugged in.

## 1. Connector and cable

| Item | Specification |
| ---- | ------------- |
| Connector | 2×8 shrouded box header, 2.54 mm pitch, with polarising key (IDC-16) |
| Cable | 16-way flat ribbon, 28 AWG, two IDC sockets, $0.3$–$1.0\,\mathrm{m}$, straight-through (pin 1 to pin 1) |
| Orientation | Pin 1 marked on the silkscreen and on the enclosure; key notch towards the board edge |
| Hot-plugging | Allowed only with the gating block in STOP |

---
## 2. Pinout

| Pin | Signal | Direction (block → box) | Description |
| --- | ------ | ----------------------- | ----------- |
| 1 | `+12V` | → | Auxiliary supply for the isolated gate supplies, $\leq 0.6\,\mathrm{A}$ per box |
| 2 | `+12V` | → | paired with pin 1 |
| 3 | `GND` | — | Logic and 12 V return |
| 4 | `GND` | — | |
| 5 | `PWM1` | → | Gate command, leg A upper switch (buck, boost: the only switch) |
| 6 | `PWM2` | → | Leg A lower switch |
| 7 | `PWM3` | → | Leg B upper |
| 8 | `PWM4` | → | Leg B lower |
| 9 | `PWM5` | → | Leg C upper |
| 10 | `PWM6` | → | Leg C lower |
| 11 | `FAULT` | ← | Open-collector, active low; box pulls low on over-current / over-voltage. Pull-up $4.7\,\mathrm{k\Omega}$ to $3.3\,\mathrm{V}$ in the block |
| 12 | `EN` | → | High while the block's outputs are enabled (lights the "armed" LED on the box) |
| 13 | `+5V` | → | Logic supply for future boxes, $\leq 0.1\,\mathrm{A}$; unused by the current boards |
| 14 | `GND` | — | |
| 15 | `GND` | — | |
| 16 | `GND` | — | |

Odd pins are on one row of the header, even pins on the other, so the pairs `PWM1`/`PWM2`, `PWM3`/`PWM4`, `PWM5`/`PWM6` sit face to face across the ribbon; `GND` on 3/4 and 14/15/16 bounds the signal group.

---
## 3. Electrical levels

| Parameter | Value |
| --------- | ----- |
| `PWMx`, `EN` logic | $5\,\mathrm{V}$ CMOS (74HCT541); $V_{OH} \geq 3.84\,\mathrm{V}$ at $6\,\mathrm{mA}$, $V_{OL} \leq 0.33\,\mathrm{V}$ |
| `PWMx` load in the box | $270\,\Omega$ + optocoupler LED ($7$–$13\,\mathrm{mA}$); $10\,\mathrm{k\Omega}$ pull-down in the block |
| Disabled state | Outputs tri-state; pull-downs hold every channel low (switch off) |
| `FAULT` | Open collector (PC817 phototransistor), $V_{OL} \leq 0.4\,\mathrm{V}$ at $1\,\mathrm{mA}$; wired-OR between boxes is allowed |
| `+12V` | $12\,\mathrm{V} \pm 10\,\%$, $\leq 1\,\mathrm{A}$ total on the bus |
| Isolation | None in the cable. All isolation (optocouplers, isolated DC/DC) is on the converter boards. The bus GND is the gating block's logic ground and may be earthed by the USB cable of the ESP32 |

---
## 4. Channel use per box

| Box | Channels used | Pairing | Default dead time |
| --- | ------------- | ------- | ----------------- |
| Buck | `PWM1` | none (single switch) | — |
| Boost | `PWM1` | none | — |
| Inverter | `PWM1`…`PWM6` | (1,2), (3,4), (5,6) complementary | $1.5\,\mathrm{\mu s}$ |
| Half-bridge / chopper experiments (future) | `PWM1`, `PWM2` | (1,2) | $1.5\,\mathrm{\mu s}$ |

The gating block never assumes which box is attached; the operator selects the mode. A wrong mode cannot damage a box: an unused channel simply has no driver populated, and the box protections act on `FAULT`.

---
## 5. Converter-side reference circuit (one channel)

```
PWMx ──► 270 Ω ──► HCPL-3120 pin 2 (anode)
GND  ──────────────► HCPL-3120 pin 3 (cathode)
                     pin 8 VCC ◄── +15 V_iso (TMA-1215S, 10 µF + 100 nF)
                     pin 5 VEE ◄── emitter / source of the switch
                     pins 6-7 VO ──► 22 Ω ──► gate   (10 kΩ gate–emitter)
```

Protection return:

```
+15 V_iso ──► 1.5 kΩ ──► PC817 LED anode
LM393 open-collector outputs (OC, OV, wired-OR) ──► PC817 LED cathode
PC817 collector ──► FAULT (pin 11)      PC817 emitter ──► GND (pin 3)
```

The `EN` line drives a green LED (1 kΩ) on each box so the operator can see that the block is armed before touching anything.

---
## 6. Mechanical

The box header is mounted on the PCB at the board edge, accessible through a slot in the enclosure; the ribbon exits the box at the same side as the low-voltage signal test points and away from the power terminals. Creepage from any bus pin to a power net on the PCB is at least $6\,\mathrm{mm}$ (reinforced-insulation distance for $300\,\mathrm{V}$ DC, pollution degree 2), implemented by the isolation gap under the optocouplers and DC/DC modules.

---
## Links
- [Gating block signal budget](../05_gating_block/10_math/51_signal_budget.md)
- [Architecture decisions](architecture.md)
- [Project README](../README.md)
