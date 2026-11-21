"""Copies the KiCad evidences of every box (3D renders, layout, schematic PDF) from 30_pcb/<project>/out
to 0N_<box>/00_assets/ with stable names, so the repository keeps the images without the reports.

    python 90_tools/collect_assets.py
"""
import glob, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = {"render_top.png": "pcb_top.png", "render_bottom.png": "pcb_bottom.png", "render_iso.png": "pcb_3d.png",
         "layout.svg": "pcb_layout.svg"}

for out in sorted(glob.glob(os.path.join(ROOT, "0*_*", "30_pcb", "*", "out"))):
    proj_dir = os.path.dirname(out)
    box = os.path.dirname(os.path.dirname(proj_dir))
    name = os.path.basename(proj_dir)
    assets = os.path.join(box, "00_assets")
    os.makedirs(assets, exist_ok=True)
    copied = []
    for src, dst in FILES.items():
        s = os.path.join(out, src)
        if os.path.exists(s):
            shutil.copyfile(s, os.path.join(assets, f"{name}_{dst}"))
            copied.append(dst)
    pdf = os.path.join(out, f"{name}.pdf")
    if os.path.exists(pdf):
        shutil.copyfile(pdf, os.path.join(assets, f"{name}_schematic.pdf"))
        copied.append("schematic.pdf")
    print(f"{os.path.basename(box)}: {', '.join(copied) or 'nothing to copy'}")
