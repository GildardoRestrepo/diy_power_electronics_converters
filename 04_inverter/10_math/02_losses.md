---
title: "Three-phase inverter: design with losses"
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
# Three-phase inverter: design with losses

> [!NOTE]
> First-level loss model of the three-phase inverter box: IGBT and diode conduction and switching losses under sinusoidal PWM, dead-time voltage distortion, DC-link ESR and shunt. Gives efficiency, junction temperatures and the output voltage error to expect in open loop.

## 1. Loss model and parameters

| Element | Parameters (hot) |
| ------- | ---------------- |
| IGBT IRG4PC40UD | $V_{CE0} = 0.9\,\mathrm{V}$, $r_{CE} = 50\,\mathrm{m\Omega}$; $E_{on} + E_{off} = 0.7\,\mathrm{mJ}$ at $480\,\mathrm{V}$, $20\,\mathrm{A}$ |
| Co-pack diode | $V_{F0} = 0.9\,\mathrm{V}$, $r_d = 60\,\mathrm{m\Omega}$; $E_{rec} = 0.1\,\mathrm{mJ}$ at $480\,\mathrm{V}$, $20\,\mathrm{A}$ |
| DC-link electrolytics | ESR $2\,\Omega$ each (47 µF, 450 V) |
| Shunt, NTC (warm) | $0.1\,\Omega$, $0.3\,\Omega$ |
| Gate drive | $Q_g = 150\,\mathrm{nC}$, $15\,\mathrm{V}$ |

Rated point: $V_{dc} = 280\,\mathrm{V}$, $I_m = 2.83\,\mathrm{A}$ ($2\,\mathrm{A_{rms}}$), $m_a = 0.8$, $\cos\varphi = 1$, $f_{sw} = 10\,\mathrm{kHz}$, $f_1 = 60\,\mathrm{Hz}$.

---
## 2. Losses per switch under sinusoidal PWM

Averaging over a fundamental period with a sinusoidal current and the linear device models:

**IGBT conduction**

$$
P_{c,Q} = V_{CE0} I_m\left(\frac{1}{2\pi} + \frac{m_a\cos\varphi}{8}\right) + r_{CE} I_m^2\left(\frac{1}{8} + \frac{m_a\cos\varphi}{3\pi}\right)
= 0.9 \cdot 2.83 \cdot 0.259 + 0.05 \cdot 8.0 \cdot 0.210 = 0.66 + 0.08 = 0.74\,\mathrm{W}
$$

**Diode conduction**

$$
P_{c,D} = V_{F0} I_m\left(\frac{1}{2\pi} - \frac{m_a\cos\varphi}{8}\right) + r_d I_m^2\left(\frac{1}{8} - \frac{m_a\cos\varphi}{3\pi}\right)
= 0.9 \cdot 2.83 \cdot 0.059 + 0.06 \cdot 8.0 \cdot 0.040 = 0.15 + 0.02 = 0.17\,\mathrm{W}
$$

**Switching** (energies proportional to current and voltage, averaged over the half-cycle in which the device switches current):

$$
P_{sw,Q} = \frac{f_{sw}}{\pi}\,(E_{on} + E_{off})\frac{V_{dc}}{480}\frac{I_m}{20}
= \frac{10\,\mathrm{kHz}}{\pi} \cdot 0.7\,\mathrm{mJ} \cdot 0.583 \cdot 0.142 = 0.18\,\mathrm{W}
$$

$$
P_{sw,D} = \frac{f_{sw}}{\pi}\, E_{rec}\frac{V_{dc}}{480}\frac{I_m}{20} = 0.03\,\mathrm{W}
$$

**Per switch position (IGBT + diode):** $0.74 + 0.17 + 0.18 + 0.03 = 1.12\,\mathrm{W}$. At $20\,\mathrm{kHz}$ the switching terms double and the total rises to $1.33\,\mathrm{W}$. With the reactor ($\cos\varphi = 0.8$) the IGBT conduction drops slightly and the diode conduction rises to $0.26\,\mathrm{W}$: the sum is within $5\,\%$ of the lamp case.

---
## 3. Total losses and efficiency

| Loss | Value |
| ---- | ----- |
| Six switch positions | $6 \cdot 1.12 = 6.7\,\mathrm{W}$ |
| DC-link electrolytics ($0.35\,\mathrm{A}$ each) | $2 \cdot 2 \cdot 0.12 = 0.49\,\mathrm{W}$ |
| Shunt ($I_{dc,rms} \approx 1.3\,\mathrm{A}$) | $0.17\,\mathrm{W}$ |
| NTC (warm) | $0.5\,\mathrm{W}$ |
| Bleeder + pilot LED | $0.4\,\mathrm{W}$ |
| Gate drive (six, from the 12 V bus) | $0.14\,\mathrm{W}$ |
| **Total (power path)** | $\approx 8.3\,\mathrm{W}$ |

$$
\eta = \frac{300}{308.3} = 97.3\,\%
$$

Auxiliary consumption from the gating block's 12 V bus: four 1 W isolated modules at light load, six driver LEDs, comparators and LEDs: about $3\,\mathrm{W}$.

---
## 4. Output voltage error: device drops and dead time

In open loop the fundamental output voltage is lower than $0.612\, m_a V_{dc}$ because of two effects.

**Device drops.** Each phase leg loses $\approx V_{CE0}$ or $V_{F0}$ whichever device conducts, i.e. about $1\,\mathrm{V}$ in the phase voltage (less than $1\,\%$ of $140\,\mathrm{V}$).

**Dead time.** During $t_d$ both switches of a leg are off and the output follows the current polarity; the average phase-voltage error is

$$
\Delta V_{AN} = \frac{2\, t_d\, f_{sw}}{1}\cdot\frac{V_{dc}}{2}\,\mathrm{sgn}(i_A)
= 1.5\,\mathrm{\mu s} \cdot 10\,\mathrm{kHz} \cdot 280\,\mathrm{V} = 4.2\,\mathrm{V}
$$

a square-wave error of $\pm 4.2\,\mathrm{V}$ in phase with the current ($3.7\,\%$ of the $112\,\mathrm{V}$ peak phase voltage at $m_a = 0.8$). Its fundamental ($4/\pi$ of the amplitude) reduces the output by $5.3\,\mathrm{V}$ peak and its 5th and 7th harmonics ($1/5$, $1/7$) add about $1.5\,\%$ of low-order distortion. At $20\,\mathrm{kHz}$ the effect doubles; the gating block can compensate it in firmware once the current polarity is known (future work).

**Corrected modulation index** for $137\,\mathrm{V_{LL}}$ at $280\,\mathrm{V}$: $m_a \approx 0.8 \cdot (1 + 0.037 + 0.01) \approx 0.84$.

---
## 5. Thermal design

Six TO-247 devices at $1.1$–$1.3\,\mathrm{W}$ each. Free-standing TO-247 in still air ($R_{thJA} \approx 40\,\mathrm{K/W}$) would reach $T_j = 40 + 1.3 \cdot 40 = 92\,^\circ\mathrm{C}$: acceptable but with no margin for the closed box. **Selected: one common extruded heatsink bar** behind the six devices with insulating pads and bushings ($R_{thCS} = 1.0\,\mathrm{K/W}$ per device, $R_{thSA} = 4\,\mathrm{K/W}$ for the bar), since the six tabs are at different potentials:

$$
T_s = T_a + 6 P\, R_{thSA} = 40 + 6.7 \cdot 4 = 67\,^\circ\mathrm{C}
\qquad
T_j = T_s + P\,(R_{thJC} + R_{thCS}) = 67 + 1.12 \cdot 1.8 = 69\,^\circ\mathrm{C}
$$

The PCB places the six devices in a row along one board edge, $15\,\mathrm{mm}$ apart, so that a $100 \times 25\,\mathrm{mm}$ bar can be bolted across them and to the enclosure wall.

---
## 6. Transients

- **Gate charge and driver.** $Q_g = 150\,\mathrm{nC}$ at $10\,\mathrm{kHz}$ is $1.5\,\mathrm{mA}$ average per driver; the shared low-side supply (three drivers + comparators) draws $\approx 25\,\mathrm{mA}$ of its $67\,\mathrm{mA}$ rating.
- **dv/dt and the isolated supplies.** The high-side supplies see the full $280\,\mathrm{V}$ swing at the switching edges ($\approx 5\,\mathrm{kV/\mu s}$); the TMA-1215S isolation capacitance ($\approx 20\,\mathrm{pF}$) injects $0.1\,\mathrm{A}$ pulses into the 12 V bus. A $100\,\mathrm{nF}$ Y-class-style capacitor from each isolated 0 V to the bus GND is **not** used (it would defeat the isolation for probing); instead the bus GND is decoupled on the board with $10\,\mathrm{\mu F}$ and routed away from the gate traces.
- **Stop with inductive load.** When the PWM stops, the reactor current freewheels through the co-pack diodes into the DC link and raises $V_{dc}$ by $\Delta V = \tfrac{1}{2} L I^2 / (C V)$: with $L = 20\,\mathrm{mH}$, $2.8\,\mathrm{A}$, $94\,\mathrm{\mu F}$ at $280\,\mathrm{V}$ this is $\approx 3\,\mathrm{V}$, well below the $400\,\mathrm{V}$ trip.

---
## 7. Summary at rated load

| Quantity | Ideal | With losses |
| -------- | ----- | ----------- |
| $m_a$ for $137\,\mathrm{V_{LL}}$ at $280\,\mathrm{V}$ | $0.80$ | $0.84$ |
| Losses | $0$ | $8.3\,\mathrm{W}$ |
| Efficiency | $100\,\%$ | $97.3\,\%$ |
| $T_j$ (common heatsink bar) | — | $69\,^\circ\mathrm{C}$ |
| Dead-time distortion (phase voltage) | $0$ | $\pm 4.2\,\mathrm{V}$ square error |

---
## 8. References

1. N. Mohan, T. Undeland, W. Robbins, *Power Electronics*, 3rd ed., Wiley, 2003, ch. 8.
2. D. Graovac, M. Pürschel, *IGBT Power Losses Calculation Using the Data-Sheet Parameters*, Infineon application note, 2009.
3. Infineon, *IRG4PC40UD datasheet*.
4. Broadcom, [HCPL-3120 datasheet](https://docs.broadcom.com/doc/AV02-0161EN).

---
## Links
- [Inverter ideal design](01_ideal.md)
- [Gating block signal and power budget](../../05_gating_block/10_math/01_signal_budget.md)
- [Project README](../../README.md)
