---
title: "Buck converter 300 V → 110 V: design with losses"
type: calculation
---
# Buck converter 300 V → 110 V: design with losses

> [!NOTE]
> First-level loss model of the buck box: conduction and switching losses of the switch and diode, inductor copper and core, shunt and capacitor ESR. Gives the corrected duty cycle, efficiency and the junction temperatures that decide the heatsinks.

## 1. Loss model and parameters

| Element | Model | Parameters (at $T_j \approx 100\,^\circ\mathrm{C}$) |
| ------- | ----- | ------------------------------------------------------ |
| IGBT IRG4PC40UD | $v_{CE} = V_{CE0} + r_{CE}\, i$; $E_{sw} = E_{ref}\dfrac{V}{V_{ref}}\dfrac{I}{I_{ref}}$ | $V_{CE0} = 0.9\,\mathrm{V}$, $r_{CE} = 50\,\mathrm{m\Omega}$; $E_{on} + E_{off} = 0.7\,\mathrm{mJ}$ at $480\,\mathrm{V}$, $20\,\mathrm{A}$ |
| MOSFET IPW60R099C6 (alternative) | $R_{DS(on)}$; $E_{sw} = \tfrac{1}{2} V I (t_r + t_f) + E_{oss}$ | $R_{DS(on)} = 0.19\,\Omega$ (hot); $t_r + t_f \approx 100\,\mathrm{ns}$ with $R_g = 22\,\Omega$; $E_{oss}(280\,\mathrm{V}) \approx 5\,\mathrm{\mu J}$ |
| Diode STTH8R06D | $v_D = V_{F0} + r_d\, i$; $Q_{rr}$ | $V_{F0} = 0.8\,\mathrm{V}$, $r_d = 60\,\mathrm{m\Omega}$, $Q_{rr} = 60\,\mathrm{nC}$ |
| Inductor | $R_L$ + core loss | $R_L = 0.4\,\Omega$; $P_{core} \approx 0.3\,\mathrm{W}$ at $0.71\,\mathrm{A}$ ripple, $20\,\mathrm{kHz}$ (powder toroid; verify with the core datasheet) |
| Shunt | $R_{sh}$ | $0.1\,\Omega$ |
| Capacitors | ESR | Electrolytic $2\,\Omega$ (47 µF, 450 V); film $< 20\,\mathrm{m\Omega}$ |
| Gate drive | $Q_g V_{GE} f_{sw}$ | $Q_g = 150\,\mathrm{nC}$, $15\,\mathrm{V}$ |

Rated point from the ideal report: $V_{in} = 280\,\mathrm{V}$, $V_o = 110\,\mathrm{V}$, $I_o = 1.82\,\mathrm{A}$, $f_{sw} = 20\,\mathrm{kHz}$, $D = 0.393$, $\Delta i_L = 0.71\,\mathrm{A}$.

---
## 2. Losses at the rated point

### 2.1 Switch (IGBT)

$$
P_{cond} = V_{CE0}\, D I_o + r_{CE}\, I_{Q,rms}^2 = 0.9 \cdot 0.72 + 0.05 \cdot 1.14^2 = 0.71\,\mathrm{W}
$$

$$
P_{sw} = f_{sw}\,(E_{on} + E_{off})\frac{V_{in}}{480}\frac{I_o}{20} = 20\,\mathrm{kHz} \cdot 0.7\,\mathrm{mJ} \cdot 0.583 \cdot 0.091 = 0.74\,\mathrm{W}
$$

$$
P_{rr} = Q_{rr} V_{in} f_{sw} = 60\,\mathrm{nC} \cdot 280\,\mathrm{V} \cdot 20\,\mathrm{kHz} = 0.34\,\mathrm{W}
\qquad
P_{Q1} = 1.8\,\mathrm{W}
$$

With the MOSFET alternative: $P_{cond} = 0.19 \cdot 1.14^2 = 0.25\,\mathrm{W}$, $P_{sw} = 20\,\mathrm{kHz}\,(\tfrac{1}{2}\cdot 280 \cdot 1.82 \cdot 100\,\mathrm{ns} + 5\,\mathrm{\mu J}) = 0.61\,\mathrm{W}$, plus the same $0.34\,\mathrm{W}$ of diode recovery: $P_{Q1} = 1.2\,\mathrm{W}$. At $50\,\mathrm{kHz}$ the MOSFET switching term grows to $1.5\,\mathrm{W}$ and the diode recovery to $0.85\,\mathrm{W}$, which is why the IGBT is limited to $20\,\mathrm{kHz}$ and the MOSFET to $50\,\mathrm{kHz}$.

### 2.2 Diode

$$
P_{D1} = V_{F0}(1 - D) I_o + r_d I_{D,rms}^2 = 0.8 \cdot 1.10 + 0.06 \cdot 1.42^2 = 1.0\,\mathrm{W}
$$

(The reverse-recovery energy is dissipated mostly in the switch and is counted there.)

### 2.3 Passive elements

| Loss | Expression | Value |
| ---- | ---------- | ----- |
| Inductor copper | $R_L\,(I_o^2 + \Delta i_L^2/12)$ | $0.4 \cdot 3.35 = 1.34\,\mathrm{W}$ |
| Inductor core | estimate | $0.3\,\mathrm{W}$ |
| Shunt | $R_{sh} I_o^2$ | $0.33\,\mathrm{W}$ |
| Input electrolytics | $\mathrm{ESR}\, I_{rms}^2$ ($0.3\,\mathrm{A}$ each) | $2 \cdot 2 \cdot 0.09 = 0.36\,\mathrm{W}$ |
| Output capacitors | film carries $0.21\,\mathrm{A}$ | $< 0.01\,\mathrm{W}$ |
| NTC (warm) | $0.3\,\Omega \cdot I_{in}^2$, $I_{in} = 0.72\,\mathrm{A}$ | $0.16\,\mathrm{W}$ |
| Gate drive | $Q_g V_{GE} f_{sw}$ | $0.05\,\mathrm{W}$ (from the 12 V bus) |

### 2.4 Total and efficiency

$$
P_{loss} = 1.8 + 1.0 + 1.64 + 0.33 + 0.36 + 0.16 \approx 5.3\,\mathrm{W}
\qquad
\eta = \frac{200}{205.3} = 97.4\,\%
$$

The auxiliary circuits (two 1 W isolated DC/DC modules, driver, comparators, LEDs) take about $1.5\,\mathrm{W}$ from the gating block's 12 V bus; they are not part of the power path.

---
## 3. Output voltage and corrected duty cycle

Averaging the switch-node voltage with the device drops and the series resistances:

$$
V_o = D\,(V_{in} - V_Q) - (1 - D)\,V_D - I_o\,(R_L + R_{sh})
$$

with $V_Q = V_{CE0} + r_{CE} I_o = 1.0\,\mathrm{V}$ and $V_D = V_{F0} + r_d I_o = 0.9\,\mathrm{V}$:

$$
V_o = 0.393 \cdot 279 - 0.607 \cdot 0.9 - 1.82 \cdot 0.5 = 109.6 - 0.55 - 0.91 = 108.2\,\mathrm{V}
$$

To obtain $110\,\mathrm{V}$ the duty cycle must be raised to

$$
D = \frac{V_o + V_D + I_o (R_L + R_{sh})}{V_{in} - V_Q + V_D} = \frac{110 + 0.9 + 0.91}{279 + 0.9} = 0.400
$$

a correction of $+1.7\,\%$ relative to the ideal $0.393$. Load regulation in open loop: $\partial V_o / \partial I_o \approx -(R_L + R_{sh} + D r_{CE} + (1-D) r_d) = -0.56\,\Omega$, i.e. $-1.0\,\mathrm{V}$ from no load to $1.82\,\mathrm{A}$. The $14\,\%$ six-pulse ripple of the rectifier input appears at the output scaled by $D$ (open loop, $\pm 7.7\,\mathrm{V}$ at $360\,\mathrm{Hz}$) unless the input is filtered; the on-board $98\,\mathrm{\mu F}$ reduces it only slightly ($\tau = RC \approx 3\,\mathrm{ms}$ at the reflected load).

---
## 4. Thermal design

Devices in TO-247 / TO-220 with $R_{thJC} \leq 1.5\,\mathrm{K/W}$. A clip-on or small extruded heatsink of $R_{thSA} = 15\,\mathrm{K/W}$ per device is enough:

| Device | $P$ | $R_{thJA}$ (with heatsink) | $T_j$ at $40\,^\circ\mathrm{C}$ ambient |
| ------ | --- | -------------------------- | --------------------------------------- |
| $Q_1$ IGBT, 20 kHz | $1.8\,\mathrm{W}$ | $0.8 + 0.5 + 15 = 16.3\,\mathrm{K/W}$ | $69\,^\circ\mathrm{C}$ |
| $Q_1$ MOSFET, 50 kHz | $2.9\,\mathrm{W}$ | $16.3\,\mathrm{K/W}$ | $87\,^\circ\mathrm{C}$ |
| $D_1$ | $1.0\,\mathrm{W}$ | $1.5 + 0.5 + 15 = 17\,\mathrm{K/W}$ | $57\,^\circ\mathrm{C}$ |

The switch tab (collector) is at $V_{in}$ and the diode tab (cathode) is at the switch node: **separate heatsinks, each at a different potential**, or insulated mounting on a common one. The inductor ($1.6\,\mathrm{W}$) and the shunt ($0.33\,\mathrm{W}$) are convection-cooled inside the box.

---
## 5. Transients

- **Turn-off overshoot.** The stray inductance of the $V_{in}$–$Q_1$–$D_1$–$C_{in}$ loop ($L_\sigma \approx 50\,\mathrm{nH}$ for a $40\,\mathrm{mm}$ loop) with $di/dt = 2.2\,\mathrm{A}/50\,\mathrm{ns}$ adds $L_\sigma\, di/dt \approx 2\,\mathrm{V}$: negligible against the 600 V rating. The film capacitor is placed right at the switch–diode pair to keep this loop short.
- **Gate loop.** $R_g = 22\,\Omega$ with $C_{ies} \approx 2\,\mathrm{nF}$ gives a $44\,\mathrm{ns}$ time constant and a peak gate current of $0.7\,\mathrm{A}$, within the $2.5\,\mathrm{A}$ of the HCPL-3120.
- **Start-up.** The NTC limits the input inrush to about $30\,\mathrm{A}$ for one time constant ($\approx 1\,\mathrm{ms}$); the gating block ramps $D$ from zero so the output and the inductor current rise without overshoot.
- **Load step (lamp switched in).** Open loop: the output drops by $R_{eq}\,\Delta I_o \approx 0.5\,\mathrm{V}$ per ampere and recovers in about $2\pi\sqrt{L C_o} \approx 3\,\mathrm{ms}$ with a damped ring at $f_0 = 1/(2\pi\sqrt{L C_o}) = 320\,\mathrm{Hz}$.

---
## 6. Summary at rated load

| Quantity | Ideal | With losses |
| -------- | ----- | ----------- |
| $D$ for $110\,\mathrm{V}$ | $0.393$ | $0.400$ |
| Losses | $0$ | $5.3\,\mathrm{W}$ |
| Efficiency | $100\,\%$ | $97.4\,\%$ |
| $T_j$ switch / diode | — | $69 / 57\,^\circ\mathrm{C}$ (IGBT, 20 kHz) |
| Open-loop load regulation | $0$ | $-0.56\,\Omega$ |

---
## 7. References

1. R. W. Erickson, D. Maksimović, *Fundamentals of Power Electronics*, 3rd ed., Springer, 2020, ch. 3 (steady-state equivalent circuit modelling, losses and efficiency).
2. Infineon, *IRG4PC40UD datasheet*; Infineon, *IPW60R099C6 datasheet*.
3. STMicroelectronics, *STTH8R06 datasheet*.
4. Broadcom, [HCPL-3120 datasheet](https://docs.broadcom.com/doc/AV02-0161EN).

---
## Links
- [Buck ideal design](01_ideal.md)
- [Boost design with losses](../../03_boost/10_math/02_losses.md)
- [Project README](../../README.md)
