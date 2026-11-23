"""Encadena los pasos de PCB de un proyecto generado por script, sin abrir KiCad.

Uso (con el Python del sistema o el de KiCad; lanza el de KiCad para los pasos de pcbnew):
    python pcb_pipeline.py <proyecto.kicad_pro> <pcb_config.json> [--from place|route|silk|check] [--fab] [--keep-tracks]

Por defecto el ruteo parte de cero (`pcb_route.py --clean`); con --keep-tracks respeta las pistas existentes.

Pasos: pcb_from_sch (netlist -> PCB) -> pcb_place -> pcb_route -> pcb_silk -> kicad_check.sh
Con --from se retoma desde un paso (p. ej. tras cambiar solo la colocación). Devuelve el código del
último paso que falló (ruteo con fallos o DRC con violaciones) para que el generador lo informe.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = os.environ.get("KICAD_PYTHON", "C:/Program Files/KiCad/10.0/bin/python.exe")
STEPS = ["from_sch", "place", "route", "silk", "check"]


def run(cmd):
    print("+", " ".join(os.path.basename(c) if c.endswith(".py") else c for c in cmd), flush=True)
    return subprocess.run(cmd).returncode


def main():
    pro, cfg = sys.argv[1], sys.argv[2]
    start = sys.argv[sys.argv.index("--from") + 1] if "--from" in sys.argv else "from_sch"
    fab = ["--fab"] if "--fab" in sys.argv else []
    proj_dir = os.path.dirname(os.path.abspath(pro))
    pcb = os.path.splitext(os.path.abspath(pro))[0] + ".kicad_pcb"
    rc, todo = 0, STEPS[STEPS.index(start):]
    if "from_sch" in todo:
        rc = run([PY, "-I", os.path.join(HERE, "pcb_from_sch.py"), pro, cfg])
        if rc:
            sys.exit(rc)
    for step, script in (("place", "pcb_place.py"), ("route", "pcb_route.py"), ("silk", "pcb_silk.py")):
        if step in todo:
            extra = ["--clean"] if step == "route" and "--keep-tracks" not in sys.argv else []
            r = run([PY, "-I", os.path.join(HERE, script), pcb, cfg] + extra)
            rc = rc or (r if step == "route" else 0)
            if r and step != "route":
                sys.exit(r)
    if "check" in todo:
        r = run(["bash", os.path.join(HERE, "kicad_check.sh")] + fab + [proj_dir, os.path.join(proj_dir, "out")])
        rc = rc or r
    sys.exit(rc)


if __name__ == "__main__":
    main()
