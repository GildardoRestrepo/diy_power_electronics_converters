"""Shared KiCad building blocks for the power-electronics boxes.

Imported by every `0N_<box>/30_pcb/scripts/gen_*.py`. Provides:
  - FP: footprint names of the common parts (all through-hole).
  - PRO: template for the .kicad_pro (design rules + net classes shared by all boards).
  - Schematic cells drawn on a flat sheet with the skill's `kicad_sch_gen.Sheet`:
      driver_cell()      HCPL-3120 + isolated 15 V supply + gate resistors   (one per switch)
      protection_cell()  shunt + LM393 over-current / over-voltage + PC817 fault return
      gate_bus()         2x8 IDC gate-bus connector with its decoupling and "armed" LED
      dc_bus_caps()      electrolytic + film capacitors of a DC bus
      bleeder_led()      bleeder resistors + pilot LED across a DC bus
      test_point(), mounting_holes()
  - ESP32 DevKitC V4 custom symbol/footprint text (universal 0.9"/1.0" socket).

Net naming convention used by all boards (see 00_docs/gate_bus_interface.md):
  GND, +12V, +5V, +3V3           gate-bus (logic) side, power symbols
  PWM1..PWM6, FAULT, EN          gate-bus signals
  GND_P                          power return at the terminals (comparator ground, TMA -Vout)
  COM                            internal power common, GND_P + shunt (emitters of low-side switches)
  VCC<n>, VEE<n>, VO<n>, LEDA<n>, G<n>   nets of driver cell n (VEE<n> is the switch emitter)
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.normpath(os.path.join(HERE, "..", "..", ".claude", "skills", "kicad-flow", "scripts"))
sys.path.insert(0, SKILL)

FP = dict(
    R="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",        # 1/4 W
    R_1W="Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P15.24mm_Horizontal",    # 1 W
    R_2W="Resistor_THT:R_Axial_DIN0617_L17.0mm_D6.0mm_P20.32mm_Horizontal",    # 2 W
    R_5W="Resistor_THT:R_Axial_Power_L20.0mm_W6.4mm_P25.40mm",                  # 5 W ceramic
    TRIM="Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical",
    C_100n="Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
    C_10n="Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
    C_10u25="Capacitor_THT:C_Radial_D5.0mm_H11.0mm_P2.00mm",
    C_100u25="Capacitor_THT:C_Radial_D8.0mm_H11.5mm_P3.50mm",
    C_47u450="Capacitor_THT:C_Radial_D16.0mm_H25.0mm_P7.50mm",
    C_4u7_400="Capacitor_THT:C_Rect_L31.5mm_W15.0mm_P27.50mm_MKS4",
    C_100n_630="Capacitor_THT:C_Rect_L13.0mm_W5.0mm_P10.00mm_FKS3_FKP3_MKS4",
    DIP4="Package_DIP:DIP-4_W7.62mm",
    DIP8="Package_DIP:DIP-8_W7.62mm",
    DIP20="Package_DIP:DIP-20_W7.62mm",
    TO247="Package_TO_SOT_THT:TO-247-3_Vertical",
    TO220_2="Package_TO_SOT_THT:TO-220-2_Vertical",
    TO220_3="Package_TO_SOT_THT:TO-220-3_Vertical",
    TMA="Converter_DCDC:Converter_DCDC_TRACO_TMA-05xxS_12xxS_Single_THT",
    TSR="Converter_DCDC:Converter_DCDC_TRACO_TSR-1_THT",
    TB2="TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
    TB3="TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal",
    FUSE="Fuse:Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open",
    IDC16="Connector_IDC:IDC-Header_2x08-1MP_P2.54mm_Latch9.5mm_Vertical",
    HDR1x2="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
    HDR1x4="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
    HDR1x8="Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical",
    SOCK1x4="Connector_PinSocket_2.54mm:PinSocket_1x04_P2.54mm_Vertical",
    LED5="LED_THT:LED_D5.0mm",
    LED3="LED_THT:LED_D3.0mm",
    MOV="Varistor:RV_Disc_D15.5mm_W4.2mm_P7.5mm",
    NTC="Varistor:RV_Disc_D15.5mm_W4.2mm_P7.5mm",
    TP="TestPoint:TestPoint_Loop_D2.50mm_Drill1.0mm",
    MH="MountingHole:MountingHole_3.2mm_M3",
    ENC="Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm",
    JACK="Connector_BarrelJack:BarrelJack_Horizontal",
    SW="Button_Switch_THT:SW_PUSH_6mm_H13mm",
    D_DO41="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",
    D_DO201="Diode_THT:D_DO-201AD_P15.24mm_Horizontal",
    POLYFUSE="Fuse:Fuse_Bourns_MF-RG1100",
)

# ------------------------------------------------------------------ .kicad_pro template
NETCLASS_BASE = dict(bus_width=12, clearance=0.2, diff_pair_gap=0.25, diff_pair_via_gap=0.25, diff_pair_width=0.2,
                     line_style=0, microvia_diameter=0.3, microvia_drill=0.1, pcb_color="rgba(0, 0, 0, 0.000)",
                     schematic_color="rgba(0, 0, 0, 0.000)", track_width=0.3, via_diameter=0.8, via_drill=0.4,
                     wire_width=6)

# Net classes shared by the power boards. Patterns are fnmatch on the net name.
# Power: 2.5 mm tracks; 2.0 mm clearance enforced by the <project>.kicad_dru rule that pcb_from_sch.py writes,
# except against pads of fine-pitch footprints (DIP, LED, 1/4 W, SIP modules), where the netclass value (0.6 mm,
# IPC-2221 B4 for 300 V under solder mask) applies and the router reaches the pad with a 0.8 mm neck.
# HV_signal: 0.5 / 0.6 mm for high-voltage nets that only feed small parts.
POWER_CLASSES = [
    dict(NETCLASS_BASE, name="Default"),
    dict(NETCLASS_BASE, name="Power", clearance=0.6, track_width=2.5, via_diameter=1.6, via_drill=0.8),
    dict(NETCLASS_BASE, name="HV_signal", clearance=0.6, track_width=0.5, via_diameter=0.8, via_drill=0.4),
    dict(NETCLASS_BASE, name="Aux", clearance=0.3, track_width=0.5, via_diameter=0.8, via_drill=0.4),
]

RULES = dict(min_clearance=0.2, min_connection=0.0, min_copper_edge_clearance=0.5, min_hole_clearance=0.25,
             min_hole_to_hole=0.25, min_microvia_diameter=0.2, min_microvia_drill=0.1, min_resolved_spokes=2,
             min_silk_clearance=0.0, min_text_height=0.8, min_text_thickness=0.08, min_through_hole_diameter=0.3,
             min_track_width=0.2, min_via_annular_width=0.1, min_via_diameter=0.5,
             solder_mask_to_copper_clearance=0.0, use_height_for_length_calcs=True)


def pro_template(path):
    """Writes a minimal .kicad_pro template with the shared design rules; returns its path.
    The ERC pin matrix allows output-output (the two paralleled VO pins of the HCPL-3120) and
    power_out-power_out (HCPL-3120 VEE, typed power output in the library, tied to the isolated -Vout)."""
    import json
    pro = {"board": {"design_settings": {"defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2,
                                                       "silk_line_width": 0.15, "silk_text_size_h": 1.0,
                                                       "silk_text_size_v": 1.0, "silk_text_thickness": 0.15},
                                          "rules": RULES},
                     "layer_presets": [], "viewports": []},
           "meta": {"filename": "", "version": 3},
           "net_settings": {"classes": [dict(NETCLASS_BASE, name="Default")], "meta": {"version": 5},
                            "netclass_patterns": []},
           "erc": {"erc_exclusions": [], "meta": {"version": 0},
                   "pin_map": [[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2], [0, 0, 0, 1, 0, 0, 1, 0, 2, 2, 2, 2],
                               [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 2], [0, 1, 0, 0, 0, 0, 1, 1, 2, 1, 1, 2],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                               [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 2], [0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 2],
                               [0, 2, 1, 2, 0, 0, 1, 0, 0, 2, 2, 2], [0, 2, 0, 1, 0, 0, 1, 1, 2, 0, 0, 2],
                               [0, 2, 1, 1, 0, 0, 1, 0, 2, 0, 0, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]],
                   "rule_severities": {}},
           "pcbnew": {"page_layout_descr_file": ""},
           "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
           "sheets": [], "text_variables": {}}
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(pro, f, indent=2)
    return path


# ------------------------------------------------------------------ schematic cells
def driver_cell(sh, n, x, y, pwm, gate, emitter, supply=True, title=None, vcc=None):
    """HCPL-3120 gate driver cell n at (x, y) [mm]. Nets: pwm (bus), gate (switch gate), emitter (switch
    emitter/source). With supply=True adds its own TMA-1215S (+12V/GND -> VCC<n>/emitter); otherwise the
    caller provides the supply net `vcc` (default VCC<n>), e.g. the shared low-side supply."""
    V, E, VO, LA = vcc or f"VCC{n}", emitter, f"VO{n}", f"LEDA{n}"
    sh.rect(x - 4, y - 6, x + 72, y + 30, title or f"Gate driver {n}: {pwm} -> {gate}")
    sh.two("Device:R", f"R{n}1", "270", x + 4, y + 8, pwm, LA, fp=FP["R"])
    sh.part("Driver_FET:HCPL-3120", f"U{n}", "HCPL-3120", x + 22, y + 10,
            {"1": "NC", "2": LA, "3": "GND", "4": "NC", "5": E, "6": VO, "7": VO, "8": V}, fp=FP["DIP8"])
    sh.two("Device:C", f"C{n}1", "100n", x + 40, y + 2, V, E, fp=FP["C_100n"])
    sh.two("Device:C_Polarized", f"C{n}2", "10u/25V", x + 46, y + 2, V, E, fp=FP["C_10u25"])
    sh.two("Device:R", f"R{n}2", "22", x + 40, y + 16, VO, gate, fp=FP["R"])
    sh.two("Device:R", f"R{n}3", "10k", x + 48, y + 16, gate, E, fp=FP["R"])
    if supply:
        sh.part("Converter_DCDC_Isolated:TMA-1215S", f"PS{n}", "TMA-1215S", x + 60, y + 10,
                {"1": "+12V", "2": "GND", "6": V, "4": E}, fp=FP["TMA"])


def protection_cell(sh, x, y, vcc, ov_net, r_ov_bot, i_trip_label="3 A", ov_label="", with_supply=False, n=9):
    """Shunt (COM -> GND_P), LM393 over-current (unit 1) and over-voltage (unit 2) comparators referenced to
    GND_P and powered from `vcc` (15 V isolated), wired-OR into the PC817 that pulls FAULT (bus) low.
    r_ov_bot sets the over-voltage trip: V_trip = 2.5 V * (940k + r_ov_bot) / r_ov_bot.
    with_supply=True adds a dedicated TMA-1215S (GND -> GND_P) producing `vcc`."""
    sh.rect(x - 4, y - 6, x + 96, y + 54, f"Protection: over-current ({i_trip_label}) and over-voltage {ov_label}")
    sh.two("Device:R", f"R{n}0", "0R1/5W", x + 2, y + 6, "COM", "GND_P", fp=FP["R_5W"])
    # over-current: COM is +R*I above GND_P; filter 1k/10n (1.6 us), reference 0..0.54 V from a trimmer
    sh.two("Device:R", f"R{n}1", "1k", x + 12, y + 6, "COM", "ISENSE", fp=FP["R"])
    sh.two("Device:C", f"C{n}1", "10n", x + 18, y + 6, "ISENSE", "GND_P", fp=FP["C_10n"])
    sh.two("Device:R", f"R{n}2", "27k", x + 26, y + 6, vcc, "IREF_TOP", fp=FP["R"])
    sh.part("Device:R_Potentiometer", f"RV{n}", "1k", x + 32, y + 6, {"1": "IREF_TOP", "2": "IREF", "3": "GND_P"},
            fp=FP["TRIM"])
    sh.part("Comparator:LM393", f"U{n}", "LM393", x + 48, y + 6, {"1": "FLT", "2": "ISENSE", "3": "IREF"},
            fp=FP["DIP8"], unit=1)                      # output low (fault) when ISENSE > IREF
    sh.two("Device:R", f"R{n}3", "1M", x + 60, y + 2, "FLT", "IREF", fp=FP["R"])      # hysteresis
    # over-voltage: 2 x 470k from the sensed bus, bottom resistor sets the trip, 2.5 V reference from vcc
    sh.two("Device:R", f"R{n}4", "470k", x + 2, y + 24, ov_net, "OVMID", fp=FP["R_1W"])
    sh.two("Device:R", f"R{n}5", "470k", x + 10, y + 24, "OVMID", "OVSENSE", fp=FP["R_1W"])
    sh.two("Device:R", f"R{n}6", r_ov_bot, x + 18, y + 24, "OVSENSE", "GND_P", fp=FP["R"])
    sh.two("Device:R", f"R{n}7", "10k", x + 26, y + 24, vcc, "VREF", fp=FP["R"])
    sh.two("Device:R", f"R{n}8", "2k", x + 32, y + 24, "VREF", "GND_P", fp=FP["R"])
    sh.part("Comparator:LM393", f"U{n}", "LM393", x + 48, y + 26, {"5": "VREF", "6": "OVSENSE", "7": "FLT"},
            fp=FP["DIP8"], unit=2)                      # output low (fault) when OVSENSE > VREF
    sh.two("Device:R", f"R{n}9", "1M", x + 60, y + 22, "FLT", "VREF", fp=FP["R"])     # hysteresis
    sh.part("Comparator:LM393", f"U{n}", "LM393", x + 72, y + 6, {"8": vcc, "4": "GND_P"}, fp=FP["DIP8"], unit=3)
    sh.two("Device:C", f"C{n}2", "100n", x + 80, y + 2, vcc, "GND_P", fp=FP["C_100n"])
    # fault output: red LED (local) and PC817 to the bus; both fed from vcc and pulled low by FLT
    sh.two("Device:R", f"R{n}10", "1k5", x + 72, y + 24, vcc, "FLT_LED", fp=FP["R"])
    sh.two("Device:LED", f"D{n}0", "RED", x + 80, y + 24, "FLT", "FLT_LED", fp=FP["LED3"])
    sh.two("Device:R", f"R{n}11", "1k5", x + 72, y + 42, vcc, "FLT_OPTO", fp=FP["R"])
    sh.part("Isolator:PC817", f"U{n+1}", "PC817", x + 86, y + 44, {"1": "FLT_OPTO", "2": "FLT", "3": "GND", "4": "FAULT"},
            fp=FP["DIP4"])
    if with_supply:
        sh.part("Converter_DCDC_Isolated:TMA-1215S", f"PS{n}", "TMA-1215S", x + 86, y + 10,
                {"1": "+12V", "2": "GND", "6": vcc, "4": "GND_P"}, fp=FP["TMA"])


def gate_bus(sh, x, y, used=(1,), ref="J1"):
    """Gate-bus connector (2x8 IDC) plus 12 V decoupling and the green "armed" LED driven by EN.
    `used`: PWM channel numbers wired on this board; the rest are marked no-connect."""
    sh.rect(x - 4, y - 6, x + 52, y + 36, "Gate bus (from gating block)")
    conns = {"1": "+12V", "2": "+12V", "3": "GND", "4": "GND", "11": "FAULT", "12": "EN", "13": "NC",
             "14": "GND", "15": "GND", "16": "GND"}
    for k in range(1, 7):
        conns[str(4 + k)] = f"PWM{k}" if k in used else "NC"
    sh.part("Connector_Generic:Conn_02x08_Odd_Even", ref, "GATE_BUS", x + 10, y + 10, conns, fp=FP["IDC16"])
    sh.two("Device:C_Polarized", "C01", "10u/25V", x + 30, y + 4, "+12V", "GND", fp=FP["C_10u25"])
    sh.two("Device:C", "C02", "100n", x + 36, y + 4, "+12V", "GND", fp=FP["C_100n"])
    sh.two("Device:R", "R01", "1k", x + 30, y + 22, "EN", "EN_LED", fp=FP["R"])
    sh.two("Device:LED", "D01", "GREEN", x + 40, y + 22, "GND", "EN_LED", fp=FP["LED3"])
    sh.part("power:PWR_FLAG", "#FLG01", "PWR_FLAG", x + 46, y + 4, {"1": "+12V"})
    sh.part("power:PWR_FLAG", "#FLG02", "PWR_FLAG", x + 46, y + 14, {"1": "GND"})


def dc_bus_caps(sh, x, y, pos, neg, refs, n_elec=1, film=True, title="DC bus"):
    """n_elec electrolytics 47u/450V and one 4.7u/400V film between `pos` and `neg`. refs: iterator of C refs."""
    sh.rect(x - 4, y - 6, x + 8 + 10 * (n_elec + 1), y + 14, title)
    for k in range(n_elec):
        sh.two("Device:C_Polarized", next(refs), "47u/450V", x + 2 + 10 * k, y + 4, pos, neg, fp=FP["C_47u450"])
    if film:
        sh.two("Device:C", next(refs), "4u7/400V", x + 2 + 10 * n_elec, y + 4, pos, neg, fp=FP["C_4u7_400"])


def bleeder_led(sh, x, y, pos, neg, refs_r, ref_led, title="Bleeder / pilot LED"):
    """Two 100k 0.5 W resistors in series with a red LED across the bus: discharge path and 'bus charged' lamp.
    The LED sits between the resistors so that its 2.54 mm pads never carry a Power-class net (2 mm clearance)."""
    sh.rect(x - 4, y - 6, x + 30, y + 14, title)
    sh.two("Device:R", next(refs_r), "100k/0.5W", x + 2, y + 4, pos, f"{pos}_BL1", fp=FP["R_1W"])
    sh.two("Device:LED", ref_led, "RED", x + 12, y + 4, f"{pos}_BL2", f"{pos}_BL1", fp=FP["LED5"])
    sh.two("Device:R", next(refs_r), "100k/0.5W", x + 20, y + 4, f"{pos}_BL2", neg, fp=FP["R_1W"])


def test_point(sh, ref, net, x, y):
    sh.part("Connector:TestPoint", ref, net, x, y, {"1": net}, fp=FP["TP"], in_bom=False)


def mounting_holes(sh, x, y, n=4):
    for k in range(n):
        sh.part("Mechanical:MountingHole", f"H{k+1}", "M3", x + 8 * k, y, {}, fp=FP["MH"], in_bom=False)


class Refs:
    """Sequential reference generator: Refs('C', 1) -> C1, C2, ..."""
    def __init__(self, prefix, start=1):
        self.p, self.k = prefix, start - 1

    def __next__(self):
        self.k += 1
        return f"{self.p}{self.k}"

    def __iter__(self):
        return self


# ------------------------------------------------------------------ ESP32 DevKitC V4 (custom symbol + footprint)
DEVKIT_LEFT = ["3V3", "EN", "VP/IO36", "VN/IO39", "IO34", "IO35", "IO32", "IO33", "IO25", "IO26", "IO27", "IO14",
               "IO12", "GND", "IO13", "SD2/IO9", "SD3/IO10", "CMD/IO11", "5V"]
DEVKIT_RIGHT = ["GND", "IO23", "IO22", "TX0/IO1", "RX0/IO3", "IO21", "GND", "IO19", "IO18", "IO5", "IO17", "IO16",
                "IO4", "IO0", "IO2", "IO15", "SD1/IO8", "SD0/IO7", "CLK/IO6"]
DEVKIT_PIN = {name: str(i + 1) for i, name in enumerate(DEVKIT_LEFT)}
DEVKIT_PIN.update({name: str(i + 20) for i, name in enumerate(DEVKIT_RIGHT)})
DEVKIT_PIN["GND"] = "14"            # the other GND pins (20, 26) are stacked on the same net in the generator


def devkit_symbol_lib():
    """kicad_sym text with the ESP32-DevKitC V4 (38 pins, two columns, pin 1 top-left)."""
    def ptype(name):
        if name in ("3V3",):
            return "power_out"
        if name in ("5V",):
            return "power_in"
        if name == "GND":
            return "power_in"
        if name == "EN" or name.startswith("VP") or name.startswith("VN") or name in ("IO34", "IO35"):
            return "input"
        return "bidirectional"
    pins = []
    for i, name in enumerate(DEVKIT_LEFT):
        y = 22.86 - 2.54 * i
        pins.append(f'''      (pin {ptype(name)} line (at -20.32 {y:.2f} 0) (length 5.08)
        (name "{name}" (effects (font (size 1.27 1.27)))) (number "{i+1}" (effects (font (size 1.27 1.27)))))''')
    for i, name in enumerate(DEVKIT_RIGHT):
        y = 22.86 - 2.54 * i
        pins.append(f'''      (pin {ptype(name)} line (at 20.32 {y:.2f} 180) (length 5.08)
        (name "{name}" (effects (font (size 1.27 1.27)))) (number "{i+20}" (effects (font (size 1.27 1.27)))))''')
    return f'''(kicad_symbol_lib (version 20241209) (generator "pe_blocks") (generator_version "10.0")
  (symbol "ESP32-DevKitC-V4" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
    (property "Reference" "A" (at -15.24 26.67 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Value" "ESP32-DevKitC-V4" (at -15.24 -26.67 0) (effects (font (size 1.27 1.27)) (justify left)))
    (property "Footprint" "pe_lib:ESP32-DevKitC-V4_Socket" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Description" "ESP32-DevKitC V4 development board, 38 pins, on 2.54 mm sockets" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "ESP32-DevKitC-V4_0_1"
      (rectangle (start -15.24 25.4) (end 15.24 -25.4) (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "ESP32-DevKitC-V4_1_1"
{chr(10).join(pins)}
    )
  )
)
'''


def devkit_footprint():
    """Footprint: two 19-pin socket rows at 25.4 mm (official DevKitC) plus two rows at 22.86 mm (clones),
    pads of the same pin number paired. Origin at the board centre, pin 1 top-left, USB edge at the bottom."""
    pads = []
    for col, x in (("L", -12.7), ("Lc", -11.43), ("Rc", 11.43), ("R", 12.7)):
        for i in range(19):
            num = i + 1 if col.startswith("L") else i + 20
            y = -22.86 + 2.54 * i
            shape = "rect" if num == 1 and col == "L" else "oval"
            pads.append(f'  (pad "{num}" thru_hole {shape} (at {x} {y:.2f}) (size 1.6 1.6) (drill 1.0) '
                        f'(layers "*.Cu" "*.Mask") (remove_unused_layers no))')
    return f'''(footprint "ESP32-DevKitC-V4_Socket" (version 20241229) (generator "pe_blocks") (generator_version "10.0")
  (layer "F.Cu")
  (descr "ESP32-DevKitC V4 on 2.54 mm socket strips; rows at 25.4 mm (official) and 22.86 mm (clones), USB at the bottom edge")
  (tags "ESP32 DevKitC socket")
  (property "Reference" "REF**" (at 0 -26.5 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
  (property "Value" "ESP32-DevKitC-V4" (at 0 26.5 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
  (attr through_hole)
  (fp_rect (start -14 -27.5) (end 14 27.5) (stroke (width 0.12) (type default)) (fill no) (layer "F.SilkS"))
  (fp_rect (start -14.5 -28) (end 14.5 28) (stroke (width 0.05) (type default)) (fill no) (layer "F.CrtYd"))
  (fp_rect (start -14 -27.5) (end 14 27.5) (stroke (width 0.1) (type default)) (fill no) (layer "F.Fab"))
  (fp_rect (start -4 24) (end 4 27.5) (stroke (width 0.12) (type default)) (fill no) (layer "F.SilkS"))
  (fp_text user "USB" (at 0 22.5 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
  (fp_text user "1" (at -14.8 -22.86 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (fp_text user "${{REFERENCE}}" (at 0 0 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
{chr(10).join(pads)}
)
'''


def write_custom_libs(out_dir):
    """Writes pe_lib.kicad_sym (via the Design) is done by the caller; this writes the footprint lib and table."""
    pretty = os.path.join(out_dir, "pe_lib.pretty")
    os.makedirs(pretty, exist_ok=True)
    with open(os.path.join(pretty, "ESP32-DevKitC-V4_Socket.kicad_mod"), "w", encoding="utf-8", newline="\n") as f:
        f.write(devkit_footprint())
    with open(os.path.join(out_dir, "fp-lib-table"), "w", encoding="utf-8", newline="\n") as f:
        f.write('(fp_lib_table\n\t(version 7)\n\t(lib (name "pe_lib")(type "KiCad")(uri "${KIPRJMOD}/pe_lib.pretty")'
                '(options "")(descr "Project footprints"))\n)\n')
