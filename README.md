# Portable Power Electronics Converters

Portable, enclosed power converters for teaching, sized to the supplies and loads of the Electric Machines Laboratory at Universidad Pontificia Bolivariana (UPB). Every unit follows the same path: calculation, simulation, PCB, build and lab validation. Each design can be reviewed and reproduced end to end.

> [!WARNING]
> These converters operate at up to 300 V DC and at mains-level AC. Build and test them only under lab supervision, with proper isolation and protection.

---

## Converters

| Family |             Converter             |     |
| :----: | :-------------------------------: | :-: |
| AC/DC  |  Three-phase full-wave rectifier  |     |
| DC/DC  |          Buck Converter           |     |
| DC/DC  |          Boost Converter          |     |
| DC/AC  | Three-phase full-wave (One level) |     |

### Rectifier
|              Parameter              |               Value               |                         Note                         |     |
| :---------------------------------: | :-------------------------------: | :--------------------------------------------------: | --- |
| Line voltage at the bridge (𝑉𝐿𝐿) |             208 Vrms              | Lab mains or transformer secondary of the same ratio |     |
|         Line frequency (𝑓)         |               60 Hz               |                       Colombia                       |     |
|       Rated DC current (𝐼𝑑)       |                5 A                |        Continuous, lamp bank or reactor load         |     |
|         Maximum DC current          |                8 A                |     10 min, heatsink-limited (see losses report)     |     |
|                Load                 | Resistive (lamps) or RL (reactor) |     𝐿𝑙𝑜𝑎𝑑 large enough for continuous 𝑖𝑑      |     |
|            Pulse number             |                 6                 |       Single box; 12 or 24 with several boxes        |     |

### Buck
|           Parameter            |                     Value                     |                    Note                    |
| :----------------------------: | :-------------------------------------------: | :----------------------------------------: |
|     Input voltage (𝑉𝑖𝑛)     |           280 V nominal, 150–320 V            | Rectifier output at 208 VLL; "300 V" class |
|     Output voltage (𝑉𝑜)      |                     110 V                     |              110 V lamp bank               |
|   Rated output power (𝑃𝑜)    |                     200 W                     |        Two 100 W lamps in parallel         |
|     Output current (𝐼𝑜)      |                    1.82 A                     |           𝑅 =𝑉2𝑜/𝑃𝑜 =60.5 Ω           |
|  Switching frequency (𝑓𝑠𝑤)  |        20 kHz nominal, 5–50 kHz usable        |   IGBT up to 20 kHz, MOSFET up to 50 kHz   |
| Inductor current ripple target |           ≤40 % of 𝐼𝑜 at nominal            |     Shared inductor with the boost box     |
|  Output voltage ripple target  |                     ≤1 %                      |                                            |
|            Control             | Open loop, duty cycle set on the gating block |        No feedback in this version         |

### Boost

|Parameter|Value|Note|
|:-:|:-:|:-:|
|Input voltage (𝑉𝑖𝑛)|110 V nominal, 60–120 V|Lab DC supply (110 V max.)|
|Output voltage (𝑉𝑜)|300 V|Feeds the buck or the inverter box, or a series lamp bank|
|Rated output power (𝑃𝑜)|200 W||
|Output current (𝐼𝑜)|0.667 A|𝑅 =𝑉2𝑜/𝑃𝑜 =450 Ω|
|Switching frequency (𝑓𝑠𝑤)|20 kHz nominal, 5–50 kHz usable|IGBT up to 20 kHz, MOSFET up to 50 kHz|
|Inductor current ripple target|≤40 % of 𝐼𝐿 at nominal|Same 4.7 mH inductor as the buck box|
|Output voltage ripple target|≤1 %||
|Control|Open loop, duty cycle set on the gating block|Over-voltage trip mandatory (see section 6)|

### Inverter

|          Parameter           |                             Value                              |                 Note                 |
| :--------------------------: | :------------------------------------------------------------: | :----------------------------------: |
|   DC-link voltage (𝑉𝑑𝑐)   |                    280 V nominal, 60–320 V                     |                                      |
|  Rated output power (𝑃𝑜)   |                             300 W                              |    Lamp bank (Y or Δ) or reactor     |
|     Rated phase current      |                             2 Arms                             |          𝐼𝑚 =2.83 A peak           |
|    Output frequency (𝑓1)    |                   0.1–400 Hz, 60 Hz default                    |                                      |
| Switching frequency (𝑓𝑠𝑤) |              10 kHz nominal (IGBT), up to 20 kHz               |                                      |
|          Modulation          | Sinusoidal PWM (𝑚𝑎 ≤1), six-step (180∘) and 120∘ square wave |     Selected on the gating block     |
|          Dead time           |                         1.5 𝜇s (IGBT)                         |    Generated by the gating block     |
|        Output filter         |              None on board (optional external LC)              | Lamps and reactor accept PWM voltage |


## Repository structure

The repository is organized by converter family. Every family uses the same five stages, and each stage is numbered after its family (e.g. `2x` for DC/DC).

```
├── 00_docs/
	├── datasheets/
	├── formulas/
	├── architecture.md
	├── gate_bus_interface.md
├── 01_rectifier/
	├── 00_assets/
	├── 10_math/
		├── 11_ideal.md
		├── 12_losses.md
	├── 20_psim/
		├── 20_ideal.psim
		├── 21_losses.psim
	├── 30_pcb/
		├── rectifier_6p/
		├── scripts/
			├── gen_rectifier.py
			├── pcb_config.JSON
	├── 40_building/
	├── 60_tests/
├── 02_buck/
	├── ...                      (same logic as 01)
├── 03_boost/
	├── ...                      (same logic as 01)
├── 04_inverter/
	├── ...                      (same logic as 01) 
├── 05_gating_block
	├── 10_math/
		├── signal_budget.md
	├── 30_pcb/
		├── gating_block/
		├── scripts/
			├── gen_gating_block.py
			├── pcb_config.JSON
├── 90_tools
├── LICENSE
└── README.md
```

---

## Workflow
1. **Math**: requirements, operating point and component sizing.
2. **Simulation**: validation in PSIM, first with ideal and then with real device models.
3. **Electronics design**: schematic and layout in KiCad.
4. **3d**: Case design in Fusion 360.
5. **Building**: Assembly and details.
6. **Tests:** lab tetsting and results.

---

## Tools & Software

|      Purpose      |                 Tool                  |
| :---------------: | :-----------------------------------: |
|    Simulation     |                 PSIM                  |
| Schematic and PCB |                 KiCad                 |
| Enclosure design  |              Fusion 360               |
| Switching control |          ESP32 + Arduino IDE          |
|     Lab tests     | Electrical Machines Laboratory at UPB |

---

## License

Released under the [MIT License](LICENSE).

---

## Enlaces

[[power_electronics|Power Electronics]]
