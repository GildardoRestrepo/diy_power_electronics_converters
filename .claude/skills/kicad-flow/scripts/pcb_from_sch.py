"""Crea (o actualiza) la .kicad_pcb a partir del esquemático, sin abrir KiCad (sustituye el F8 manual).

Uso (con el Python de KiCad, con el proyecto cerrado en KiCad):
    "/c/Program Files/KiCad/10.0/bin/python.exe" -I pcb_from_sch.py <proyecto.kicad_pro> [--layers 2|4]

Pasos: exporta el netlist con kicad-cli (`sch export netlist --format kicadsexpr`), carga cada huella
desde las bibliotecas estándar (o desde `<proyecto>/<lib>.pretty` si existe `fp-lib-table` en la carpeta),
le pone referencia, valor, campos, ruta jerárquica (sheetpath + tstamp, lo que compara la paridad del
DRC) y la red de cada pad (también las `unconnected-*` de los pines con marca de no conexión, que la
paridad de KiCad 10 exige). Si la PCB ya existe, conserva posición/rotación de las huellas con la misma
ruta y las pistas/zonas existentes; las huellas que ya no están en el esquemático se eliminan.
"""
import json, os, re, subprocess, sys

import pcbnew
from pcbnew import VECTOR2I, FromMM as M

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kicad_sexpr import parse, find, first  # noqa: E402

CLI = os.environ.get("KICAD_CLI", "C:/Program Files/KiCad/10.0/bin/kicad-cli.exe")
FPDIR = os.environ.get("KICAD_FOOTPRINT_DIR", "C:/Program Files/KiCad/10.0/share/kicad/footprints")


def val(node, key, default=""):
    n = first(node, key)
    if n is None:
        return default
    return n[1] if len(n) > 1 else default


def prop(node, key, name):
    for p in find(node, key):
        if val(p, "name") == name:
            return val(p, "value")
    return None


def pj_rules(pro, text=None):
    """Clases con separación > 1 mm del .kicad_pro: para ellas se escribe la regla de 'huellas finas'."""
    pj = json.loads(text) if text is not None else json.load(open(pro, encoding="utf-8"))
    return [(c["name"], c["clearance"]) for c in pj.get("net_settings", {}).get("classes", [])
            if c.get("clearance", 0) > 1.0 or c["name"] == "Power"]


def write_dru(base, b, classes, pitch=4.0, power_clr=2.0):
    """<proyecto>.kicad_dru: las redes de potencia guardan `power_clr` con todo, salvo con los pads de las
    huellas de paso fino (DIP, LED, resistencias 1/4 W, módulos SIP), donde rige la clase (0.6 mm). Así una red
    de potencia puede llegar a un pin de un DIP sin violar el DRC entre pines vecinos."""
    import math
    small = []
    for fp in b.GetFootprints():
        pts = [(pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)) for p in fp.Pads()]
        if any(math.hypot(a[0] - c[0], a[1] - c[1]) < pitch for i, a in enumerate(pts) for c in pts[i + 1:]):
            small.append(fp.GetReference())
    names = [n for n, _ in classes] or ["Power"]
    is_pwr = " || ".join(f"A.NetClass == '{n}' || B.NetClass == '{n}'" for n in names)
    in_small = " || ".join(f"A.memberOfFootprint('{r}') || B.memberOfFootprint('{r}')" for r in small) or "0"
    text = (f"(version 1)\n"
            f"(rule \"power_clearance\"\n"
            f"  (condition \"({is_pwr}) && !({in_small})\")\n"
            f"  (constraint clearance (min {power_clr}mm)))\n")
    with open(base + ".kicad_dru", "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"regla DRC de potencia escrita ({len(small)} huellas de paso fino exentas)")


def main():
    pro = sys.argv[1]
    layers = int(sys.argv[sys.argv.index("--layers") + 1]) if "--layers" in sys.argv else 2
    proj_dir = os.path.dirname(os.path.abspath(pro))
    base = os.path.splitext(os.path.abspath(pro))[0]
    sch, pcb, net = base + ".kicad_sch", base + ".kicad_pcb", base + ".net"
    subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", net, sch], check=True,
                   stdout=subprocess.DEVNULL)
    tree = parse(open(net, encoding="utf-8").read())

    # bibliotecas propias del proyecto (fp-lib-table con uri ${KIPRJMOD}/x.pretty)
    local_libs = {}
    flt = os.path.join(proj_dir, "fp-lib-table")
    if os.path.exists(flt):
        for row in find(parse(open(flt, encoding="utf-8").read()), "lib"):
            local_libs[val(row, "name")] = val(row, "uri").replace("${KIPRJMOD}", proj_dir)

    # Guardar el .kicad_pro tal como lo escribió el generador del esquemático: al guardar una placa NUEVA,
    # pcbnew reescribe el proyecto con valores por defecto y borra la matriz ERC y las clases de red.
    pro_text = open(pro, encoding="utf-8").read()
    if os.path.exists(pcb):
        b = pcbnew.LoadBoard(pcb)
    else:
        b = pcbnew.CreateEmptyBoard()
        b.SetCopperLayerCount(layers)
    old = {fp.GetPath().AsString(): fp for fp in b.GetFootprints()}

    # redes (incluidas las `unconnected-*` de pines marcados como no conectados: la paridad del DRC las exige)
    nets = {}
    for n in find(first(tree, "nets"), "net"):
        name = val(n, "name")
        for node in find(n, "node"):
            nets[(val(node, "ref"), val(node, "pin"))] = name
    for name in sorted(set(nets.values())):
        if b.FindNet(name) is None:
            b.Add(pcbnew.NETINFO_ITEM(b, name))

    kept, loaded, missing_fp = set(), 0, []
    for comp in find(first(tree, "components"), "comp"):
        ref, value, fpid = val(comp, "ref"), val(comp, "value"), val(comp, "footprint")
        if ref.startswith("#"):
            continue
        sp = val(first(comp, "sheetpath"), "tstamps") if first(comp, "sheetpath") else "/"
        path = (sp if sp.endswith("/") else sp + "/") + val(comp, "tstamps")
        if not fpid or ":" not in fpid:
            missing_fp.append(ref); continue
        lib, name = fpid.split(":", 1)
        libpath = local_libs.get(lib, f"{FPDIR}/{lib}.pretty")
        fp = old.get(path)
        if fp is not None and fp.GetFPIDAsString() == fpid:
            pass                                                   # ya está: solo actualizar campos y redes
        else:
            new = pcbnew.FootprintLoad(libpath, name)
            if new is None:
                missing_fp.append(f"{ref} ({fpid})"); continue
            if fp is not None:                                     # cambió la huella: conservar posición
                new.SetPosition(fp.GetPosition()); new.SetOrientation(fp.GetOrientation())
                if fp.IsFlipped():
                    new.Flip(new.GetPosition(), False)
                b.Remove(fp)
            else:
                new.SetPosition(VECTOR2I(M(50 + 10 * (loaded % 10)), M(50 + 10 * (loaded // 10))))
            new.SetFPIDAsString(fpid)
            fp = new; b.Add(fp); loaded += 1
            new.thisown = False                                # la placa es ahora la dueña (evita avisos de SWIG)
        kept.add(path)
        fp.SetReference(ref); fp.SetValue(value)
        fp.SetPath(pcbnew.KIID_PATH(path))
        # campos del símbolo (Datasheet, Description y campos de usuario)
        for f in find(first(comp, "fields") or [], "field"):
            fname = val(f, "name")
            fval = f[2] if len(f) > 2 else ""
            if fname in ("Reference", "Value", "Footprint"):
                continue
            fld = fp.GetField(fname) if fp.HasField(fname) else None
            if fld is None:
                fld = pcbnew.PCB_FIELD(fp, fp.GetNextFieldOrdinal(), fname)
                fld.SetVisible(False); fld.SetLayer(pcbnew.F_Fab)
                fp.AddField(fld)
            fld.SetText(fval)
        # atributos del símbolo: fuera de BOM / de archivos de posición / DNP
        props = {val(pr, "name") for pr in find(comp, "property")}
        attrs = fp.GetAttributes() & ~(pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_DNP)
        for key, flag in (("exclude_from_bom", pcbnew.FP_EXCLUDE_FROM_BOM),
                          ("exclude_from_pos_files", pcbnew.FP_EXCLUDE_FROM_POS_FILES), ("dnp", pcbnew.FP_DNP)):
            if key in props:
                attrs |= flag
        fp.SetAttributes(attrs)
        # redes de pads
        for p in fp.Pads():
            name = nets.get((ref, p.GetNumber()))
            p.SetNetCode(b.FindNet(name).GetNetCode() if name else 0)

    for path, fp in old.items():
        if path not in kept:
            b.Remove(fp)
    b.Save(pcb)
    write_dru(base, b, pj_rules(pro, pro_text))
    # restaurar el .kicad_pro original (ERC, clases de red, reglas) y registrar la placa
    pj = json.loads(pro_text)
    pj["boards"] = pj.get("boards") or []
    json.dump(pj, open(pro, "w", encoding="utf-8", newline="\n"), indent=2, ensure_ascii=False)
    os.remove(net)
    print(f"PCB: {len(kept)} huellas ({loaded} cargadas), {len(set(nets.values()))} redes, "
          f"eliminadas: {len(old) - len(set(old) & kept)}")
    if missing_fp:
        print("SIN HUELLA:", ", ".join(missing_fp))
        sys.exit(1)


if __name__ == "__main__":
    main()
