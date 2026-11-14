---
title: "Six-pulse rectifier: design with losses"
type: calculation
---
# Six-pulse rectifier: design with losses

> [!NOTE]
> First-level loss model of the six-pulse rectifier box: diode forward drop and resistance, transformer leakage (commutation overlap), shunt and wiring. Gives the expected output voltage, efficiency and heatsink requirement at the rated point of the ideal report.

## 1. Loss model

Each element is replaced by a linear model valid around the operating point:

| Element | Model | Parameters used |
| ------- | ----- | --------------- |
| Diode | $v_D = V_{F0} + r_d\, i_D$ | 20ETS08: $V_{F0} = 0.75\,\mathrm{V}$, $r_d = 30\,\mathrm{m\Omega}$ at $T_j = 100\,^\circ\mathrm{C}$ (from the $V_F$–$I_F$ curve) |
| AC source | $L_s$ per phase (transformer leakage + wiring) | $L_s = 1.0\,\mathrm{mH}$ ($X_s = 0.38\,\Omega$, about $1.3\,\%$ of $Z_{base} = V_{LL}^2/S$ at $1.5\,\mathrm{kVA}$); update with the measured short-circuit impedance of the lab transformer |
| Shunt + wiring + fuses + terminals | $R_w$ | $R_{sh} = 0.10\,\Omega$, $R_{wire} \approx 0.05\,\Omega$ |

Rated point from the ideal report: $V_{LL} = 208\,\mathrm{V}$, $I_d = 5\,\mathrm{A}$, $V_{do} = 281\,\mathrm{V}$.

---
## 2. Output voltage regulation

**Commutation overlap.** With $L_s$ in each phase the current cannot transfer instantly between diodes; during the overlap angle $u$ two diodes of the same group conduct and the output voltage follows the average of two phases. The average voltage drop is

$$
\Delta V_u = \frac{3\,\omega L_s}{\pi}\, I_d = \frac{3 \cdot 377 \cdot 1.0\,\mathrm{mH}}{\pi} \cdot 5\,\mathrm{A} \approx 1.8\,\mathrm{V}
\qquad
\cos u = 1 - \frac{2\,\omega L_s I_d}{\sqrt{2}\,V_{LL}} \Rightarrow u \approx 9.2^\circ
$$

**Diode drop.** Two diodes conduct in series at every instant:

$$
\Delta V_D = 2\,(V_{F0} + r_d\, I_d) = 2\,(0.75 + 0.03 \cdot 5) = 1.8\,\mathrm{V}
$$

**Resistive drop.** $\Delta V_R = R_w I_d = 0.15 \cdot 5 = 0.75\,\mathrm{V}$.

**Loaded output voltage:**

$$
V_d = V_{do} - \Delta V_u - \Delta V_D - \Delta V_R \approx 281 - 1.8 - 1.8 - 0.75 \approx 276.5\,\mathrm{V}
$$

The regulation from no load to $5\,\mathrm{A}$ is about $1.6\,\%$. The equivalent DC source is $V_{do} - 2V_{F0} = 279.5\,\mathrm{V}$ behind $R_{eq} = 3\omega L_s/\pi + 2 r_d + R_w \approx 0.36 + 0.06 + 0.15 = 0.57\,\Omega$.

---
## 3. Losses and efficiency

| Loss | Expression | Value at $5\,\mathrm{A}$ | At $8\,\mathrm{A}$ |
| ---- | ---------- | ------------------------ | ------------------ |
| Diodes (six) | $6\,(V_{F0} I_{D,avg} + r_d I_{D,rms}^2) = 2 V_{F0} I_d + 2 r_d I_d^2$ | $7.5 + 1.5 = 9.0\,\mathrm{W}$ | $12 + 3.8 = 15.8\,\mathrm{W}$ |
| Shunt | $R_{sh} I_d^2$ | $2.5\,\mathrm{W}$ | $6.4\,\mathrm{W}$ |
| Wiring, fuses, terminals | $R_{wire} I_d^2$ | $1.3\,\mathrm{W}$ | $3.2\,\mathrm{W}$ |
| Snubber | $C_s \Delta v^2 \cdot 6 f$ (worst case $\Delta v = 39\,\mathrm{V}$) | $< 0.1\,\mathrm{W}$ | $< 0.1\,\mathrm{W}$ |
| Pilot LED chain | $V_d^2 / 200\,\mathrm{k\Omega}$ | $0.4\,\mathrm{W}$ | $0.4\,\mathrm{W}$ |
| **Total** | | $13.2\,\mathrm{W}$ | $25.9\,\mathrm{W}$ |

Overlap losses are not dissipated in the box: the energy is exchanged with $L_s$ and appears as a voltage drop, not as heat.

$$
\eta = \frac{V_d I_d}{V_d I_d + P_{loss}} = \frac{1382}{1382 + 13.2} \approx 99.0\,\%
$$

Per diode: $1.5\,\mathrm{W}$ at $5\,\mathrm{A}$ and $2.6\,\mathrm{W}$ at $8\,\mathrm{A}$.

---
## 4. Thermal design

20ETS08 in TO-220AC: $R_{thJC} = 1.5\,\mathrm{K/W}$, $T_{j,max} = 150\,^\circ\mathrm{C}$. Free-standing with no heatsink $R_{thJA} \approx 60\,\mathrm{K/W}$, which at $1.5\,\mathrm{W}$ gives a $90\,\mathrm{K}$ rise: too hot for a closed box. Each diode gets a small clip-on heatsink ($R_{thSA} \approx 20\,\mathrm{K/W}$, e.g. Fischer FK 244 or equivalent) and the enclosure has ventilation slots above the diode row.

$$
T_j = T_a + P_D\,(R_{thJC} + R_{thCS} + R_{thSA}) = 40 + 1.5\,(1.5 + 0.5 + 20) = 73\,^\circ\mathrm{C} \quad (5\,\mathrm{A})
$$

$$
T_j = 40 + 2.6 \cdot 22 = 97\,^\circ\mathrm{C} \quad (8\,\mathrm{A})
$$

Both are below the $110\,^\circ\mathrm{C}$ design limit. The lower-group diodes ($D_2, D_4, D_6$) have their tabs at the phase potentials and the upper group at DC+, so **every heatsink is at a different potential**: use one heatsink per diode, or an insulating pad and bushing if a common bar is used.

The shunt dissipates $2.5\,\mathrm{W}$ ($6.4\,\mathrm{W}$ at $8\,\mathrm{A}$): a $5\,\mathrm{W}$ ceramic-cased resistor mounted $5\,\mathrm{mm}$ above the board.

---
## 5. Ripple and harmonics with a real load

**Lamp load (resistive).** The output current follows the voltage envelope ($i_d = v_d/R$), the ripple factor of the current equals the $4.2\,\%$ of the voltage, and diode RMS currents are $1.3\,\%$ higher than in the constant-current case; no change in sizing.

**Reactor load (RL).** With the lab reactor ($L \gg R/\omega$) the current ripple is

$$
\Delta i_{d,pp} \approx \frac{2\,V_6}{6\,\omega L} = \frac{32\,\mathrm{V}}{2262 \cdot L}
$$

so a $20\,\mathrm{mH}$ reactor gives $0.7\,\mathrm{A_{pp}}$ ($14\,\%$ of $5\,\mathrm{A}$). Continuous conduction holds while $I_d > \Delta i_{d,pp}/2$.

**Source side.** The overlap angle rounds the edges of the line current, reducing the 5th and 7th harmonics by a few percent relative to the $31\,\%$ THD of the ideal case. Measured THD is expected between $27$ and $30\,\%$.

---
## 6. Transient and protection notes

- **Turn-on surge.** The DC snubber capacitor and the stray capacitance are small, so there is no inrush beyond the load's own (cold lamp filaments draw about 10× their rated current for a few milliseconds; the 6.3 A T fuses tolerate this).
- **Reactor disconnection.** Opening the DC output with the reactor energized produces a voltage spike limited only by the varistor; always de-energize the AC side first (test procedure).
- **Fuse coordination.** Line current $4.1\,\mathrm{A_{rms}}$ at $5\,\mathrm{A}$ DC and $6.5\,\mathrm{A_{rms}}$ at the $8\,\mathrm{A}$ short-term limit; a 6.3 A T fuse holds $6.5\,\mathrm{A}$ for minutes and clears a diode short in well under one second at the prospective short-circuit current of the lab supply.

---
## 7. Summary at rated load

| Quantity | Ideal | With losses |
| -------- | ----- | ----------- |
| $V_d$ at $5\,\mathrm{A}$ | $281\,\mathrm{V}$ | $276.5\,\mathrm{V}$ |
| Losses | $0$ | $13.2\,\mathrm{W}$ |
| Efficiency | $100\,\%$ | $99.0\,\%$ |
| Diode junction temperature | — | $73\,^\circ\mathrm{C}$ (clip-on heatsink, $40\,^\circ\mathrm{C}$ ambient) |
| Overlap angle | $0$ | $9.2^\circ$ ($L_s = 1\,\mathrm{mH}$) |

---
## 8. References

1. N. Mohan, T. Undeland, W. Robbins, *Power Electronics*, 3rd ed., Wiley, 2003, sec. 5-6 (effect of $L_s$ on three-phase rectifiers).
2. Vishay, *20ETS08 datasheet* (standard recovery rectifier, 20 A, 800 V).
3. Fischer Elektronik, *FK 244 clip-on heatsink datasheet*.

---
## Links
- [Rectifier ideal design](01_ideal.md)
- [Project README](../../README.md)
