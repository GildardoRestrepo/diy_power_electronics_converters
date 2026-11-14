---
title: "Buck converter 300 V → 110 V: ideal design"
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
# Buck converter 300 V → 110 V: ideal design

> [!NOTE]
> Operating point, inductor, capacitors and semiconductor stresses of the step-down (buck) box, with ideal components and continuous conduction. The input comes from the six-pulse rectifier box ($\approx 280\,\mathrm{V}$) or from the boost box; the switch is driven by the external gating block through the on-board isolated gate driver.

## 1. Design premises

| Parameter | Value | Note |
| --------- | ----- | ---- |
| Input voltage ($V_{in}$) | $280\,\mathrm{V}$ nominal, $150$–$320\,\mathrm{V}$ | Rectifier output at $208\,\mathrm{V_{LL}}$; "300 V" class |
| Output voltage ($V_o$) | $110\,\mathrm{V}$ | 110 V lamp bank |
| Rated output power ($P_o$) | $200\,\mathrm{W}$ | Two 100 W lamps in parallel |
| Output current ($I_o$) | $1.82\,\mathrm{A}$ | $R = V_o^2/P_o = 60.5\,\Omega$ |
| Switching frequency ($f_{sw}$) | $20\,\mathrm{kHz}$ nominal, $5$–$50\,\mathrm{kHz}$ usable | IGBT up to 20 kHz, MOSFET up to 50 kHz |
| Inductor current ripple target | $\leq 40\,\%$ of $I_o$ at nominal | Shared inductor with the boost box |
| Output voltage ripple target | $\leq 1\,\%$ | |
| Control | Open loop, duty cycle set on the gating block | No feedback in this version |

The same $4.7\,\mathrm{mH}$ inductor is used in the buck and the boost boxes; both carry $1.82\,\mathrm{A}$ average at their rated points.

---
## 2. Topology and operating point

High-side switch $Q_1$ (IGBT or MOSFET, TO-247) between $V_{in}$ and the switch node; freewheeling diode $D_1$ from the return rail to the switch node; $L$ from the switch node to the output; $C_o$ across the load. The switch emitter/source floats at the switch node, so its gate driver needs an isolated supply (one 15 V DC/DC module per switch).

$$
D = \frac{V_o}{V_{in}} = \frac{110}{280} = 0.393
$$

At the voltage limits: $D = 0.733$ at $150\,\mathrm{V}$ and $D = 0.344$ at $320\,\mathrm{V}$. The average inductor current equals the load current, $I_L = I_o = 1.82\,\mathrm{A}$.

---
## 3. Inductor

Inductor current ripple (peak to peak):

$$
\Delta i_L = \frac{V_o\,(1 - D)}{L\, f_{sw}} = \frac{110 \cdot 0.607}{4.7\,\mathrm{mH} \cdot 20\,\mathrm{kHz}} = 0.71\,\mathrm{A} \quad (39\,\%\ \text{of}\ I_o)
$$

$$
I_{L,max} = I_o + \tfrac{1}{2}\Delta i_L = 2.17\,\mathrm{A} \qquad I_{L,min} = 1.46\,\mathrm{A}
$$

Continuous conduction holds while $I_o > \Delta i_L / 2$:

$$
I_{o,B} = \frac{V_o (1 - D)}{2 L f_{sw}} = 0.36\,\mathrm{A} \quad\Rightarrow\quad R_{crit} = 310\,\Omega,\ P_{min} = 39\,\mathrm{W}
$$

Below $39\,\mathrm{W}$ (one 40 W lamp or less) the converter enters discontinuous conduction and $V_o$ rises above $D\,V_{in}$. Ripple at other frequencies, same $L$:

| $f_{sw}$ | $\Delta i_L$ | Ripple | $P_{min}$ (CCM) |
| -------- | ------------ | ------ | --------------- |
| $5\,\mathrm{kHz}$ | $2.84\,\mathrm{A}$ | $156\,\%$ | $156\,\mathrm{W}$ |
| $10\,\mathrm{kHz}$ | $1.42\,\mathrm{A}$ | $78\,\%$ | $78\,\mathrm{W}$ |
| $20\,\mathrm{kHz}$ | $0.71\,\mathrm{A}$ | $39\,\%$ | $39\,\mathrm{W}$ |
| $50\,\mathrm{kHz}$ | $0.28\,\mathrm{A}$ | $16\,\%$ | $16\,\mathrm{W}$ |

**Selected: $L = 4.7\,\mathrm{mH}$, $I_{sat} \geq 3\,\mathrm{A}$**, DC resistance $\leq 0.5\,\Omega$ (powder toroid or gapped ferrite). Stored energy at $I_{L,max}$: $\tfrac{1}{2} L I_{L,max}^2 = 11\,\mathrm{mJ}$. The inductor is external to the PCB (screw terminal `L`) so it can be swapped during the course.

---
## 4. Capacitors

**Output capacitor.** The inductor current ripple flows into $C_o$; with the triangular approximation,

$$
\Delta V_o = \frac{\Delta i_L}{8\, f_{sw}\, C_o}
\quad\Rightarrow\quad
C_o \geq \frac{0.71}{8 \cdot 20\,\mathrm{kHz} \cdot 1.1\,\mathrm{V}} = 4.0\,\mathrm{\mu F}
$$

**Selected: $4.7\,\mathrm{\mu F}$ film ($\geq 400\,\mathrm{V}$) in parallel with $47\,\mathrm{\mu F}$ electrolytic ($450\,\mathrm{V}$).** The film capacitor sets the switching ripple ($0.94\,\mathrm{V}$, $0.85\,\%$); the electrolytic adds low-frequency energy storage. Output capacitor RMS current: $\Delta i_L / \sqrt{12} = 0.21\,\mathrm{A}$. Both are rated for the full input voltage so that a wrong duty cycle (up to $D = 1$) cannot destroy them.

**Input capacitor.** The switch draws pulses of $I_o$ during $D T_s$, so the input capacitor must supply

$$
I_{C_{in},rms} = I_o\sqrt{D(1 - D)} = 1.82 \cdot 0.488 = 0.89\,\mathrm{A}
\qquad
\Delta V_{in} = \frac{I_o D (1 - D)}{f_{sw} C_{in}}
$$

**Selected: $2 \times 47\,\mathrm{\mu F}$, $450\,\mathrm{V}$ electrolytic in parallel with $4.7\,\mathrm{\mu F}$ film.** The film capacitor carries the high-frequency part of the $0.89\,\mathrm{A}$ and sets $\Delta V_{in} \approx 4.6\,\mathrm{V}$ ($1.6\,\%$); the electrolytics share about $0.3\,\mathrm{A}$ each.

---
## 5. Semiconductor stresses

| Device | Voltage | Average current | RMS current | Peak current |
| ------ | ------- | --------------- | ----------- | ------------ |
| $Q_1$ (switch) | $V_{in} = 280\,\mathrm{V}$ ($320$ max) | $D I_o = 0.72\,\mathrm{A}$ | $I_o\sqrt{D} = 1.14\,\mathrm{A}$ | $2.17\,\mathrm{A}$ |
| $D_1$ (freewheeling) | $V_{in}$ reverse | $(1 - D) I_o = 1.10\,\mathrm{A}$ | $I_o\sqrt{1 - D} = 1.42\,\mathrm{A}$ | $2.17\,\mathrm{A}$ |
| $L$ | — | $1.82\,\mathrm{A}$ | $1.83\,\mathrm{A}$ | $2.17\,\mathrm{A}$ |

With $320\,\mathrm{V}$ maximum input plus turn-off overshoot, **600 V devices** are used:

| Component | Selection | Notes |
| --------- | --------- | ----- |
| $Q_1$ | IGBT IRG4PC40UD (600 V, 20 A, with co-pack diode) or MOSFET IPW60R099C6 (650 V, 38 A) | Same TO-247 pinout G-C-E / G-D-S; MOSFET for $> 20\,\mathrm{kHz}$ |
| $D_1$ | STTH8R06D (600 V, 8 A, ultrafast, $t_{rr} = 25\,\mathrm{ns}$) | TO-220AC |
| Gate driver | HCPL-3120 with TMA-1215S isolated 15 V supply, $R_g = 22\,\Omega$ | Driver referenced to the emitter (switch node) |

---
## 6. Protection and measurement

- **Input inrush.** $98.7\,\mathrm{\mu F}$ at the input charged from the rectifier: a $10\,\Omega$ NTC in the positive input lead limits the first peak to $\approx 30\,\mathrm{A}$ and decays to $< 0.3\,\Omega$ warm.
- **Over-current.** $0.1\,\Omega$ shunt in the return rail, comparator threshold set with a trimmer (default $3\,\mathrm{A}$, i.e. $0.30\,\mathrm{V}$); on trip, the board pulls the `FAULT` line of the gate bus low and the gating block stops the PWM.
- **Over-voltage.** Output divider to the second comparator, default trip at $150\,\mathrm{V}$ (protects a 110 V lamp bank from a wrong duty cycle).
- **Test points.** `V_IN`, `SW` (switch node), `V_OUT`, `I_L` (shunt, $0.1\,\mathrm{V/A}$), `GND_P` (power return). Use a differential probe for `SW` and `V_IN`.
- **Fuse.** 5×20 mm, $3.15\,\mathrm{A}$ T in the input.

---
## 7. Summary

| Quantity | Value |
| -------- | ----- |
| $D$ at nominal | $0.393$ |
| $L$ / $\Delta i_L$ | $4.7\,\mathrm{mH}$ / $0.71\,\mathrm{A}$ ($39\,\%$) |
| $C_o$ / $\Delta V_o$ | $4.7\,\mathrm{\mu F}$ film + $47\,\mathrm{\mu F}$ / $0.94\,\mathrm{V}$ |
| $C_{in}$ / $\Delta V_{in}$ | $2 \times 47\,\mathrm{\mu F}$ + $4.7\,\mathrm{\mu F}$ film / $4.6\,\mathrm{V}$ |
| CCM limit | $39\,\mathrm{W}$ ($R < 310\,\Omega$) |
| Switch, diode | 600 V class, $I_{rms}$ $1.14$ / $1.42\,\mathrm{A}$ |

---
## 8. References

1. D. W. Hart, *Power Electronics*, McGraw-Hill, 2011, ch. 6 (buck converter).
2. R. W. Erickson, D. Maksimović, *Fundamentals of Power Electronics*, 3rd ed., Springer, 2020, ch. 2–3.
3. Broadcom, [HCPL-3120 datasheet](https://docs.broadcom.com/doc/AV02-0161EN).

---
## Links
- [Buck design with losses](02_losses.md)
- [Boost ideal design](../../03_boost/10_math/01_ideal.md)
- [Gate bus interface](../../00_docs/gate_bus_interface.md)
- [Project README](../../README.md)
