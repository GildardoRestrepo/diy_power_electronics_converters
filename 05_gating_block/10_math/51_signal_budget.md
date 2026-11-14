---
title: "Gating block: signal, timing and power budget"
created: 2026-11-13
time: ""
creator: "Fable 5.1"
last update: 2026-11-13
update by: "Fable 5.1"
type: calculation
status: draft
stage: 1
area: control
editor: "Gilbert"
order: 1
tags:
  - type/calculation
---
# Gating block: signal, timing and power budget

> [!NOTE]
> Sizing of the external gating block (the physical version of PSIM's gating block): logic levels and LED currents on the gate bus, propagation delays and the dead time they impose, PWM resolution of the ESP32, and the 12 V / 5 V power budget for one block driving up to one inverter box.

## 1. Signal chain

```
ESP32 (3.3 V GPIO) ─► 74HCT541 (5 V buffer, output enable) ─► gate bus (ribbon, ≤ 1 m)
   ─► converter box: 270 Ω ─► HCPL-3120 LED ─► isolated 15 V driver ─► Rg = 22 Ω ─► IGBT gate
```

The gating block only produces 5 V logic; all isolation and gate power is on the converter boards. One cable carries the six PWM channels, the enable, the fault return and the 12 V that powers the isolated gate supplies.

---
## 2. Logic levels and LED current

| Stage | Parameter | Value | Source |
| ----- | --------- | ----- | ------ |
| ESP32 output | $V_{OH,min}$ at $3.3\,\mathrm{V}$ | $2.64\,\mathrm{V}$ | ESP32 datasheet ($0.8\,V_{DD}$) |
| 74HCT541 input | $V_{IH,min}$ at $5\,\mathrm{V}$ | $2.0\,\mathrm{V}$ | TTL-compatible input: accepts 3.3 V logic |
| 74HCT541 output | $V_{OH}$ at $I_{OH} = 6\,\mathrm{mA}$ / typical at $12\,\mathrm{mA}$ | $3.84\,\mathrm{V}$ min / $\approx 4.3\,\mathrm{V}$ | 74HCT541 datasheet |
| HCPL-3120 LED | $V_F$ at $10\,\mathrm{mA}$ | $1.5\,\mathrm{V}$ typ, $1.95\,\mathrm{V}$ max | Broadcom datasheet |
| HCPL-3120 LED | recommended $I_F$ | $7$–$16\,\mathrm{mA}$ | Broadcom datasheet |

Series resistor on the converter board, $R_{LED} = 270\,\Omega$:

$$
I_{F,typ} = \frac{4.3 - 1.5}{270} = 10.4\,\mathrm{mA}
\qquad
I_{F,min} = \frac{3.84 - 1.95}{270} = 7.0\,\mathrm{mA}
\qquad
I_{F,max} = \frac{5.0 - 1.5}{270} = 13\,\mathrm{mA}
$$

All within the recommended window; the worst case still exceeds the $I_{FLH}$ turn-on threshold ($2.5\,\mathrm{mA}$ max) by a factor of 2.8. The 74HCT541 sources up to $6 \times 13 = 78\,\mathrm{mA}$ with all six channels on, below its $70\,\mathrm{mA}$ continuous $V_{CC}$/GND limit only if no more than five are on simultaneously at 100 % duty, which never happens with complementary pairs (at most three channels on at any instant: $39\,\mathrm{mA}$).

When the outputs are disabled (tri-state) the $10\,\mathrm{k\Omega}$ pull-downs on each channel keep the LEDs off ($< 0.5\,\mathrm{mA}$ leakage path).

---
## 3. Timing: delays, skew and dead time

| Element | Delay (typ / max) | Note |
| ------- | ----------------- | ---- |
| ESP32 MCPWM output | $\leq 25\,\mathrm{ns}$ | GPIO matrix |
| 74HCT541 | $14 / 25\,\mathrm{ns}$ | |
| Ribbon cable ($1\,\mathrm{m}$) | $5\,\mathrm{ns}$ | |
| HCPL-3120 $t_{PLH}$, $t_{PHL}$ | $0.3 / 0.5\,\mathrm{\mu s}$ | |
| HCPL-3120 pulse-width distortion | $\leq 0.3\,\mathrm{\mu s}$ | $\lvert t_{PHL} - t_{PLH} \rvert$ |
| HCPL-3120 skew between two parts | $\leq 0.35\,\mathrm{\mu s}$ | $t_{PSK}$ |
| IGBT IRG4PC40UD turn-off ($t_{d(off)} + t_f$) | $0.4 / 0.6\,\mathrm{\mu s}$ | at $R_g = 22\,\Omega$, hot |
| IGBT turn-on ($t_{d(on)} + t_r$) | $0.1\,\mathrm{\mu s}$ | |

Minimum dead time for a half-bridge leg: the upper switch must be fully off before the lower turns on, in the worst combination of driver skew and device delays:

$$
t_{d,min} = t_{PSK} + t_{off,max} - t_{on,min} \approx 0.35 + 0.6 - 0.1 = 0.85\,\mathrm{\mu s}
$$

**Selected dead time: $1.5\,\mathrm{\mu s}$ for IGBTs, $0.8\,\mathrm{\mu s}$ for MOSFETs**, configurable from $0.2$ to $5\,\mathrm{\mu s}$ in the menu. The pulse-width distortion of $0.3\,\mathrm{\mu s}$ shifts the effective duty cycle by $0.3\,\mathrm{\mu s} \cdot f_{sw}$: $0.6\,\%$ at $20\,\mathrm{kHz}$, visible in the open-loop output voltage; this is the dominant systematic error of the chain and sets the minimum usable pulse width ($\geq 1\,\mathrm{\mu s}$).

---
## 4. PWM resolution and frequency range (ESP32 MCPWM)

The MCPWM peripheral runs from $160\,\mathrm{MHz}$ with a prescaler, giving a timer resolution of $12.5\,\mathrm{ns}$ at $80\,\mathrm{MHz}$ timer clock and a 16-bit period counter:

| $f_{sw}$ | Period counts at $80\,\mathrm{MHz}$ | Duty resolution |
| -------- | ----------------------------------- | --------------- |
| $1\,\mathrm{kHz}$ | $80\,000$ → prescale 2 ($40\,000$) | $0.0025\,\%$ |
| $20\,\mathrm{kHz}$ | $4\,000$ | $0.025\,\%$ |
| $50\,\mathrm{kHz}$ | $1\,600$ | $0.063\,\%$ |
| $200\,\mathrm{kHz}$ | $400$ | $0.25\,\%$ |

Dead time is inserted by the MCPWM dead-time generator in steps of $12.5\,\mathrm{ns}$. For sinusoidal PWM the duty is updated once per carrier period from a $256$-point sine table (CPU load at $20\,\mathrm{kHz}$: three multiplies per period, negligible). For the PSIM-style "switching point list" mode the timer compare registers are rewritten at each listed angle; angles are quantised to the carrier resolution ($0.36^\circ$ of a $60\,\mathrm{Hz}$ fundamental at $12.5\,\mathrm{ns}$ is far finer than needed).

Frequency range offered in the menu: $0.1\,\mathrm{Hz}$ to $200\,\mathrm{kHz}$ for the carrier (prescaler and period computed in firmware); $0.1$–$400\,\mathrm{Hz}$ for the fundamental.

---
## 5. Fault path

The converter pulls `FAULT` low through a PC817 phototransistor; the gating block has a $4.7\,\mathrm{k\Omega}$ pull-up to $3.3\,\mathrm{V}$ (sink current $0.7\,\mathrm{mA}$, within the PC817's capability at its minimum current-transfer ratio of 50 % with $8\,\mathrm{mA}$ LED current).

Two reactions in parallel:

1. **Hardware.** `FAULT` drives an NPN inverter that releases the second output-enable pin of the 74HCT541 ($\overline{G2}$): all six channels go tri-state within $\approx 50\,\mathrm{ns}$ of the fault, independent of firmware. This path is not latched; while the fault persists the outputs stay off.
2. **Firmware.** The ESP32 reads `FAULT` on an interrupt pin, stops the PWM, latches the state, shows it on the display and waits for the operator to press *reset*.

Latency from an over-current event to the LED current of the drivers being removed: comparator ($1\,\mathrm{\mu s}$ with the $1.6\,\mathrm{\mu s}$ RC filter) + PC817 ($\approx 4\,\mathrm{\mu s}$) + buffer: **about $6\,\mathrm{\mu s}$**, plus the driver and IGBT turn-off. With the $4.7\,\mathrm{mH}$ inductor and $300\,\mathrm{V}$ the current rises by only $0.4\,\mathrm{A}$ in that time, so a $3\,\mathrm{A}$ threshold protects the $20\,\mathrm{A}$ devices with ample margin.

The front-panel **RUN/STOP** switch drives $\overline{G1}$ directly: with the switch in STOP the outputs are tri-stated regardless of the firmware.

---
## 6. Power budget

The block is fed from a $12\,\mathrm{V}$ / $2\,\mathrm{A}$ wall adapter. The same 12 V is passed to the converter boards over the gate bus.

| Consumer | Current at 12 V | Note |
| -------- | --------------- | ---- |
| TSR 1-2450 → 5 V rail (ESP32 Wi-Fi peaks $0.5\,\mathrm{A}$, OLED, 74HCT541, LEDs: $\leq 0.6\,\mathrm{A}$ at 5 V) | $0.28\,\mathrm{A}$ | switching regulator, $\eta \approx 90\,\%$ |
| Inverter box: $4 \times$ TMA-1215S (1 W, $\eta = 80\,\%$) + comparators + LEDs | $0.45\,\mathrm{A}$ | worst case, all modules at full load |
| DC/DC box: $2 \times$ TMA-1215S + comparators | $0.25\,\mathrm{A}$ | |
| Rectifier box | $0$ | no gate bus |
| **Total, one block + one inverter box** | $0.75\,\mathrm{A}$ | $9\,\mathrm{W}$ |

Two bus pins carry 12 V and five carry GND; a 28 AWG ribbon pin is rated $1\,\mathrm{A}$, so the paired 12 V pins are needed. Voltage drop over $1\,\mathrm{m}$ of ribbon ($0.2\,\Omega$ per conductor, two in parallel each way): $0.15\,\mathrm{V}$, inside the TMA-1215S $\pm 10\,\%$ input range.

Protection: $1.1\,\mathrm{A}$ resettable fuse and a series Schottky diode (reverse polarity) at the jack; the 5 V rail has no separate fuse (the TSR limits at $1.2\,\mathrm{A}$).

---
## 7. Summary

| Quantity | Value |
| -------- | ----- |
| Bus logic | $5\,\mathrm{V}$ CMOS (74HCT541), tri-state when disabled, $10\,\mathrm{k\Omega}$ pull-downs |
| LED current (per channel, on the converter board) | $7$–$13\,\mathrm{mA}$ with $270\,\Omega$ |
| Dead time | $1.5\,\mathrm{\mu s}$ IGBT / $0.8\,\mathrm{\mu s}$ MOSFET (menu $0.2$–$5\,\mathrm{\mu s}$) |
| Carrier range / resolution | $0.1\,\mathrm{Hz}$–$200\,\mathrm{kHz}$ / $12.5\,\mathrm{ns}$ |
| Fault latency to drivers off | $\approx 6\,\mathrm{\mu s}$ (hardware path) |
| Power | $12\,\mathrm{V}$, $0.75\,\mathrm{A}$ worst case with an inverter box |

---
## 8. References

1. Broadcom, [HCPL-3120 datasheet](https://docs.broadcom.com/doc/AV02-0161EN).
2. Texas Instruments, *SN74HCT541 datasheet*.
3. Espressif, *ESP32 Technical Reference Manual*, ch. MCPWM.
4. Sharp, *PC817 datasheet*.
5. Traco Power, *TSR 1 series datasheet*; Traco Power, *TMA series datasheet*.

---
## Links
- [Gate bus interface](../../00_docs/gate_bus_interface.md)
- [Architecture decisions](../../00_docs/architecture.md)
- [Project README](../../README.md)
