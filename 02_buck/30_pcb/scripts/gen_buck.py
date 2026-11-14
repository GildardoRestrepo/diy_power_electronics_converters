"""Generates the buck converter KiCad project (schematic + PCB) in 02_buck/30_pcb/buck/.

    python gen_buck.py            # schematic + PCB pipeline (place, route, silk, DRC)
    python gen_buck.py --sch      # schematic only

Design values: 02_buck/10_math/01_ideal.md and 02_losses.md. Gate bus: 00_docs/gate_bus_interface.md.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "90_tools", "kicad_blocks"))
import pe_blocks as pe                                   # noqa: E402
from kicad_sch_gen import Design                         # noqa: E402

OUT = os.path.join(HERE, "..", "buck")
PROJECT = "buck"
FP = pe.FP


def build():
    d = Design(PROJECT, power_nets=("+12V", "GND"),
               title_block=dict(company="UPB - Power Electronics", rev="0.1",
                                comments=["Buck converter box 300 V -> 110 V, 200 W, external 4.7 mH inductor"]))
    sh = d.root("A3", title="Buck converter 300 V -> 110 V (external gating block)")

    # --- Gate bus, driver cell (high-side switch, floating supply) and protection cell (own supply)
    pe.gate_bus(sh, 20, 30, used=(1,), ref="J1")
    pe.driver_cell(sh, 1, 90, 30, "PWM1", "G1", "SW", supply=True, title="Gate driver Q1 (high side, floating 15 V)")
    pe.protection_cell(sh, 20, 90, "VCC9", "VOUT", "16k", i_trip_label="3 A", ov_label="(V_OUT > 150 V)", with_supply=True)

    # --- Power stage
    sh.rect(180, 30, 400, 150, "Power stage: V_IN 150-320 V -> V_OUT 110 V, 20 kHz, L = 4.7 mH external")
    sh.part("Connector:Screw_Terminal_01x02", "J2", "DC IN", 190, 60, {"1": "VIN+", "2": "GND_P"}, fp=FP["TB2"])
    sh.two("Device:Fuse", "F1", "3.15A T", 205, 46, "VIN+", "VF", fp=FP["FUSE"])
    sh.two("Device:Thermistor_NTC", "TH1", "NTC 10R", 220, 46, "VF", "VIN", fp=FP["NTC"])
    pe.dc_bus_caps(sh, 230, 60, "VIN", "COM", pe.Refs("C", 1), n_elec=2, title="Input bus 2 x 47u/450V + 4.7u film")
    sh.part("Device:Q_NIGBT_GCE", "Q1", "IRG4PC40UD", 280, 50, {"1": "G1", "2": "VIN", "3": "SW"}, fp=FP["TO247"])
    sh.two("Device:D", "D1", "STTH8R06D", 300, 70, "SW", "COM", fp=FP["TO220_2"])
    sh.part("Connector:Screw_Terminal_01x02", "J3", "L 4.7mH", 320, 50, {"1": "SW", "2": "VOUT"}, fp=FP["TB2"])
    pe.dc_bus_caps(sh, 330, 80, "VOUT", "COM", pe.Refs("C", 4), n_elec=1, title="Output bus 47u/450V + 4.7u film")
    pe.bleeder_led(sh, 330, 110, "VOUT", "COM", pe.Refs("R", 1), "D2", title="Bleeder / V_OUT present")
    sh.part("Connector:Screw_Terminal_01x02", "J4", "DC OUT", 380, 60, {"1": "VOUT", "2": "COM"}, fp=FP["TB2"])
    pe.test_point(sh, "TP1", "VIN", 250, 120)
    pe.test_point(sh, "TP2", "SW", 270, 120)
    pe.test_point(sh, "TP3", "VOUT", 290, 120)
    pe.test_point(sh, "TP4", "COM", 250, 135)
    pe.test_point(sh, "TP5", "GND_P", 270, 135)
    pe.mounting_holes(sh, 300, 135)
    sh.text("Shunt R90 (0.1 ohm) between COM (internal power common) and GND_P (V_IN- terminal): "
            "TP4-TP5 = 0.1 V/A of input current. Gate bus side is isolated from the power stage.", 20, 160,
            size=1.5, bold=False)

    pro_tpl = pe.pro_template(os.path.join(HERE, "pro_template.json"))
    patterns = {"/VIN+": "Power", "/VF": "Power", "/VIN": "Power", "/SW": "Power", "/VOUT": "Power", "/COM": "Power",
                "/GND_P": "Power", "/G1": "HV_signal", "/VO1": "HV_signal", "/VCC1": "HV_signal",
                "/VOUT_BL*": "HV_signal", "/OVMID": "HV_signal", "/VCC9": "Aux", "/ISENSE": "Aux", "/IREF*": "Aux",
                "/OVSENSE": "Aux", "/VREF": "Aux", "/FLT*": "Aux"}
    d.write(OUT, template_pro=pro_tpl, netclasses=pe.POWER_CLASSES, patterns=patterns, rules=pe.RULES)
    os.remove(pro_tpl)
    print("schematic written to", os.path.normpath(OUT))


if __name__ == "__main__":
    build()
    if "--sch" not in sys.argv:
        rc = subprocess.run([sys.executable, os.path.join(pe.SKILL, "pcb_pipeline.py"),
                             os.path.join(OUT, PROJECT + ".kicad_pro"), os.path.join(HERE, "pcb_config.json")]
                            + [a for a in sys.argv[1:] if a.startswith("--")]).returncode
        sys.exit(rc)
