---
title: "KiCad projects generated from code"
type: reference
---
# KiCad projects generated from code

> [!NOTE]
> How the five KiCad projects of this repository are produced, where the sources of truth are, and how to regenerate or modify a board without losing the design intent.

## 1. Sources of truth

| Item | Where | Edit here |
| ---- | ----- | --------- |
| Circuit (parts, values, nets) | `0N_<box>/30_pcb/scripts/gen_<box>.py` | yes |
| Shared cells (gate driver, protection, gate bus, DC bus capacitors, bleeder, ESP32 socket) | `90_tools/kicad_blocks/pe_blocks.py` | yes |
| Board size, placement, net classes, routing and silkscreen options | `0N_<box>/30_pcb/scripts/pcb_config.json` | yes |
| KiCad files (`.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, `pe_lib.*`) | `0N_<box>/30_pcb/<project>/` | no: regenerated |
| Reports and renders | `0N_<box>/30_pcb/<project>/out/` (ignored by git); final images copied to `0N_<box>/00_assets/` | no |
| Generator scripts | `.claude/skills/kicad-flow/scripts/` | yes |

The KiCad files can be opened, inspected and even fabricated from directly; any manual change in KiCad is overwritten the next time the generator runs, so changes go into the scripts or the JSON.

---
## 2. Regenerating a board

```bash
cd 02_buck/30_pcb/scripts
python gen_buck.py            # schematic, PCB, placement, routing, silkscreen, ERC and DRC
python gen_buck.py --sch      # schematic only (fast; check ERC)
```

Requirements: KiCad 10 installed in the default Windows location (the scripts call `kicad-cli.exe` and KiCad's own Python with `pcbnew`), system Python 3.12 for the generators. The pipeline prints the routing result per net class and ends with the DRC summary; the return code is non-zero when nets are left unrouted or the DRC reports violations.

Partial runs, after a change in the JSON only:

```bash
python ../../../.claude/skills/kicad-flow/scripts/pcb_pipeline.py ../buck/buck.kicad_pro pcb_config.json --from place
```

`--from route` re-routes from scratch; `--keep-tracks` keeps existing tracks (manual routing) and only completes the missing ones; `--fab` also exports Gerbers and drill files to `out/gerbers/`.

---
## 3. Checking a placement before routing

Routing a board takes 10–20 minutes. The placement step reports every footprint's courtyard and the overlaps in seconds:

```bash
"/c/Program Files/KiCad/10.0/bin/python.exe" -I ../../../.claude/skills/kicad-flow/scripts/pcb_place.py ../buck/buck.kicad_pcb pcb_config.json --report
```

Coordinates in the JSON are millimetres from the top-left corner of the board; the anchor `c` is the footprint origin (pin 1 for almost all through-hole parts). A rotation of 90° turns +x into −y (upwards on screen); vertical 1/4 W resistors therefore use 270° so that pin 2 lies below pin 1.

---
## 4. Net classes and clearances

| Class | Track | Clearance | Via | Used for |
| ----- | ----- | --------- | --- | -------- |
| Power | 2.5 mm | 2.0 mm | 1.6 / 0.8 mm | Buses and switch nodes that only touch parts with ≥ 5 mm pad pitch |
| HV_signal | 0.5 mm | 0.6 mm | 0.8 / 0.4 mm | High-voltage nets that reach 2.54 mm parts (gate resistors, driver supply, bleeder chain, divider) |
| Aux | 0.5 mm | 0.3 mm | 0.8 / 0.4 mm | Comparator and reference nets on the isolated 15 V side |
| Default | 0.3 mm | 0.2 mm | 0.8 / 0.4 mm | Gate-bus logic |

The same values are written to the `.kicad_pro` net classes (with their patterns) so that KiCad's DRC and the script router agree. The isolation barrier between the gate-bus side and the power side is at least 6 mm and runs between the two pin rows of the optocouplers and between the input and output pins of the isolated DC/DC modules.

---
## 5. Known limits of this version

- Routing is a grid A* with 45° segments; power traces are not yet widened into polygons. For fabrication, review the power paths in KiCad and, if desired, add copper pours by hand on a copy that is no longer generated.
- Heatsinks, the external inductor and the enclosure are not on the PCB; they are mechanical items of stage 40.
- Silkscreen references are placed automatically; a few may need manual nudging (`silk.manual` in the JSON).

---
## Links
- [Architecture decisions](architecture.md)
- [Gate bus interface](gate_bus_interface.md)
- [Project README](../README.md)

---
## Enlaces
[[power_electronics|Power Electronics]]
