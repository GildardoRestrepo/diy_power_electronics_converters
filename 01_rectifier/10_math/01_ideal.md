---
title: "Six-pulse rectifier: ideal design"
created: 2026-11-13
time: ""
creator: "Fable 5.1"
last update: 2026-11-13
update by: "Fable 5.1"
type: calculation
status: draft
stage: 1
area: power
editor: "Gilbert"
order: 1
tags:
  - type/calculation
---
# Six-pulse rectifier: ideal design

> [!NOTE]
> Operating point and component stresses of the three-phase full-wave (six-pulse) diode rectifier box, with ideal diodes and an ideal source. Four identical boxes are built so that they can be combined into 12- and 24-pulse rectifiers with the lab's phase-shifting transformers.

## 1. Design premises

| Parameter | Value | Note |
| --------- | ----- | ---- |
| Line voltage at the bridge ($V_{LL}$) | $208\,\mathrm{V_{rms}}$ | Lab mains or transformer secondary of the same ratio |
| Line frequency ($f$) | $60\,\mathrm{Hz}$ | Colombia |
| Rated DC current ($I_d$) | $5\,\mathrm{A}$ | Continuous, lamp bank or reactor load |
| Maximum DC current | $8\,\mathrm{A}$ | 10 min, heatsink-limited (see losses report) |
| Load | Resistive (lamps) or RL (reactor) | $L_{load}$ large enough for continuous $i_d$ |
| Pulse number | 6 | Single box; 12 or 24 with several boxes |

Each box must be **electrically floating**: for 12- and 24-pulse operation the DC outputs of several bridges are connected in series (or in parallel through an interphase transformer), so no terminal of the bridge can be bonded to chassis or to the other boxes.

---
## 2. Topology

Six diodes in a Graetz bridge. The upper group ($D_1, D_3, D_5$, cathodes tied to DC+) conducts the most positive phase; the lower group ($D_4, D_6, D_2$, anodes tied to DC−) conducts the most negative one. Each diode conducts $120^\circ$ per cycle and the output has six pulses per period ($360\,\mathrm{Hz}$ ripple at $60\,\mathrm{Hz}$).

```
      A ──┬──▶|── D1 ──┐
          │            │
      B ──┼──▶|── D3 ──┼────── DC+
          │            │
      C ──┼──▶|── D5 ──┘
          │
          ├──|◀── D4 ──┐
          │            │
          ├──|◀── D6 ──┼────── DC−
          │            │
          └──|◀── D2 ──┘
```

---
## 3. Output voltage

Average output voltage with ideal diodes and no commutation overlap:

$$
V_{do} = \frac{3\sqrt{2}}{\pi}\,V_{LL} = 1.3505 \cdot 208\,\mathrm{V} \approx 281\,\mathrm{V}
$$

Instantaneous output is the envelope of the six line voltages, so

$$
v_{d,max} = \sqrt{2}\,V_{LL} = 294\,\mathrm{V} \qquad
v_{d,min} = \sqrt{2}\,V_{LL}\cos 30^\circ = 255\,\mathrm{V}
$$

Peak-to-peak ripple is $39\,\mathrm{V}$ ($14\,\%$ of $V_{do}$). The RMS value of the output voltage and its ripple factor:

$$
V_{d,rms} = \sqrt{2}\,V_{LL}\sqrt{\tfrac{1}{2} + \tfrac{3\sqrt{3}}{4\pi}} = 1.3516\,V_{LL} \approx 281.1\,\mathrm{V}
\qquad
RF = \sqrt{\left(\tfrac{V_{d,rms}}{V_{do}}\right)^2 - 1} \approx 4.2\,\%
$$

The dominant ripple harmonic is the sixth ($360\,\mathrm{Hz}$), with amplitude

$$
V_6 = \frac{2 V_{do}}{36 - 1} \approx 0.057\,V_{do} = 16\,\mathrm{V}
$$

---
## 4. Currents

With a highly inductive load the output current is a constant $I_d = 5\,\mathrm{A}$. With a pure lamp (resistive) load it follows the voltage envelope; the diode stresses below use the constant-current case, which is the more demanding one for RMS values.

| Quantity | Expression | Value at $I_d = 5\,\mathrm{A}$ |
| -------- | ---------- | ------------------------------ |
| Diode average current | $I_{D,avg} = I_d/3$ | $1.67\,\mathrm{A}$ |
| Diode RMS current | $I_{D,rms} = I_d/\sqrt{3}$ | $2.89\,\mathrm{A}$ |
| Diode peak current | $I_{D,pk} = I_d$ | $5\,\mathrm{A}$ |
| AC line current (RMS) | $I_{L,rms} = I_d\sqrt{2/3}$ | $4.08\,\mathrm{A}$ |
| AC line fundamental (RMS) | $I_{L1} = \frac{\sqrt{6}}{\pi} I_d$ | $3.90\,\mathrm{A}$ |
| Line current THD | $\sqrt{(I_{L,rms}/I_{L1})^2 - 1}$ | $31\,\%$ |
| Output power | $P_d = V_{do} I_d$ | $1.40\,\mathrm{kW}$ |

The line current is a quasi-square wave of $\pm I_d$ with $120^\circ$ blocks; its harmonics are of order $6k \pm 1$ ($5, 7, 11, 13, \dots$) with amplitude $1/n$ of the fundamental. This is the spectrum that the 12- and 24-pulse connections cancel.

---
## 5. Voltage stresses

| Quantity | Expression | Value |
| -------- | ---------- | ----- |
| Diode peak inverse voltage | $PIV = \sqrt{2}\,V_{LL}$ | $294\,\mathrm{V}$ |
| DC output capacitor / varistor | $v_{d,max}$ | $294\,\mathrm{V}$ |

Selected ratings include margin for mains surges and for a $10\,\%$ high secondary voltage: diodes rated $\geq 600\,\mathrm{V}$ (800 V chosen), DC-side varistor with $V_{rms} = 320\,\mathrm{V}$ (clamps near $510\,\mathrm{V}$).

---
## 6. Multi-pulse operation with several boxes

| Configuration | Boxes | Transformer secondaries | $V_{do}$ (series) | Ripple | Line harmonics |
| ------------- | ----- | ----------------------- | ----------------- | ------ | -------------- |
| 6-pulse | 1 | one (Y or Δ) | $1.35\,V_{LL}$ | 6th ($4.2\,\%$) | $5, 7, 11, 13, \dots$ |
| 12-pulse | 2 | Y and Δ ($30^\circ$ apart) | $2.70\,V_{LL}$ | 12th ($1.0\,\%$) | $11, 13, 23, 25, \dots$ |
| 24-pulse | 4 | four, $15^\circ$ apart (zigzag) | $5.40\,V_{LL}$ | 24th ($0.25\,\%$) | $23, 25, 47, 49, \dots$ |

Series connection adds the DC voltages and keeps $I_d$; parallel connection (same $I_d$ per bridge, interphase transformer between the DC+ terminals) keeps $V_{do}$ and adds currents. The diode stresses of each box are unchanged in both cases, which is why one box design serves all three experiments. With the series connection at $208\,\mathrm{V}$ the 24-pulse output reaches $1.1\,\mathrm{kV}$; lamp banks must then be connected in series and the test procedure must treat the stack as high voltage.

---
## 7. Selected components (ideal sizing)

| Component | Selection | Rating / note |
| --------- | --------- | ------------- |
| $D_1 \dots D_6$ | Standard-recovery rectifier, TO-220AC (e.g. Vishay 20ETS08) | $800\,\mathrm{V}$, $20\,\mathrm{A}$; one clip-on heatsink each |
| AC fuses $F_1 \dots F_3$ | 5×20 mm, time-lag | $6.3\,\mathrm{A}$ T, $250\,\mathrm{V}$ (line current $4.1\,\mathrm{A_{rms}}$ at $I_d = 5\,\mathrm{A}$) |
| DC varistor $RV_1$ | Disc 14 mm | $320\,\mathrm{V_{rms}}$ |
| DC snubber $R_s C_s$ | $47\,\Omega$ 2 W + $0.1\,\mathrm{\mu F}$ 630 V film | Damps the LC ringing between transformer leakage and stray capacitance at each commutation |
| Measuring shunt $R_{sh}$ | $0.1\,\Omega$, $5\,\mathrm{W}$ | $v = 0.1\,\mathrm{V/A}$ at the `I_D` test points, inserted in the DC− rail |
| Pilot LED | LED + $2 \times 100\,\mathrm{k\Omega}$ 0.5 W | $1.4\,\mathrm{mA}$ at $281\,\mathrm{V}$, shows "DC present" |
| Terminals | 5.08 mm screw blocks | AC: 3 poles; DC: 2 poles |

---
## 8. References

1. N. Mohan, T. Undeland, W. Robbins, *Power Electronics: Converters, Applications and Design*, 3rd ed., Wiley, 2003, ch. 5 (three-phase diode rectifiers).
2. D. W. Hart, *Power Electronics*, McGraw-Hill, 2011, ch. 4.
3. M. H. Rashid, *Power Electronics: Circuits, Devices and Applications*, 4th ed., Pearson, 2014, ch. 3 (multi-pulse rectifiers).

---
## Links
- [Rectifier design with losses](02_losses.md)
- [Project README](../../README.md)
