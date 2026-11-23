---
name: kicad-flow
description: Flujo para generar, revisar y documentar placas KiCad 10 por script en este repo (convertidores de potencia UPB): esquemático desde Python, PCB desde el netlist sin abrir KiCad, colocación por JSON con informe de solapes, ruteo por clases de red (potencia / señal HV / lógica), serigrafía, ERC/DRC y renders. Úsala cuando el usuario quiera crear o modificar un esquemático o PCB, cambiar la colocación o las clases de red, correr ERC/DRC, exportar renders/Gerbers/BOM o entender por qué falla el ruteo.
---

# Flujo KiCad (placas de potencia generadas por código)

## Entorno
- KiCad 10.0.5 en Windows. CLI: `/c/Program Files/KiCad/10.0/bin/kicad-cli.exe`. Python con `pcbnew`: `/c/Program Files/KiCad/10.0/bin/python.exe` (siempre con `-I`). Bibliotecas estándar en `/c/Program Files/KiCad/10.0/share/kicad/{symbols,footprints,3dmodels}`.
- Cada caja tiene `0N_<caja>/30_pcb/<proyecto>/` (archivos KiCad, versionados) y `0N_<caja>/30_pcb/scripts/` (`gen_<caja>.py` + `pcb_config.json`, la fuente de verdad). `out/` (reportes, renders, SVG) está en `.gitignore`; los renders finales se copian a `0N_<caja>/00_assets/`.
- Celdas compartidas (driver HCPL-3120 + TMA, protección LM393/PC817, bus de disparo IDC-16, buses DC, bleeder, huella/símbolo del ESP32 DevKitC) en `90_tools/kicad_blocks/pe_blocks.py`.

## Regla de oro
Las placas se **regeneran** desde los scripts: una edición manual en KiCad se pierde en la siguiente generación. Antes de tocar un `.kicad_*` por script, el proyecto debe estar cerrado en KiCad (si hay `*.lck`, sigue abierto). Si el usuario quiere editar a mano, se deja de generar ese proyecto y se anota en su README.

## Ciclo completo (un comando)
```bash
cd 0N_<caja>/30_pcb/scripts && python gen_<caja>.py          # esquemático + PCB + ruteo + serigrafía + ERC/DRC
python gen_<caja>.py --sch                                      # solo esquemático (rápido, para iterar con ERC)
python .claude/skills/kicad-flow/scripts/pcb_pipeline.py <proyecto.kicad_pro> <pcb_config.json> --from place|route|silk|check [--fab] [--keep-tracks]
```
`pcb_pipeline.py` encadena `pcb_from_sch.py` (netlist → PCB, sustituye el F8 manual) → `pcb_place.py` → `pcb_route.py --clean` → `pcb_silk.py` → `kicad_check.sh`. Devuelve ≠ 0 si el ruteo deja redes sin conectar o el DRC tiene violaciones.

### Orden de trabajo recomendado
1. **Esquemático** (`--sch`) y ERC con `kicad-cli sch erc --severity-all`. Para mirarlo: `kicad-cli sch export pdf` y leer el PDF (o recortar con `pymupdf` a 6x).
2. **Colocación**: `"$PY" -I pcb_place.py <pcb> <config> --report` imprime el courtyard de cada huella (relativo al origen de la placa), los **solapes** y las huellas fuera del contorno. Iterar aquí (segundos) hasta `SOLAPES: ninguno`; el ruteo tarda 10–20 min por placa y en segundo plano.
3. **Ruteo** (`--from route`), después **serigrafía** y **DRC**. Mirar `out/render_top.png` con la herramienta Read.
4. **Evidencias**: copiar `render_top.png`, `render_iso.png` y el PDF del esquemático a `00_assets/`.

## Esquemático por código (`kicad_sch_gen.py`)
- `Design(project, power_nets=(...))`, `d.root("A3")`, `sh.part(lib_id, ref, valor, x, y, {pin: red}, fp=..., unit=n)`, `sh.two(...)` para pasivos, `sh.rect(...)` para bloques con título. Cada pin recibe un tramo de 2.54 mm + etiqueta local / símbolo de alimentación / `"NC"`.
- **Símbolos multi-unidad** (LM393, 74xx): una llamada por unidad con `unit=1,2,3` y la misma referencia.
- **Separación**: un pasivo vertical ocupa ±(3.81 + 2.54) mm más la etiqueta: dejar ≥ 15 mm en vertical y ≥ 12 mm en horizontal entre componentes; si un extremo de tramo cae sobre un pin ajeno, las redes se funden sin aviso (ERC `multiple_net_names`). Correr ERC siempre.
- Redes: las etiquetas de la hoja raíz se llaman `/NOMBRE` en la PCB; los símbolos de alimentación, `NOMBRE`. Los patrones de clase deben llevar la barra.
- Matriz ERC del proyecto (`pe.pro_template`): salida–salida y power_out–power_out rebajados a advertencia por los dos pines VO y el VEE del HCPL-3120.
- Bibliotecas propias: `d.add_lib("pe_lib", texto_kicad_sym)` + `pe.write_custom_libs(out)` escribe `pe_lib.pretty` y `fp-lib-table`; `pcb_from_sch.py` resuelve `${KIPRJMOD}`.

## PCB
- **`pcb_from_sch.py <pro>`**: exporta el netlist, carga cada huella de la biblioteca, asigna referencia/valor/campos/ruta jerárquica (paridad del DRC), redes de pads (incluidas las `unconnected-*` de los pines NC) y atributos (fuera de BOM / pos, DNP). Conserva posiciones y pistas si la PCB ya existe. Al crear una PCB **nueva**, pcbnew reescribe el `.kicad_pro` con valores por defecto (sin matriz ERC ni clases de red): el script guarda el proyecto antes y lo restaura después. `pcb_place.py` ya no toca las redes `unconnected-*`.
- **`pcb_config.json`**: `board` (origen, tamaño), `place` (`ref: [x, y, rot, ancla]`; el ancla `c` es el origen de la huella = pin 1 en casi todas las THT), `planes`, `keepouts`, `route`, `silk`. Rotación 90 lleva +x a −y (arriba): una resistencia vertical que debe bajar desde su pin 1 lleva rot 270.
- **Clases de red en el ruteo** (`route.classes`, misma definición que `net_settings` del `.kicad_pro` vía `pe.POWER_CLASSES`): `Power` 2.5 mm de pista para las redes de alta tensión que llevan corriente (bus de entrada, nodo de conmutación, salida); los 2.0 mm de separación los impone la regla `power_clearance` del `.kicad_dru` (que escribe `pcb_from_sch.py`), con excepción de los pads de huellas de paso fino (DIP, LED, SIP, radiales de 2.5 mm), a los que el router llega con un cuello de 0.8 mm y 0.6 mm de separación. `Return` 1.5 mm / 0.6 mm para los retornos a 0 V (`COM`, `GND_P`): llevan corriente pero conviven con la lógica de protección. `HV_signal` 0.5 / 0.6 mm para redes de alta tensión que solo alimentan piezas pequeñas (driver flotante, bleeder, divisor). `Aux`/`Default` para lógica.
- **Dominios de tensión** (`route.domains`): grupos de redes que están a pocos voltios entre sí, p. ej. `["/VIN+", "/VF", "/VIN"]` (fusible y NTC en serie) o `["/SW", "/G1", "/VO1", "/VCC1"]` (nodo de conmutación y alimentación flotante de su driver). El router hace una pasada por dominio y dentro de él separa solo 0.6 mm; `pcb_from_sch.py <pro> <config.json>` escribe la misma excepción en la regla del `.kicad_dru`. Sin dominios, un driver flotante nunca cabe junto a su propio nodo de conmutación.
- **Reglas extra del `.kicad_dru`**: la serigrafía de los conectores IDC del bus puede salir del borde (el cierre va hacia fuera a propósito). El router respeta la separación agujero-agujero también entre vías y pads de la misma red.
- **Prioridad de ruteo** (`route.priority`): redes que se rutean primero dentro de su pasada, p. ej. `/FLT`, que une las dos salidas del LM393 en esquinas opuestas del DIP y se queda sin camino si va al final.
- El router hace una pasada por clase (de la más ancha a la más fina) y respeta la separación de la red del obstáculo. Fallos típicos: `(pad bloqueado)` = pad solapado con otro o rodeado; sin camino = abrir espacio o mover el componente hacia su red. `--clean` (por defecto desde el pipeline) borra el ruteo anterior; `--keep-tracks` respeta pistas manuales. El ruteo trabaja sobre una copia en una carpeta temporal y solo reemplaza la PCB al terminar: interrumpirlo deja la placa como estaba.
- Planos: `planes` rellena zonas (p. ej. GND en B.Cu en placas lógicas). Aun así conviene rutear GND como red normal (no ponerla en `plane_nets`) para que no queden islas.
- Aislamiento: en las placas con bus de disparo, el lado lógico ocupa una franja (x < 10–14 mm o el borde inferior) y la barrera pasa entre las columnas de los DIP (HCPL-3120, PC817) y entre los pines de entrada y salida de los TMA; nada de cobre de potencia a menos de 6 mm del lado lógico.

## Verificación y exportación
```bash
bash .claude/skills/kicad-flow/scripts/kicad_check.sh [--fab] <carpeta_proyecto> [salida]
```
ERC + DRC con paridad y zonas rellenadas, esquemático SVG/PDF, `render_top/bottom/iso.png`, `layout.svg`, un SVG por capa; con `--fab`, Gerbers y taladros. BOM: `kicad-cli sch export bom -o bom.csv <sch>`.

## Trampas conocidas
- **No usar referencias con cero a la izquierda** (`C01`, `R01`): KiCad compara la parte numérica, trata `C01` y `C1` como la misma referencia y las fusiona en un componente de dos unidades; una de las dos huellas desaparece de la PCB sin ningún error. Las celdas de `pe_blocks.py` usan la serie 80 para el bus de disparo.
- `pcb_from_sch.py` reconoce las huellas existentes por ruta y, si no coincide, por referencia (el generador crea uuids nuevos en cada corrida): así conserva posiciones y pistas en lugar de borrar y recargar toda la placa.
- Si un proyecto pierde sus clases de red o su matriz ERC (ERC con `pin_to_pin` en el HCPL-3120, DRC sin la clase `Power`), regenerarlo completo con `gen_<caja>.py`: el esquemático reescribe el `.kicad_pro` y `pcb_from_sch.py` ya lo conserva.
- `pcbnew` + SWIG: tras `b.Remove()` el siguiente `LoadBoard` del mismo proceso devuelve objetos sin tipo → los pasos destructivos van en un subproceso. Tras `b.Add(fp)` poner `fp.thisown = False` para evitar avisos de fuga.
- `GetStart()/GetEnd()` devuelven referencias; copiar con `VECTOR2I(...)` antes de modificar.
- La herramienta Bash corta comandos de más de ~120 líneas (heredoc con "unexpected EOF"): escribir archivos largos con Write y ejecutarlos.
- `kicad-cli sch export` no genera PNG; usar PDF/SVG. Los SVG no se pueden ver con Read: usar el PDF.
- El bloque de bornes MKDS horizontal tiene la entrada de cable hacia −y; con rot 90 queda hacia la izquierda y con 270 hacia la derecha (bordes izquierdo/derecho de la placa).
- Referencias de serigrafía: `pcb_silk.py` las coloca por cercanía; las que no caben quedan en F.Fab y se listan: usar `silk.manual`.
