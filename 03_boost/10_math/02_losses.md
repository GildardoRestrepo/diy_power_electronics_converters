---
title: "Boost converter 110 V → 300 V: design with losses"
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
order: 2
tags:
  - type/calculation
---
# Boost converter 110 V → 300 V: design with losses

> [!NOTE]
> First-level loss model of the boost box: conduction and switching losses of the switch and diode, inductor copper and core, shunt, NTC and capacitor ESR. Gives the corrected duty cycle, the maximum attainable gain, efficiency and junction temperatures.

## 1. Loss model and parameters

Same device models as the buck report:

| Element | Parameters (hot) |
| ------- | ---------------- |
| IGBT IRG4PC40UD | $V_{CE0} = 0.9\,\mathrm{V}$, $r_{CE} = 50\,\mathrm{m\Omega}$; $E_{on} + E_{off} = 0.7\,\mathrm{mJ}$ at $480\,\mathrm{V}$, $20\,\mathrm{A}$ |
| MOSFET IPW60R099C6 | $R_{DS(on)} = 0.19\,\Omega$; $t_r + t_f = 100\,\mathrm{ns}$; $E_{oss}(300\,\mathrm{V}) \approx 6\,\mathrm{\mu J}$ |
| Diode STTH8R06D | $V_{F0} = 0.8\,\mathrm{V}$, $r_d = 60\,\mathrm{m\Omega}$, $Q_{rr} = 60\,\mathrm{nC}$ |
| Inductor | $R_L = 0.4\,\Omega$, $P_{core} \approx 0.3\,\mathrm{W}$ |
| Shunt, NTC (warm) | $0.1\,\Omega$, $0.3\,\Omega$ |
| Electrolytic ESR | $2\,\Omega$ each (47 µF, 450 V); film $< 20\,\mathrm{m\Omega}$ |

Rated point: $V_{in} = 110\,\mathrm{V}$, $V_o = 300\,\mathrm{V}$, $I_o = 0.667\,\mathrm{A}$, $I_L = 1.82\,\mathrm{A}$, $D = 0.633$, $f_{sw} = 20\,\mathrm{kHz}$.

---
## 2. Losses at the rated point

### 2.1 Switch (IGBT)

$$
P_{cond} = V_{CE0}\, D I_L + r_{CE}\, I_{Q,rms}^2 = 0.9 \cdot 1.15 + 0.05 \cdot 1.45^2 = 1.14\,\mathrm{W}
$$

$$
P_{sw} = f_{sw}\,(E_{on} + E_{off})\frac{V_o}{480}\frac{I_L}{20} = 20\,\mathrm{kHz} \cdot 0.7\,\mathrm{mJ} \cdot 0.625 \cdot 0.091 = 0.80\,\mathrm{W}
$$

$$
P_{rr} = Q_{rr} V_o f_{sw} = 60\,\mathrm{nC} \cdot 300\,\mathrm{V} \cdot 20\,\mathrm{kHz} = 0.36\,\mathrm{W}
\qquad
P_{Q1} = 2.3\,\mathrm{W}
$$

MOSFET alternative: $0.19 \cdot 1.45^2 = 0.40\,\mathrm{W}$ conduction, $20\,\mathrm{kHz}\,(\tfrac{1}{2} \cdot 300 \cdot 1.82 \cdot 100\,\mathrm{ns} + 6\,\mathrm{\mu J}) = 0.67\,\mathrm{W}$ switching, $0.36\,\mathrm{W}$ recovery: $P_{Q1} = 1.4\,\mathrm{W}$.

### 2.2 Diode

$$
P_{D1} = V_{F0} I_o + r_d I_{D,rms}^2 = 0.8 \cdot 0.667 + 0.06 \cdot 1.10^2 = 0.61\,\mathrm{W}
$$

### 2.3 Passive elements

| Loss | Expression | Value |
| ---- | ---------- | ----- |
| Inductor copper | $R_L\,(I_L^2 + \Delta i_L^2/12)$ | $0.4 \cdot 3.36 = 1.34\,\mathrm{W}$ |
| Inductor core | estimate | $0.3\,\mathrm{W}$ |
| Shunt | $R_{sh} I_L^2$ | $0.33\,\mathrm{W}$ |
| NTC (warm) | $0.3\,\Omega \cdot I_L^2$ | $1.0\,\mathrm{W}$ |
| Output electrolytics | $\mathrm{ESR}\, I_{rms}^2$ ($0.35\,\mathrm{A}$ each) | $2 \cdot 2 \cdot 0.12 = 0.49\,\mathrm{W}$ |
| Output film | takes the current edges | $\approx 0.05\,\mathrm{W}$ |
| Input capacitors | ripple $0.21\,\mathrm{A}$ | $< 0.1\,\mathrm{W}$ |
| Gate drive | $Q_g V_{GE} f_{sw}$ | $0.05\,\mathrm{W}$ (12 V bus) |

The NTC is the second-largest loss: with the input current of $1.82\,\mathrm{A}$ it self-heats to a few tenths of an ohm. A bypass relay is not included in this version; a solder-jumper footprint across the NTC allows bypassing it once the start-up behaviour has been verified in the lab.

### 2.4 Total and efficiency

$$
P_{loss} = 2.3 + 0.61 + 1.64 + 0.33 + 1.0 + 0.55 \approx 6.4\,\mathrm{W}
\qquad
\eta = \frac{200}{206.4} = 96.9\,\%
$$

---
## 3. Output voltage, corrected duty cycle and maximum gain

Volt-second balance on $L$ with the device drops and series resistances ($R_s = R_L + R_{sh} + R_{NTC} = 0.8\,\Omega$):

$$
V_o = \frac{V_{in} - I_L R_s - D\, V_Q - (1 - D)\, V_D}{1 - D}
$$

with $V_Q = V_{CE0} + r_{CE} I_L = 1.0\,\mathrm{V}$ and $V_D = V_{F0} + r_d I_L = 0.9\,\mathrm{V}$:

$$
V_o = \frac{110 - 1.46 - 0.63 - 0.33}{0.367} = \frac{107.6}{0.367} = 293\,\mathrm{V}
$$

The corrected duty cycle for $300\,\mathrm{V}$ (solving the implicit relation with $I_L = I_o/(1 - D)$) is $D \approx 0.640$ ($+1.1\,\%$). The series resistance limits the attainable gain; with a resistive load $R$,

$$
\frac{V_o}{V_{in}} = \frac{1}{(1 - D)}\cdot\frac{1}{1 + \dfrac{R_s}{(1 - D)^2 R}}
\qquad
\left.\frac{V_o}{V_{in}}\right|_{max} \approx \frac{1}{2}\sqrt{\frac{R}{R_s}} = \frac{1}{2}\sqrt{\frac{450}{0.8}} = 12
$$

far above the $2.7$ needed here, so the operating point is on the well-behaved side of the curve. Open-loop load regulation: $\partial V_o/\partial I_o \approx -R_s/(1 - D)^2 = -5.9\,\Omega$, i.e. $-3.9\,\mathrm{V}$ from no load to $0.667\,\mathrm{A}$ (before the DCM rise at light load, which is much larger).

**Output ripple with ESR.** The diode current steps from $0$ to $I_{L,min} = 1.45\,\mathrm{A}$ at turn-off; through the parallel impedance of the two electrolytics ($1\,\Omega$) and the film ($|X_C| = 1.7\,\Omega$ at $20\,\mathrm{kHz}$) it produces a step of about $0.9\,\mathrm{V}$ plus the $0.22\,\mathrm{V}$ capacitive ramp: total $\approx 1.1\,\mathrm{V_{pp}}$ ($0.4\,\%$).

---
## 4. Thermal design

| Device | $P$ | $R_{thJA}$ with $15\,\mathrm{K/W}$ heatsink | $T_j$ at $40\,^\circ\mathrm{C}$ |
| ------ | --- | ------------------------------------------- | ------------------------------- |
| $Q_1$ IGBT, 20 kHz | $2.3\,\mathrm{W}$ | $16.3\,\mathrm{K/W}$ | $77\,^\circ\mathrm{C}$ |
| $Q_1$ MOSFET, 50 kHz | $3.4\,\mathrm{W}$ | $16.3\,\mathrm{K/W}$ | $95\,^\circ\mathrm{C}$ |
| $D_1$ | $0.6\,\mathrm{W}$ | $17\,\mathrm{K/W}$ | $50\,^\circ\mathrm{C}$ |

The switch tab (collector) is at the switch node and the diode tab (cathode) at $V_o$: separate heatsinks or insulated mounting. NTC and inductor dissipate $2.6\,\mathrm{W}$ together inside the box; ventilation slots are required.

---
## 5. Transients

- **Start-up without PWM.** $C_o$ charges through $L$, $D_1$ and the NTC; with the NTC cold ($10\,\Omega$) the damping ratio is $\zeta = R/(2 Z_0) = 10/13.8 = 0.72$, peak current $\approx 11\,\mathrm{A}$, output settles at $V_{in} - V_D$ within $5\,\mathrm{ms}$ with $< 5\,\%$ overshoot. Without the NTC the overshoot would approach $2 V_{in} = 220\,\mathrm{V}$ and the first current peak $16\,\mathrm{A}$.
- **PWM ramp.** Ramping $D$ from $0$ to $0.64$ over $\geq 200\,\mathrm{ms}$ keeps the inductor current within $10\,\%$ of its steady-state value at every step (the output time constant with the load is $R C_o = 45\,\mathrm{ms}$).
- **Load removal.** If the load opens at $D = 0.64$, $V_o$ rises at $I_L/C_o \approx 18\,\mathrm{V/ms}$: the over-voltage comparator must trip within a few milliseconds, which it does (microsecond response, firmware stop in $< 100\,\mathrm{\mu s}$).
- **Turn-off overshoot.** Loop $C_o$–$D_1$–$Q_1$ kept short on the PCB ($< 40\,\mathrm{mm}$, film capacitor adjacent): $L_\sigma\, di/dt \approx 2\,\mathrm{V}$.

---
## 6. Summary at rated load

| Quantity | Ideal | With losses |
| -------- | ----- | ----------- |
| $D$ for $300\,\mathrm{V}$ | $0.633$ | $0.640$ |
| Losses | $0$ | $6.4\,\mathrm{W}$ |
| Efficiency | $100\,\%$ | $96.9\,\%$ |
| $T_j$ switch / diode | — | $77 / 50\,^\circ\mathrm{C}$ (IGBT, 20 kHz) |
| Maximum gain (resistive limit) | $\infty$ | $12$ |
| Output ripple | $0.22\,\mathrm{V}$ | $1.1\,\mathrm{V_{pp}}$ (ESR) |

---
## 7. References

1. R. W. Erickson, D. Maksimović, *Fundamentals of Power Electronics*, 3rd ed., Springer, 2020, ch. 3 (boost with inductor resistance, maximum gain).
2. Infineon, *IRG4PC40UD datasheet*; Infineon, *IPW60R099C6 datasheet*.
3. STMicroelectronics, *STTH8R06 datasheet*.

---
## Links
- [Boost ideal design](01_ideal.md)
- [Buck design with losses](../../02_buck/10_math/02_losses.md)
- [Project README](../../README.md)
