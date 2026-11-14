"""Generates the gating block KiCad project (schematic + PCB) in 05_gating_block/30_pcb/gating_block/.

    python gen_gating_block.py            # schematic + PCB pipeline (place, route, silk, DRC)
    python gen_gating_block.py --sch      # schematic only

Signal budget and pin map: 05_gating_block/10_math/01_signal_budget.md, 00_docs/gate_bus_interface.md.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "90_tools", "kicad_blocks"))
import pe_blocks as pe                                   # noqa: E402
from kicad_sch_gen import Design                         # noqa: E402

OUT = os.path.join(HERE, "..", "gating_block")
PROJECT = "gating_block"
FP = pe.FP

# ESP32 GPIO assignment (DevKitC pin names as in pe_blocks.DEVKIT_*)
GPIO = {
    "IO25": "PWM1_M", "IO26": "PWM2_M", "IO27": "PWM3_M", "IO14": "PWM4_M", "IO13": "PWM5_M", "IO23": "PWM6_M",
    "IO4": "EN_M", "IO32": "SYNC", "IO34": "FAULT", "IO35": "RUN_SW",
    "IO18": "ENC_A", "IO19": "ENC_B", "IO5": "ENC_SW", "IO21": "SDA", "IO22": "SCL",
    "IO33": "BTN1", "VP/IO36": "BTN2", "IO2": "LED_RUN", "IO16": "LED_FLT", "IO17": "SPARE",
}


def build():
    d = Design(PROJECT, power_nets=("+12V", "+5V", "+3V3", "GND"),
               title_block=dict(company="UPB - Power Electronics", rev="0.1",
                                comments=["Gating block: ESP32 PWM generator with 5 V buffered gate bus"]))
    d.add_lib("pe_lib", pe.devkit_symbol_lib(), "ESP32 DevKitC and project symbols")
    sh = d.root("A3", title="Gating block (ESP32 DevKitC + 74HCT541 gate bus driver)")

    # --- Power input: 12 V jack, polyfuse, reverse diode, 5 V switching regulator
    sh.rect(20, 30, 150, 80, "Power: 12 V in -> 5 V (TSR 1-2450); 12 V also feeds the gate bus")
    sh.part("Connector:Barrel_Jack_Switch", "J1", "12V DC", 30, 50, {"1": "VJ", "2": "GND", "3": "NC"}, fp=FP["JACK"])
    sh.two("Device:Polyfuse", "F1", "1.1A", 50, 44, "VJ", "VF", fp=FP["POLYFUSE"])
    sh.two("Device:D_Schottky", "D1", "1N5822", 66, 44, "+12V", "VF", fp=FP["D_DO201"])
    sh.two("Device:C_Polarized", "C1", "100u/25V", 82, 50, "+12V", "GND", fp=FP["C_100u25"])
    sh.two("Device:C", "C2", "100n", 90, 50, "+12V", "GND", fp=FP["C_100n"])
    sh.part("Converter_DCDC:TSR_1-2450", "U1", "TSR 1-2450", 110, 50, {"1": "+12V", "2": "GND", "3": "+5V"}, fp=FP["TSR"])
    sh.two("Device:C_Polarized", "C3", "10u/25V", 130, 50, "+5V", "GND", fp=FP["C_10u25"])
    sh.two("Device:C", "C4", "100n", 138, 50, "+5V", "GND", fp=FP["C_100n"])
    sh.two("Device:R", "R1", "2k2", 100, 66, "+12V", "LED12", fp=FP["R"])
    sh.two("Device:LED", "D4", "YELLOW 12V", 112, 66, "GND", "LED12", fp=FP["LED3"])
    sh.part("power:PWR_FLAG", "#FLG1", "PWR_FLAG", 70, 70, {"1": "GND"})
    sh.part("power:PWR_FLAG", "#FLG2", "PWR_FLAG", 80, 70, {"1": "+12V"})

    # --- ESP32 DevKitC
    sh.rect(20, 95, 110, 200, "ESP32-DevKitC V4 (socketed, programmed over its own USB)")
    conns = {}
    for name in pe.DEVKIT_LEFT + pe.DEVKIT_RIGHT:
        num = pe.DEVKIT_PIN[name] if name != "GND" else None
        if name == "GND":
            continue
        net = GPIO.get(name)
        if name == "3V3":
            net = "+3V3"
        elif name == "5V":
            net = "+5V"
        conns[num] = net or "NC"
    for num in ("14", "20", "26"):
        conns[num] = "GND"
    sh.part("pe_lib:ESP32-DevKitC-V4", "A1", "ESP32-DevKitC-V4", 60, 150, conns, fp="pe_lib:ESP32-DevKitC-V4_Socket")

    # --- 74HCT541 buffer: 3.3 V -> 5 V, tri-state when RUN/STOP open or FAULT low
    sh.rect(120, 95, 250, 200, "5 V gate-bus buffer with hardware enable (RUN/STOP switch and FAULT)")
    sh.part("74xx:74HCT541", "U2", "74HCT541", 160, 140,
            {"1": "OE1", "19": "OE2", "2": "PWM1_M", "3": "PWM2_M", "4": "PWM3_M", "5": "PWM4_M", "6": "PWM5_M",
             "7": "PWM6_M", "8": "EN_M", "9": "GND", "18": "PWM1", "17": "PWM2", "16": "PWM3", "15": "PWM4",
             "14": "PWM5", "13": "PWM6", "12": "EN", "11": "NC", "10": "GND", "20": "+5V"}, fp=FP["DIP20"])
    sh.two("Device:C", "C5", "100n", 184, 112, "+5V", "GND", fp=FP["C_100n"])
    for k, net in enumerate(["PWM1", "PWM2", "PWM3", "PWM4", "PWM5", "PWM6", "EN"]):
        sh.two("Device:R", f"R{10+k}", "10k", 200 + 6 * k, 170, net, "GND", fp=FP["R"])
    # OE1: RUN/STOP panel switch (closed = run), pulled up to 3.3 V, also read by the ESP32
    sh.part("Connector:Conn_01x02_Pin", "J3", "RUN/STOP", 130, 112, {"1": "RUN_SW", "2": "GND"}, fp=FP["HDR1x2"])
    sh.two("Device:R", "R2", "10k", 140, 104, "+3V3", "RUN_SW", fp=FP["R"])
    sh.two("Device:C", "C6", "100n", 140, 120, "RUN_SW", "GND", fp=FP["C_100n"])
    sh.two("Device:R", "R3", "0R", 140, 128, "RUN_SW", "OE1", fp=FP["R"])
    # OE2: FAULT low -> Q1 off -> OE2 pulled high -> outputs tri-state
    sh.two("Device:R", "R4", "4k7", 130, 150, "+3V3", "FAULT", fp=FP["R"])
    sh.two("Device:R", "R5", "10k", 130, 160, "FAULT", "Q1B", fp=FP["R"])
    sh.part("Transistor_BJT:2N3904", "Q1", "2N3904", 140, 182, {"1": "GND", "2": "Q1B", "3": "OE2"},
            fp="Package_TO_SOT_THT:TO-92_Inline")
    sh.two("Device:R", "R6", "10k", 130, 176, "+5V", "OE2", fp=FP["R"])

    # --- Gate bus connector and scope header
    sh.rect(260, 95, 360, 160, "Gate bus (IDC-16) and scope header")
    sh.part("Connector_Generic:Conn_02x08_Odd_Even", "J2", "GATE_BUS", 280, 120,
            {"1": "+12V", "2": "+12V", "3": "GND", "4": "GND", "5": "PWM1", "6": "PWM2", "7": "PWM3", "8": "PWM4",
             "9": "PWM5", "10": "PWM6", "11": "FAULT", "12": "EN", "13": "+5V", "14": "GND", "15": "GND", "16": "GND"},
            fp=FP["IDC16"])
    sh.part("Connector:Conn_01x08_Pin", "J5", "SCOPE", 320, 120,
            {"1": "PWM1", "2": "PWM2", "3": "PWM3", "4": "PWM4", "5": "PWM5", "6": "PWM6", "7": "SYNC", "8": "GND"},
            fp=FP["HDR1x8"])

    # --- User interface: encoder, buttons, OLED, LEDs
    sh.rect(260, 170, 400, 260, "User interface: encoder with push, two buttons, OLED I2C, LEDs")
    sh.part("Device:RotaryEncoder_Switch", "SW1", "EC11", 280, 190,
            {"A": "ENC_A", "B": "ENC_B", "C": "GND", "S1": "ENC_SW", "S2": "GND"}, fp=FP["ENC"])
    for k, net in enumerate(["ENC_A", "ENC_B", "ENC_SW", "BTN1", "BTN2"]):
        sh.two("Device:R", f"R{20+k}", "10k", 300 + 6 * k, 180, "+3V3", net, fp=FP["R"])
    sh.two("Device:C", "C7", "100n", 300, 200, "ENC_A", "GND", fp=FP["C_100n"])
    sh.two("Device:C", "C8", "100n", 306, 200, "ENC_B", "GND", fp=FP["C_100n"])
    sh.part("Switch:SW_Push", "SW2", "BACK", 290, 215, {"1": "BTN1", "2": "GND"}, fp=FP["SW"])
    sh.part("Switch:SW_Push", "SW3", "RESET", 290, 228, {"1": "BTN2", "2": "GND"}, fp=FP["SW"])
    sh.part("Connector:Conn_01x04_Socket", "J4", "OLED I2C", 350, 190, {"1": "GND", "2": "+3V3", "3": "SCL", "4": "SDA"},
            fp=FP["SOCK1x4"])
    sh.two("Device:R", "R25", "4k7", 340, 180, "+3V3", "SDA", fp=FP["R"])
    sh.two("Device:R", "R26", "4k7", 346, 180, "+3V3", "SCL", fp=FP["R"])
    sh.two("Device:R", "R27", "330", 330, 215, "LED_RUN", "LEDR_K", fp=FP["R"])
    sh.two("Device:LED", "D2", "GREEN RUN", 342, 215, "GND", "LEDR_K", fp=FP["LED3"])
    sh.two("Device:R", "R28", "330", 330, 228, "LED_FLT", "LEDF_K", fp=FP["R"])
    sh.two("Device:LED", "D3", "RED FAULT", 342, 228, "GND", "LEDF_K", fp=FP["LED3"])
    sh.part("Connector:Conn_01x02_Pin", "J6", "SPARE IO17", 370, 215, {"1": "SPARE", "2": "GND"}, fp=FP["HDR1x2"])
    pe.mounting_holes(sh, 300, 250)

    pro_tpl = pe.pro_template(os.path.join(HERE, "pro_template.json"))
    classes = [dict(pe.NETCLASS_BASE, name="Default"),
               dict(pe.NETCLASS_BASE, name="Supply", clearance=0.25, track_width=0.8)]
    patterns = {"+12V": "Supply", "+5V": "Supply", "+3V3": "Supply", "/VJ": "Supply", "/VF": "Supply"}
    d.write(OUT, template_pro=pro_tpl, netclasses=classes, patterns=patterns, rules=pe.RULES)
    pe.write_custom_libs(OUT)
    os.remove(pro_tpl)
    print("schematic written to", os.path.normpath(OUT))


if __name__ == "__main__":
    build()
    if "--sch" not in sys.argv:
        rc = subprocess.run([sys.executable, os.path.join(pe.SKILL, "pcb_pipeline.py"),
                             os.path.join(OUT, PROJECT + ".kicad_pro"), os.path.join(HERE, "pcb_config.json")]
                            + [a for a in sys.argv[1:] if a.startswith("--")]).returncode
        sys.exit(rc)
