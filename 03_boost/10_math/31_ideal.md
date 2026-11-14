---
title: "Boost converter 110 V → 300 V: ideal design"
type: calculation
---
# Boost converter 110 V → 300 V: ideal design

> [!NOTE]
> Operating point, inductor, capacitors and semiconductor stresses of the step-up (boost) box, with ideal components and continuous conduction. The input is the lab's 110 V DC supply; the low-side switch is driven by the external gating block through the on-board isolated gate driver.

## 1. Design premises

|           Parameter            |                           Value                           |                           Note                            |
| :----------------------------: | :-------------------------------------------------------: | :-------------------------------------------------------: |
|    Input voltage ($V_{in}$)    |     $110\,\mathrm{V}$ nominal, $60$–$120\,\mathrm{V}$     |                Lab DC supply (110 V max.)                 |
|     Output voltage ($V_o$)     |                     $300\,\mathrm{V}$                     | Feeds the buck or the inverter box, or a series lamp bank |
|   Rated output power ($P_o$)   |                     $200\,\mathrm{W}$                     |                                                           |
|     Output current ($I_o$)     |                    $0.667\,\mathrm{A}$                    |               $R = V_o^2/P_o = 450\,\Omega$               |
| Switching frequency ($f_{sw}$) | $20\,\mathrm{kHz}$ nominal, $5$–$50\,\mathrm{kHz}$ usable |          IGBT up to 20 kHz, MOSFET up to 50 kHz           |
| Inductor current ripple target |             $\leq 40\,\%$ of $I_L$ at nominal             |     Same $4.7\,\mathrm{mH}$ inductor as the buck box      |
|  Output voltage ripple target  |                       $\leq 1\,\%$                        |                                                           |
|            Control             |       Open loop, duty cycle set on the gating block       |        Over-voltage trip mandatory (see section 6)        |

---
## 2. Topology and operating point

$L$ from $V_{in}$ to the switch node; low-side switch $Q_1$ from the switch node to the return rail; diode $D_1$ from the switch node to $V_o$; $C_o$ across the output. The switch emitter/source sits at the power return, so the gate driver and the protection circuit share a single isolated 15 V supply.

$$
D = 1 - \frac{V_{in}}{V_o} = 1 - \frac{110}{300} = 0.633
$$

$$
I_L = I_{in} = \frac{I_o}{1 - D} = \frac{P_o}{V_{in}} = 1.82\,\mathrm{A}
$$

At $60\,\mathrm{V}$ input the same output needs $D = 0.80$ and $I_L = 3.33\,\mathrm{A}$ (above the $3\,\mathrm{A}$ inductor rating: derate $P_o$ to $180\,\mathrm{W}$ at that input).

---
## 3. Inductor

$$
\Delta i_L = \frac{V_{in}\, D}{L\, f_{sw}} = \frac{110 \cdot 0.633}{4.7\,\mathrm{mH} \cdot 20\,\mathrm{kHz}} = 0.74\,\mathrm{A} \quad (41\,\%\ \text{of}\ I_L)
$$

$$
I_{L,max} = 2.19\,\mathrm{A} \qquad I_{L,min} = 1.45\,\mathrm{A}
$$

Boundary of continuous conduction (as a function of $D$, worst at $D = 1/3$):

$$
I_{o,B} = \frac{V_o\, D (1 - D)^2}{2 L f_{sw}} = \frac{300 \cdot 0.633 \cdot 0.135}{2 \cdot 4.7\,\mathrm{mH} \cdot 20\,\mathrm{kHz}} = 0.136\,\mathrm{A}
\quad\Rightarrow\quad R_{crit} = 2.2\,\mathrm{k\Omega},\ P_{min} = 41\,\mathrm{W}
$$

| $f_{sw}$ | $\Delta i_L$ | Ripple | $P_{min}$ (CCM) |
| -------- | ------------ | ------ | --------------- |
| $5\,\mathrm{kHz}$ | $2.96\,\mathrm{A}$ | $163\,\%$ | $163\,\mathrm{W}$ |
| $10\,\mathrm{kHz}$ | $1.48\,\mathrm{A}$ | $81\,\%$ | $82\,\mathrm{W}$ |
| $20\,\mathrm{kHz}$ | $0.74\,\mathrm{A}$ | $41\,\%$ | $41\,\mathrm{W}$ |
| $50\,\mathrm{kHz}$ | $0.30\,\mathrm{A}$ | $16\,\%$ | $16\,\mathrm{W}$ |

**Selected: $L = 4.7\,\mathrm{mH}$, $I_{sat} \geq 3\,\mathrm{A}$** (external, screw terminal `L`), identical to the buck box.

---
## 4. Capacitors

**Output capacitor.** During $D T_s$ the diode is off and the load is fed only by $C_o$:

$$
\Delta V_o = \frac{I_o\, D}{f_{sw}\, C_o}
\quad\Rightarrow\quad
C_o \geq \frac{0.667 \cdot 0.633}{20\,\mathrm{kHz} \cdot 3\,\mathrm{V}} = 7.0\,\mathrm{\mu F}
$$

The output capacitor carries the pulsed diode current:

$$
I_{C_o,rms} = I_o\sqrt{\frac{D}{1 - D}} = 0.667 \cdot 1.31 = 0.88\,\mathrm{A}
$$

**Selected: $2 \times 47\,\mathrm{\mu F}$, $450\,\mathrm{V}$ electrolytic in parallel with $4.7\,\mathrm{\mu F}$ film ($\geq 400\,\mathrm{V}$).** Capacitive ripple $0.22\,\mathrm{V}$; the film capacitor takes the edges of the diode current pulses (see the losses report for the ESR contribution, which dominates). Each electrolytic carries about $0.35\,\mathrm{A_{rms}}$, within its rating.

**Input capacitor.** The input current is the inductor current (continuous, $0.74\,\mathrm{A_{pp}}$ triangular), so the input capacitor only has to absorb the ripple from the lab supply leads:

$$
\Delta V_{in} = \frac{\Delta i_L}{8 f_{sw} C_{in}}
$$

**Selected: $47\,\mathrm{\mu F}$, $450\,\mathrm{V}$ electrolytic + $4.7\,\mathrm{\mu F}$ film**, $\Delta V_{in} \approx 1\,\mathrm{V}$. Both rated $450\,\mathrm{V}$ so that a reverse-connected or back-fed box is not destroyed.

---
## 5. Semiconductor stresses

| Device | Voltage | Average current | RMS current | Peak current |
| ------ | ------- | --------------- | ----------- | ------------ |
| $Q_1$ (switch) | $V_o = 300\,\mathrm{V}$ | $D I_L = 1.15\,\mathrm{A}$ | $I_L\sqrt{D} = 1.45\,\mathrm{A}$ | $2.19\,\mathrm{A}$ |
| $D_1$ | $V_o$ reverse | $I_o = 0.67\,\mathrm{A}$ | $I_L\sqrt{1 - D} = 1.10\,\mathrm{A}$ | $2.19\,\mathrm{A}$ |
| $L$ | — | $1.82\,\mathrm{A}$ | $1.83\,\mathrm{A}$ | $2.19\,\mathrm{A}$ |

| Component | Selection | Notes |
| --------- | --------- | ----- |
| $Q_1$ | IGBT IRG4PC40UD (600 V) or MOSFET IPW60R099C6 (650 V) | TO-247, low side |
| $D_1$ | STTH8R06D (600 V, 8 A, ultrafast) | TO-220AC |
| Gate driver | HCPL-3120 + TMA-1215S (shared with the protection circuit) | $R_g = 22\,\Omega$ |

---
## 6. Protection and measurement

> [!WARNING]
> In open loop the boost output has no upper limit: with no load, or in discontinuous conduction, $V_o$ rises far above $V_{in}/(1 - D)$ until something breaks. **Never run the boost without a load connected**, ramp $D$ from zero, and keep the over-voltage trip enabled.

- **Over-voltage.** Output divider to a comparator, default trip at $360\,\mathrm{V}$; pulls `FAULT` low on the gate bus so the gating block stops the PWM. The $450\,\mathrm{V}$ capacitors and 600 V semiconductors survive the trip point with margin.
- **Over-current.** $0.1\,\Omega$ shunt in the return rail (inductor current), trimmer threshold, default $3\,\mathrm{A}$.
- **Start-up.** When $V_{in}$ is applied, $C_o$ charges through $L$ and $D_1$ even with $Q_1$ off; the $L$–$C_o$ resonance ($Z_0 = \sqrt{L/C_o} = 6.9\,\Omega$, $f_0 = 230\,\mathrm{Hz}$) would overshoot to nearly $2 V_{in}$. A $10\,\Omega$ NTC in the input lead damps it ($\zeta \approx 0.7$) and limits the first current peak to $\approx 11\,\mathrm{A}$.
- **Test points.** `V_IN`, `SW`, `V_OUT`, `I_L` ($0.1\,\mathrm{V/A}$), `GND_P`.
- **Fuse.** 5×20 mm, $4\,\mathrm{A}$ T at the input.

---
## 7. Summary

| Quantity | Value |
| -------- | ----- |
| $D$ at nominal | $0.633$ |
| $I_L$ / $\Delta i_L$ | $1.82\,\mathrm{A}$ / $0.74\,\mathrm{A}$ ($41\,\%$) |
| $C_o$ / capacitive $\Delta V_o$ | $2 \times 47\,\mathrm{\mu F}$ + $4.7\,\mathrm{\mu F}$ film / $0.22\,\mathrm{V}$ |
| $C_{in}$ | $47\,\mathrm{\mu F}$ + $4.7\,\mathrm{\mu F}$ film |
| CCM limit | $41\,\mathrm{W}$ ($R < 2.2\,\mathrm{k\Omega}$) |
| Switch, diode | 600 V class, $I_{rms}$ $1.45$ / $1.10\,\mathrm{A}$ |

---
## 8. References

1. D. W. Hart, *Power Electronics*, McGraw-Hill, 2011, ch. 6 (boost converter).
2. R. W. Erickson, D. Maksimović, *Fundamentals of Power Electronics*, 3rd ed., Springer, 2020, ch. 2–3 and 5 (discontinuous conduction).
3. Broadcom, [HCPL-3120 datasheet](https://docs.broadcom.com/doc/AV02-0161EN).

---
## Links
- [Boost design with losses](02_losses.md)
- [Buck ideal design](../../02_buck/10_math/01_ideal.md)
- [Gate bus interface](../../00_docs/gate_bus_interface.md)
- [Project README](../../README.md)
