#!/usr/bin/env python3
"""Generate the Diffuino selector schematic with kicad-sch-api.

The generated file is committed so readers do not need this Python dependency.
Run this script only when changing the circuit topology or presentation.
"""

from pathlib import Path

import kicad_sch_api as ksa


HERE = Path(__file__).resolve().parent
sch = ksa.create_schematic("Diffuino BCD Selector")


def add(lib, ref, value, x, y, *, rotation=0, footprint=None):
    return sch.components.add(
        lib,
        reference=ref,
        value=value,
        position=(x, y),
        rotation=rotation,
        footprint=footprint,
    )


def labels(ref, mapping):
    """Attach {pin: net_name} labels directly to symbol pins."""
    for pin, name in mapping.items():
        sch.add_label(name, pin=(ref, str(pin)), size=1.0)


def note(text, x, y, size=1.27):
    sch.add_text(text, (x, y), size=size)


# Page title and interface -------------------------------------------------
note("DIFFUINO — 4-BIT BCD SELECTOR, VALIDITY GATE, AND RESET", 115.0, 15.24, 2.0)
note("VALID = NOT(BCD3 AND (BCD2 OR BCD1));  D6 = GENERATE AND VALID", 115.0, 20.32, 1.27)
note("Arduino UNO Q interface", 35.0, 30.48, 1.27)

add(
    "Connector_Generic:Conn_01x08",
    "J1",
    "UNO_Q",
    38.1,
    45.72,
    footprint="Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical",
)
for pin, net in enumerate(["+5V", "GND", "B0_D2", "B1_D3", "B2_D4", "B3_D5", "TRIG_D6", "RESET_D7"], 1):
    labels("J1", {pin: net})

# Four-bit DIP selector ----------------------------------------------------
note("BCD input and indication", 82.0, 30.48, 1.27)
add(
    "Switch:SW_DIP_x04",
    "SW1",
    "BCD_SELECT",
    81.28,
    45.72,
    footprint="Button_Switch_THT:SW_DIP_SPSTx04_Slide_9.78x12.34mm_W7.62mm_P2.54mm",
)
# Left pins 1..4 are +5 V; right pins 8..5 are BCD3..BCD0.
for pin in range(1, 5):
    labels("SW1", {pin: "+5V"})
for pin, net in zip(range(8, 4, -1), ["B3R", "B2R", "B1R", "B0R"]):
    labels("SW1", {pin: net})

for index, (bit, d_pin, y) in enumerate(
    [(3, "B3_D5", 78.74), (2, "B2_D4", 96.52), (1, "B1_D3", 114.3), (0, "B0_D2", 132.08)], 1
):
    raw = f"B{bit}R"
    net = d_pin
    # Pulldown and RC filtering.
    add("Device:R", f"R{index}", "10k", 35.56, y, rotation=90, footprint="Resistor_SMD:R_0805_2012Metric")
    labels(f"R{index}", {1: raw, 2: "GND"})
    add("Device:C", f"C{index}", "10nF", 60.96, y, rotation=90, footprint="Capacitor_SMD:C_0805_2012Metric")
    labels(f"C{index}", {1: raw, 2: "GND"})
    add("Device:R", f"R{index + 4}", "1k", 86.36, y, rotation=90, footprint="Resistor_SMD:R_0805_2012Metric")
    labels(f"R{index + 4}", {1: raw, 2: net})
    # Buffered-by-resistor local indicator; about 3 mA at 5 V.
    add("Device:R", f"R{index + 8}", "1k", 111.76, y, rotation=90, footprint="Resistor_SMD:R_0805_2012Metric")
    labels(f"R{index + 8}", {1: raw, 2: f"L{bit}A"})
    add("Device:LED", f"D{index}", f"BCD{bit}", 137.16, y, rotation=90, footprint="LED_SMD:LED_0805_2012Metric")
    labels(f"D{index}", {2: f"L{bit}A", 1: "GND"})
    # D2...D5 input labels connect through the 1 k series resistors.

# Combinational validity network -----------------------------------------
note("BCD validity interlock (values 10–15 cannot trigger inference)", 202.0, 30.48, 1.27)
logic_fp = "Package_TO_SOT_SMD:SOT-23-5"
add("74xGxx:74AHC1G32", "U1", "74AHC1G32", 147.32, 45.72, footprint=logic_fp)
labels("U1", {1: "B2_D4", 2: "B1_D3", 3: "GND", 4: "B_OR_C", 5: "+5V"})
add("74xGxx:74AHC1G08", "U2", "74AHC1G08", 167.64, 45.72, footprint=logic_fp)
labels("U2", {1: "B3_D5", 2: "B_OR_C", 3: "GND", 4: "INVALID", 5: "+5V"})
add("74xGxx:74AHC1G04", "U3", "74AHC1G04", 187.96, 45.72, footprint=logic_fp)
labels("U3", {2: "INVALID", 3: "GND", 4: "VALID", 5: "+5V"})

add("Switch:SW_Push", "SW2", "GENERATE", 142.24, 71.12, footprint="Button_Switch_THT:SW_PUSH_6mm")
labels("SW2", {1: "+5V", 2: "GENERATE_RAW"})
add("Device:R", "R13", "10k", 154.94, 71.12, rotation=90, footprint="Resistor_SMD:R_0805_2012Metric")
labels("R13", {1: "GENERATE_RAW", 2: "GND"})
add("Device:C", "C5", "100nF", 167.64, 71.12, rotation=90, footprint="Capacitor_SMD:C_0805_2012Metric")
labels("C5", {1: "GENERATE_RAW", 2: "GND"})
add("74xGxx:74AHC1G08", "U4", "74AHC1G08", 187.96, 71.12, footprint=logic_fp)
labels("U4", {1: "GENERATE_RAW", 2: "VALID", 3: "GND", 4: "TRIGGER", 5: "+5V"})
add("Device:R", "R14", "1k", 208.28, 71.12, rotation=90, footprint="Resistor_SMD:R_0805_2012Metric")
labels("R14", {1: "TRIGGER", 2: "TRIG_D6"})

# Trigger indicator is isolated from the logic output by Q1.
add("Device:R", "R15", "10k", 187.96, 88.9, rotation=90, footprint="Resistor_SMD:R_0805_2012Metric")
labels("R15", {1: "TRIGGER", 2: "Q1_BASE"})
add("Transistor_BJT:Q_NPN_BCE", "Q1", "2N3904", 208.28, 88.9, footprint="Package_TO_SOT_THT:TO-92_Inline")
labels("Q1", {1: "Q1_BASE", 2: "TRIGGER_LED_K", 3: "GND"})
add("Device:LED", "D5", "TRIGGER", 226.06, 88.9, rotation=90, footprint="LED_THT:LED_D3.0mm")
labels("D5", {1: "TRIGGER_LED_K", 2: "TRIGGER_LED_A"})
add("Device:R", "R16", "1k", 241.3, 88.9, rotation=90, footprint="Resistor_SMD:R_0805_2012Metric")
labels("R16", {1: "TRIGGER_LED_A", 2: "+5V"})

# Dedicated reset path ----------------------------------------------------
note("Reset / re-arm", 139.7, 106.68, 1.27)
add("Switch:SW_Push", "SW3", "RESET", 142.24, 121.92, footprint="Button_Switch_THT:SW_PUSH_6mm")
labels("SW3", {1: "+5V", 2: "RESET_RAW"})
add("Device:R", "R17", "10k", 157.48, 121.92, rotation=90, footprint="Resistor_SMD:R_0805_2012Metric")
labels("R17", {1: "RESET_RAW", 2: "GND"})
add("Device:C", "C6", "100nF", 172.72, 121.92, rotation=90, footprint="Capacitor_SMD:C_0805_2012Metric")
labels("C6", {1: "RESET_RAW", 2: "GND"})
add("Device:R", "R18", "1k", 187.96, 121.92, rotation=90, footprint="Resistor_SMD:R_0805_2012Metric")
labels("R18", {1: "RESET_RAW", 2: "RESET_D7"})

# Supply bypass -----------------------------------------------------------
note("Power filtering — place each 100 nF capacitor beside its IC", 25.4, 142.24, 1.27)
for i, x in enumerate([38.1, 58.42, 78.74, 99.06], 7):
    add("Device:C", f"C{i}", "100nF", x, 157.48, rotation=90, footprint="Capacitor_SMD:C_0805_2012Metric")
    labels(f"C{i}", {1: "+5V", 2: "GND"})
add("Device:C_Polarized", "C11", "10uF", 121.92, 157.48, rotation=90, footprint="Capacitor_THT:C_Radial_D5.0mm_H5.0mm_P2.00mm")
labels("C11", {1: "+5V", 2: "GND"})
add("power:PWR_FLAG", "#FLG01", "PWR_FLAG", 220.98, 157.48)
labels("#FLG01", {1: "+5V"})
add("power:PWR_FLAG", "#FLG02", "PWR_FLAG", 238.76, 157.48)
labels("#FLG02", {1: "GND"})

note("Firmware adds 40 ms debounce, ignores D6 while sampling, and latches the result until D7 reset.", 25.4, 177.8, 1.0)
note("Use only the UNO Q STM32 digital header shown here; do not connect these 5 V nets to 1.8 V MPU GPIO.", 25.4, 182.88, 1.0)

sch.save(HERE / "diffuino_selector.kicad_sch")
print(f"saved {HERE / 'diffuino_selector.kicad_sch'}")
