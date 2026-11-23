---
title: Architecture decisions
type: reference
---
# Architecture decisions

> [!NOTE]
> Record of the system-level decisions that shape all five boxes (four converters and the gating block): why the gate drive lives on the converter boards, why there is a common gate bus, which devices and ratings are shared, and how the boards are generated.

## 1. One external gating block, drivers on the converter boards

**Context.** The course needs to vary duty cycle, frequency, dead time and modulation while keeping students away from mains-referenced electronics. Previous quick builds used an ESP32 and an HCPL optocoupler on a breadboard next to the power stage. PSIM models the control as a separate *gating block* that is simply wired to the switch.

**Options considered.**
- *Drivers inside the gating block, gate wires to the boxes.* Compact block, but the gate wires carry the floating switch-node potential (up to 300 V) and the gate loop becomes long and inductive.
- *Drivers and isolated supplies on each converter board, only logic on the bus.* One more DC/DC module per switch, but the cable is low-voltage, the gate loop is short, and any box works with the same cable.

**Decision.** Logic-only gate bus; every converter board carries its own optocoupler drivers, isolated 15 V supplies and protection, powered from the 12 V that the bus provides.

**Consequences.**
- ✅ The cable can be touched while running; boxes are interchangeable.
- ✅ The same driver cell (HCPL-3120 + TMA-1215S) is reused on three boards.
- ⚠️ Cost of four DC/DC modules on the inverter board, two on each DC/DC board.

---
## 2. Gate bus: 16-way IDC ribbon

**Context.** Six PWM channels, an enable, a fault return and 12 V must travel up to one metre.

**Options considered.**
- *D-sub 15.* Robust, but needs soldered cables and the shell is large for the box wall.
- *RJ45 / Ethernet cable.* Only eight conductors; two cables needed.
- *2×8 IDC box header.* Cheap, crimped flat cable, keyed, fits a slot in a printed enclosure, 16 conductors.

**Decision.** IDC-16 with the pinout in the [gate bus interface](gate_bus_interface.md).

**Consequences.**
- ✅ Any lab can crimp a replacement cable in minutes.
- ⚠️ 28 AWG limits the bus to about 1 A; the 12 V is doubled on two pins.

---
## 3. ESP32 DevKitC on a universal socket

**Context.** The lab already programs ESP32 boards from the Arduino IDE; students should be able to replace the module without soldering.

**Options considered.**
- *Bare ESP32-WROOM-32E module with USB-serial on the board.* Smallest, but needs a USB bridge, antenna keep-out and reflow soldering.
- *DevKitC V4 plugged into two 19-pin socket rows.* Students can swap it, program it over its own USB, and the block's PCB stays through-hole.

**Decision.** DevKitC V4 on sockets. Because clone boards come with $0.9''$ and official boards with $1.0''$ row spacing, the footprint carries both spacings (four socket rows, pads of each pin paired), so either board fits.

**Consequences.**
- ✅ No SMD assembly on the gating block.
- ⚠️ The DevKitC USB ground ties the bus GND to the PC earth: the bus is therefore never used as a floating measurement reference.

---
## 4. Common semiconductor and capacitor platform

**Context.** Four different boards would otherwise need four bills of materials.

**Decision.** 600 V class, TO-247 IGBT IRG4PC40UD (MOSFET IPW60R099C6 as pin-compatible alternative) for all switches; STTH8R06D for all fast diodes; 20ETS08 for the line rectifier; $47\,\mathrm{\mu F}$/450 V electrolytics and $4.7\,\mathrm{\mu F}$/400 V film for every DC bus; $0.1\,\Omega$ shunts; LM393 + PC817 protection cell; 5.08 mm screw terminals.

**Consequences.**
- ✅ One purchase list, spare parts interchangeable between boxes.
- ⚠️ The IGBT limits the DC/DC boxes to about 20 kHz; the MOSFET option covers 50 kHz.

---
## 5. Open loop, with hardware protections

**Context.** The converters are teaching instruments: the duty cycle is a knob, not a regulated variable.

**Decision.** No voltage or current feedback in this version. Every box has an over-current comparator on its DC-return shunt and an over-voltage comparator on its most sensitive bus, both wired-OR into the `FAULT` line, plus input fuse, NTC inrush limiter and a bleeder/pilot LED on every bus above 60 V.

**Consequences.**
- ✅ The behaviour students see is the textbook open-loop behaviour (DCM voltage rise, boost runaway, dead-time distortion).
- ⚠️ The boost must never run without load; the OV trip is the only barrier.

---
## 6. Board size, layers and assembly

**Decision.** All boards are $100 \times 100\,\mathrm{mm}$ or smaller, two-layer (four layers for the inverter, see section 9), $2\,\mathrm{oz}$ copper recommended, through-hole components only, four M3 mounting holes on a $92 \times 92\,\mathrm{mm}$ pattern (the enclosure limit is $120 \times 120 \times 60\,\mathrm{mm}$). Power traces are $\geq 2.5\,\mathrm{mm}$ wide with $\geq 2.0\,\mathrm{mm}$ clearance between power nets and $\geq 6\,\mathrm{mm}$ between any power net and the gate-bus side.

**Consequences.**
- ✅ Hand-solderable by students, cheap at any PCB service.
- ⚠️ 100 mm limits the inverter to six TO-247 in a row with 15 mm spacing; the heatsink bar is shared.

---
## 7. Boards generated from code

**Context.** Five boards with repeated cells (driver, protection, bus connector) must stay consistent and reviewable.

**Decision.** Each project's schematic and PCB are produced by a Python script (`30_pcb/scripts/gen_*.py`) using the repository's KiCad skill: shared cells live in `90_tools/kicad_blocks/pe_blocks.py`; the schematic generator writes hierarchical sheets, a netlist-to-PCB step replaces the manual *Update PCB from schematic*, and placement, routing and silkscreen are driven by a JSON configuration. ERC and DRC run from `kicad-cli`; renders are stored in each box's `00_assets`.

**Consequences.**
- ✅ A change in the driver cell propagates to all boards by re-running the scripts.
- ⚠️ Manual edits in KiCad are overwritten by the next generation; edit the scripts instead, or stop generating that project.

---
## 8. Inverter DC link raised to 340 V by the boost box

**Context.** With the six-pulse rectifier ($\approx 280\,\mathrm{V}$) the inverter reaches at most $171\,\mathrm{V_{LL}}$ in the linear PWM range ($m_a = 1$), below the lab's $208\,\mathrm{V_{LL}}$.

**Options considered.**
- *Keep 280 V and accept $\approx 137\,\mathrm{V_{LL}}$ at $m_a = 0.8$.* No hardware change, but the inverter cannot reproduce the mains voltage.
- *Six-step operation.* Reaches $218\,\mathrm{V_{LL}}$ but only with the $31\,\%$ THD square wave.
- *Feed the inverter from the boost box at 340 V.* Linear range up to $208\,\mathrm{V_{LL}}$, and the two boxes are used together in a lab session.

**Decision.** The inverter's nominal DC link becomes $340\,\mathrm{V}$, supplied by the boost box from the lab's $110\,\mathrm{V}$ source. The rectifier remains a valid source for lower output voltages.

**Consequences.**
- ✅ $208\,\mathrm{V_{LL}}$ needs $m_a = 208 / (0.612 \cdot 340) = 1.00$ ideally; lamps of $110\,\mathrm{V}$ in Y ($190\,\mathrm{V_{LL}}$) need $m_a = 0.91$.
- ⚠️ With dead time and device drops, $208\,\mathrm{V_{LL}}$ needs $m_a \approx 1.05$: slight overmodulation, which the gating block supports up to $1.15$.
- ⚠️ Boost: $D = 1 - 110/340 = 0.676$. Its over-voltage trip, set today at $348\,\mathrm{V}$ ($6.8\,\mathrm{k\Omega}$), must rise to about $381\,\mathrm{V}$ ($6.2\,\mathrm{k\Omega}$, the same as the inverter); the $450\,\mathrm{V}$ capacitors keep $18\,\%$ margin.
- ⚠️ Open: the boost is rated $200\,\mathrm{W}$ and the inverter $300\,\mathrm{W}$. Either the boost is re-rated to $300\,\mathrm{W}$ ($I_L \approx 2.9\,\mathrm{A}$ average, within the 600 V / 20 A devices but at the limit of a $3\,\mathrm{A}$ inductor and of the lab supply current), or the inverter is limited to $200\,\mathrm{W}$ when fed from the boost. To be decided in the boost stage.

---
## 9. Inverter board on four layers

**Context.** On two layers and $115 \times 115\,\mathrm{mm}$ the inverter (six TO-247, six drivers, four isolated supplies, protection) left 65 pads unrouted and exceeded the $100\,\mathrm{mm}$ board limit of section 6.

**Decision.** The inverter moves to a four-layer, $1.6\,\mathrm{mm}$ board within $100 \times 100\,\mathrm{mm}$. Inner layers carry split planes per isolation domain (gate-bus GND, each floating driver supply, power common), keeping the $6\,\mathrm{mm}$ gap between domains on every layer. The other boards stay on two layers.

**Consequences.**
- ✅ Shorter gate loops and a return plane under each driver.
- ⚠️ The script router only handles F.Cu/B.Cu today; the skill needs inner-layer planes per domain and routing on four layers before the inverter can be regenerated.
- ⚠️ Higher fabrication cost for one board.

---
## 10. Purchased inductor for the DC/DC boxes

**Context.** Buck and boost share an external inductor of $4.7\,\mathrm{mH}$ that must carry $1.8\,\mathrm{A}$ average and about $2.2\,\mathrm{A}$ peak without saturating ($3\,\mathrm{A}$ or more if the boost is re-rated to $300\,\mathrm{W}$). Surface-mount power inductors with several amperes of saturation current are in the microhenry range; the millihenry surface-mount and radial parts saturate near $0.15\,\mathrm{A}$.

**Decision.** Buy a chassis-mount power choke of $4.7$–$10\,\mathrm{mH}$ with a DC rating of at least $4\,\mathrm{A}$, connected to the `L` terminal block. Candidates found: Hammond 157E ($6\,\mathrm{mH}$, $4\,\mathrm{A}$) and Hammond 159ZJ ($10\,\mathrm{mH}$, $5\,\mathrm{A}$, $0.16\,\Omega$). Winding a powder-core toroid remains the fallback.

**Consequences.**
- ✅ A higher inductance lowers the ripple and the CCM limit; $0.16\,\Omega$ is below the $0.4\,\Omega$ assumed in the loss reports.
- ⚠️ The ripple, CCM limit and loss tables must be recalculated with the chosen part. Its size and mounting go into the enclosure design, outside the $12 \times 12 \times 6\,\mathrm{cm}$ box.

---
## 11. Lab characterisation of transformers and reactor

**Context.** The loss models assume a transformer leakage of $L_s = 1\,\mathrm{mH}$ per phase and a $20\,\mathrm{mH}$ reactor. New phase-shifting transformers are arriving for the 12- and 24-pulse tests.

**Decision.** Measure each new transformer (open-circuit and short-circuit tests: magnetising branch, leakage inductance, winding resistance, phase shift between secondaries) and the reactor (inductance at $60\,\mathrm{Hz}$ and its DC resistance) as a lab experiment of the rectifier stage. The measured values replace the assumptions in the rectifier and inverter loss reports.

**Consequences.**
- ✅ The commutation overlap, regulation and ripple predictions become checkable against measurement.
- ⚠️ The rectifier stage needs a test procedure before the transformers are used.

---
## Links
- [Gate bus interface](gate_bus_interface.md)
- [Project README](../README.md)

---
## Enlaces
[[power_electronics|Power Electronics]]
