"""Generates the six-pulse rectifier KiCad project (schematic + PCB) in 01_rectifier/30_pcb/rectifier_6p/.

    python gen_rectifier.py            # schematic + .kicad_pro, then the PCB pipeline (place, route, silk, DRC)
    python gen_rectifier.py --sch      # schematic only

Design values: 01_rectifier/10_math/01_ideal.md and 02_losses.md.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "90_tools", "kicad_blocks"))
import pe_blocks as pe                                   # noqa: E402  (adds the skill scripts to sys.path)
from kicad_sch_gen import Design                         # noqa: E402

OUT = os.path.join(HERE, "..", "rectifier_6p")
PROJECT = "rectifier_6p"


def build():
    d = Design(PROJECT, power_nets=(), title_block=dict(company="UPB - Power Electronics", rev="0.1",
                                                        comments=["Six-pulse diode rectifier box, 208 V LL, 5 A"]))
    sh = d.root("A3", title="Six-pulse rectifier (6P box)")

    # --- AC input: terminals, fuses, test points
    sh.rect(20, 30, 110, 110, "AC input 208 V LL")
    sh.part("Connector:Screw_Terminal_01x03", "J1", "AC IN", 30, 60, {"1": "A", "2": "B", "3": "C"}, fp=pe.FP["TB3"])
    for k, ph in enumerate("ABC"):
        sh.two("Device:Fuse", f"F{k+1}", "6.3A T", 60, 50 + 15 * k, ph, f"{ph}_F", fp=pe.FP["FUSE"])
        pe.test_point(sh, f"TP{k+1}", f"{ph}_F", 90, 50 + 15 * k)

    # --- Diode bridge: upper group to DC+, lower group from DCN (diode pin 1 = cathode, pin 2 = anode)
    sh.rect(120, 30, 230, 110, "Graetz bridge, 6 x 20ETS08 (800 V, 20 A)")
    for k, ph in enumerate("ABC"):
        upper, lower = [1, 3, 5][k], [4, 6, 2][k]
        sh.two("Device:D", f"D{upper}", "20ETS08", 140 + 30 * k, 50, "DC+", f"{ph}_F", fp=pe.FP["TO220_2"])
        sh.two("Device:D", f"D{lower}", "20ETS08", 140 + 30 * k, 90, f"{ph}_F", "DCN", fp=pe.FP["TO220_2"])

    # --- DC output: shunt, snubber, varistor, bleeder + pilot LED, terminals, test points
    sh.rect(240, 30, 380, 120, "DC output: shunt 0.1 V/A, RC snubber, varistor, bleeder/pilot LED")
    sh.two("Device:R", "R1", "0R1/5W", 250, 100, "DCN", "DC-", fp=pe.FP["R_5W"])
    sh.two("Device:R", "R2", "47R/2W", 270, 50, "DC+", "SNUB", fp=pe.FP["R_2W"])
    sh.two("Device:C", "C1", "100n/630V", 270, 70, "SNUB", "DC-", fp=pe.FP["C_100n_630"])
    sh.two("Device:Varistor", "RV1", "S14K320", 290, 60, "DC+", "DC-", fp=pe.FP["MOV"])
    pe.bleeder_led(sh, 300, 90, "DC+", "DC-", pe.Refs("R", 3), "D7", title="Bleeder / DC present")
    sh.part("Connector:Screw_Terminal_01x02", "J2", "DC OUT", 360, 60, {"1": "DC+", "2": "DC-"}, fp=pe.FP["TB2"])
    pe.test_point(sh, "TP4", "DC+", 340, 45)
    pe.test_point(sh, "TP5", "DCN", 340, 95)
    pe.test_point(sh, "TP6", "DC-", 340, 110)
    pe.mounting_holes(sh, 250, 135)
    sh.text("Floating box: no terminal is bonded to the enclosure. Series/parallel connection of several boxes "
            "for 12- and 24-pulse operation.", 20, 150, size=1.5, bold=False)

    pro_tpl = pe.pro_template(os.path.join(HERE, "pro_template.json"))
    # local labels on the root sheet become nets named "/<label>"
    patterns = {"/A": "Power", "/B": "Power", "/C": "Power", "/?_F": "Power", "/DC+": "Power", "/DC-": "Power",
                "/DCN": "Power", "/SNUB": "HV_signal", "/DC+_BL*": "HV_signal"}
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
