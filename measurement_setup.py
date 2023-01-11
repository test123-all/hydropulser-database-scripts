from rdflib import Namespace
from pyKRAKEN.kraken import (
    FST,
    QUANTITYKIND,
    Kraken,
    PhysicalObject,
    ObservableProperty,
    Sensor,
)

# declare Namespace for EXP specific entities
EXP = Namespace(FST["TutorialDigitalization/Calorimetry/"])

# build metadata graph for experiment setup
data = Kraken()

frame = PhysicalObject(data, iri=EXP["FRAME_001"], identifier="FRAME_001", label="item frame calorimetry experiment",
                       owner="FST", manufacturer="FST")

rpi = PhysicalObject(data, iri=FST["RPI_069"], identifier="RPI_069", label="Raspberry Pi 4 Model B 2Gb",
                     owner="FST", manufacturer="Raspberry Pi Foundation", isHostedBy=frame.iri)

wbc = PhysicalObject(data, iri=EXP["FRAME_001/WaterBathCold"], identifier="FRAME_001/WaterBathCold",
                     label="Cold water bath for calorimetry experiment",
                     owner="FST", manufacturer="unknown", isHostedBy=frame.iri)

wbh = PhysicalObject(data, iri=EXP["FRAME_001/WaterBathHot"], identifier="FRAME_001/WaterBathHot",
                     label="Hot water bath for calorimetry experiment",
                     owner="FST", manufacturer="unknown", isHostedBy=frame.iri)

htr = PhysicalObject(data, iri=FST["FRAME_001/Heater"], identifier="FRAME_001/Heater",
                     label="immersion heater for energy input into hot water bath",
                     owner="FST", manufacturer="unknown", isHostedBy=wbh.iri)

aa = PhysicalObject(data, iri=EXP["FRAME_001/AmbientAir"], identifier="FRAME_001/AmbientAir",
                    label="ambient air around the calorimetry experiment", owner="FST")

specimen = PhysicalObject(data, iri=EXP["SPECIMEN_001"], identifier="SPECIMEN_001",
                          label="material specimen calorimetry experiment",
                          owner="FST", manufacturer="FST", isHostedBy=wbh.iri)  # weight, heatcapacity

temp_wbc = ObservableProperty(data, iri=EXP["FRAME_001/WaterBathCold/Temp"], label="temperature of cold water bath",
                              hasQuantityKind=QUANTITYKIND.Temperature, isPropertyOf=wbc.iri)

temp_wbh = ObservableProperty(data, iri=EXP["FRAME_001/WaterBathHot/Temp"], label="temperature of hot water bath",
                              hasQuantityKind=QUANTITYKIND.Temperature, isPropertyOf=wbh.iri)

temp_aa = ObservableProperty(data, iri=EXP["FRAME_001/AmbientAir/Temp"],
                             label="temperature of ambient air around the calorimetry experiment",
                             hasQuantityKind=QUANTITYKIND.Temperature, isPropertyOf=aa.iri)

volt_htr = ObservableProperty(data, iri=EXP["FRAME_001/Heater/voltage"], label="voltage of immersion heater",
                              hasQuantityKind=QUANTITYKIND.Voltage, isPropertyOf=htr.iri)

curr_htr = ObservableProperty(data, iri=EXP["FRAME_001/Heater/current"], label="current of immersion heater",
                              hasQuantityKind=QUANTITYKIND.ElectricCurrent, isPropertyOf=htr.iri)

s1 = Sensor(data, iri=FST["TEMP_003"], identifier="TEMP_003",
            label="Keyestudio DS18B20 1m Waterproof Tube with Connect Module",
            owner="FST", manufacturer="Keyestudio", serialNumber="3c01f09540b7",
            location="water bath", isHostedBy=frame.iri).observes(temp_wbc.iri)

s2 = Sensor(data, iri=FST["TEMP_006"], identifier="TEMP_006",
            label="Keyestudio DS18B20 1m Waterproof Tube with Connect Module",
            owner="FST", manufacturer="Keyestudio", serialNumber="3c01f0963e25",
            location="water bath", isHostedBy=frame.iri).observes(temp_wbc.iri)

s3 = Sensor(data, iri=FST["TEMP_009"], identifier="TEMP_009",
            label="Keyestudio DS18B20 1m Waterproof Tube with Connect Module",
            owner="FST", manufacturer="Keyestudio", serialNumber="3c01f09538d1",
            location="water bath", isHostedBy=frame.iri).observes(temp_wbc.iri)

swbh = Sensor(data, iri=FST["TEMP_010"], identifier="TEMP_010",
              label="Keyestudio DS18B20 1m Waterproof Tube with Connect Module",
              owner="FST", manufacturer="Keyestudio", serialNumber="3ca9f649c484",
              location="water bath", isHostedBy=frame.iri).observes(temp_wbh.iri)

saa = Sensor(data, iri=FST["TEMP_005"], identifier="TEMP_005",
             label="Keyestudio DS18B20 1m Waterproof Tube with Connect Module",
             owner="FST", manufacturer="Keyestudio", serialNumber="0120188db2af",
             location="water bath", isHostedBy=frame.iri).observes(temp_aa.iri)

# export metadata graph for experiment setup to ttl for later use
data.g.serialize(destination="./calorimetry_setup_rdf.ttl", format="longturtle")
