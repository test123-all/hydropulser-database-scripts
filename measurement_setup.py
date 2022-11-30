from rdflib import Namespace
from modules.kraken import (
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

frame = PhysicalObject(data, EXP["FRAME_001"], "item frame calorimetry experiment", "FRAME_001", "FST", "FST")

rpi = PhysicalObject(data, FST["RPI_069"], "Raspberry Pi 4 Model B 2Gb", "RPI_069",
                     "FST", "Raspberry Pi Foundation").isHostedBy(frame.iri)

wbc = PhysicalObject(data, EXP["FRAME_001/WaterBathCold"], "Cold water bath for calorimetry experiment",
                     "FRAME_001/WaterBathCold", "FST", "unknown").isHostedBy(frame.iri)

wbh = PhysicalObject(data, EXP["FRAME_001/WaterBathHot"], "Hot water bath for calorimetry experiment",
                     "FRAME_001/WaterBathHot", "FST", "unknown").isHostedBy(frame.iri)

htr = PhysicalObject(data, FST["FRAME_001/Heater"], "immersion heater for energy input into hot water bath",
                     "FRAME_001/Heater", "FST", "unknown").isHostedBy(wbh.iri)

aa = PhysicalObject(data, EXP["FRAME_001/AmbientAir"], "ambient air around the calorimetry experiment",
                    "FRAME_001/AmbientAir", "FST", None)

specimen = PhysicalObject(data, EXP["SPECIMEN_001"], "material specimen calorimetry experiment",
                          "SPECIMEN_001", "FST", "FST").isHostedBy(wbh.iri)  # weight, heatcapacity

temp_wbc = ObservableProperty(data, EXP["FRAME_001/WaterBathCold/Temp"],
                              "temperature of cold water bath", QUANTITYKIND.Temperature, wbc.iri)

temp_wbh = ObservableProperty(data, EXP["FRAME_001/WaterBathHot/Temp"],
                              "temperature of hot water bath", QUANTITYKIND.Temperature, wbh.iri)

temp_aa = ObservableProperty(data, EXP["FRAME_001/AmbientAir/Temp"],
                             "temperature of ambient air around the calorimetry experiment",
                             QUANTITYKIND.Temperature, aa.iri)

volt_htr = ObservableProperty(data, EXP["FRAME_001/Heater/voltage"],
                              "voltage of immersion heater", QUANTITYKIND.Voltage, htr.iri)

curr_htr = ObservableProperty(data, EXP["FRAME_001/Heater/current"],
                              "current of immersion heater", QUANTITYKIND.ElectricCurrent, htr.iri)

s1 = Sensor(data, FST["TEMP_003"], "Keyestudio DS18B20 1m Waterproof Tube with Connect Module", "TEMP_003",
            "3c01f09540b7", "FST", "Keyestudio", "water bath").observes(temp_wbc.iri).isHostedBy(frame.iri)

s2 = Sensor(data, FST["TEMP_006"], "Keyestudio DS18B20 1m Waterproof Tube with Connect Module", "TEMP_006",
            "3c01f0963e25", "FST", "Keyestudio", "water bath").observes(temp_wbc.iri).isHostedBy(frame.iri)

s3 = Sensor(data, FST["TEMP_009"], "Keyestudio DS18B20 1m Waterproof Tube with Connect Module", "TEMP_009",
            "3c01f09538d1", "FST", "Keyestudio", "water bath").observes(temp_wbc.iri).isHostedBy(frame.iri)

swbh = Sensor(data, FST["TEMP_010"], "Keyestudio DS18B20 1m Waterproof Tube with Connect Module", "TEMP_010",
              "3ca9f649c484", "FST", "Keyestudio", "water bath").observes(temp_wbh.iri).isHostedBy(frame.iri)

saa = Sensor(data, FST["TEMP_005"], "Keyestudio DS18B20 1m Waterproof Tube with Connect Module", "TEMP_005",
             "0120188db2af", "FST", "Keyestudio", "water bath").observes(temp_aa.iri).isHostedBy(frame.iri)

# export metadata graph for experiment setup to ttl for later use
data.g.serialize(destination="./usecase_setup_rdf.ttl", format="longturtle")
