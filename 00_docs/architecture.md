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

**Decision.** All boards are $100 \times 100\,\mathrm{mm}$ or smaller, two-layer, $2\,\mathrm{oz}$ copper recommended, through-hole components only, four M3 mounting holes on a $92 \times 92\,\mathrm{mm}$ pattern (the enclosure limit is $120 \times 120 \times 60\,\mathrm{mm}$). Power traces are $\geq 2.5\,\mathrm{mm}$ wide with $\geq 2.0\,\mathrm{mm}$ clearance between power nets and $\geq 6\,\mathrm{mm}$ between any power net and the gate-bus side.

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
## Links
- [Gate bus interface](gate_bus_interface.md)
- [Project README](../README.md)

---
## Enlaces
[[power_electronics|Power Electronics]]
