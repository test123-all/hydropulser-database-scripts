import os

from pathlib import Path
from urllib.parse import quote
from rdflib import Namespace, Literal, URIRef
from rdflib.namespace import RDF, FOAF, SOSA, DCTERMS
from pyKRAKEN.kraken import (
    SDO,
    DBO,
    UNIT,
    QUANTITYKIND,
    SSN_SYSTEM,
    Kraken,
    Sensor,
    SensorCapability,
    Property,
    Quantity
)
import pandas as pd
import numpy as np


SENSOR = Namespace("https://w3id.org/fst/resource/")

quantitykind_dict = {"Druck": QUANTITYKIND.Pressure,
                     "Temperatur": QUANTITYKIND.Temperature,
                     "Kraft": QUANTITYKIND.Force,
                     "Weg": QUANTITYKIND.Displacement}

unit_dict = {"bar": UNIT.BAR,
             "mbar": UNIT.MilliBAR,
             "psi": UNIT.PSI,
             "°C": UNIT.DEG_C,
             "N": UNIT.N,
             "kN": UNIT.KiloN,
             "mm": UNIT.MilliM}


def generate_sensor_files(sensor_dir, sheet_name, df_row):
    data = Kraken()
    data.g.bind("fst", SENSOR)

    sensor_id = df_row["uuid"]  # str(uuid6())
    fst_id = df_row["Ident-Nummer"]
    val_ref = None # df_row["absolut/ relativ"]
    maintainer = df_row["Verantwortlicher WiMi"]
    meas_tech = df_row["Messprinzip"]
    modified = df_row["letzte Prüfung/ Kalibration"]
    rel = df_row["Zubehör"]

    # the sensor
    sensor = Sensor(data, hasSensorCapability=SENSOR[sensor_id + "/SensorCapability"],
                    iri=SENSOR[sensor_id], identifier=sensor_id, name=df_row["Bezeichnung"],
                    comment=df_row["Bemerkung"], owner="FST", manufacturer=df_row["Hersteller"],
                    serialNumber=str(df_row["Seriennummer"]), location=df_row["Aufbewahrungsort"])
    sensor.identifier = f"fst-inv:{fst_id}"
    data.g.add((sensor.iri, DBO.maintainedBy, Literal(maintainer)))
    data.g.add((sensor.iri, SOSA.usedProcedure, Literal(meas_tech)))
    data.g.add((sensor.iri, SDO.keywords, Literal(sheet_name)))
    data.g.add((sensor.iri, DCTERMS.modified, Literal(modified)))
    if val_ref is not None:
        data.g.add((sensor.iri, SDO.keywords, Literal(val_ref)))
    if meas_tech is not None:
        data.g.add((sensor.iri, SDO.keywords, Literal(meas_tech)))
    if rel is not None:
        data.g.add((sensor.iri, DCTERMS.relation, Literal(rel)))

    # properties
    sys_capa = SensorCapability(data, iri=SENSOR[sensor_id + "/SensorCapability"], name="sensor capabilities",
                                comment="sensor capabilities not regarding any conditions at this time")

    meas_range = Quantity(data, isPropertyOf=sys_capa.iri, hasQuantityKind=quantitykind_dict[sheet_name],
                          minValue=df_row["Messbereich von"], maxValue=df_row["Messbereich bis"], unit=unit_dict[df_row["Messbereich Einheit"]],
                          iri=SENSOR[sensor_id + "/MeasurementRange"], identifier=None, name="measurement range",
                          rdftype=SSN_SYSTEM.MeasurementRange)
    if val_ref is not None:
        data.g.add((meas_range.iri, SDO.valueReference, Literal(val_ref)))

    sensitivity = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/Sensitivity"],
                           comment="gain", rdftype=SSN_SYSTEM.Sensitivity, name="sensitivity", value=df_row["Kennlinie Steigung"])

    bias = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/Bias"],
                    comment="offset", rdftype=SSN_SYSTEM.SystemProperty, name="bias", value=df_row["Kennlinie Offset"])

    # we got all info we want > make dirs if they dont exist
    rdfpath = sensor_dir + sensor_id + "/"
    docpath = rdfpath + "docs"
    imgpath = rdfpath + "img"
    Path(docpath).mkdir(parents=True, exist_ok=True)
    Path(imgpath).mkdir(parents=True, exist_ok=True)

    # documentation
    with os.scandir(imgpath) as it:
        for entry in it:
            if entry.name.lower().endswith((".png", ".jpg", "jpeg")) and entry.is_file():
                img = URIRef("img/" + quote(entry.name))
                sensor.subjectOf = img
                sensor.image = img

    docs = URIRef("docs/")
    sensor.subjectOf = docs
    sensor.documentation = docs

    with os.scandir(docpath) as it:
        for entry in it:
            if entry.is_file():
                datasheet = URIRef("docs/" + quote(entry.name))
                sensor.subjectOf = datasheet
                sensor.documentation = datasheet

    # rdf doc references
    docttl = SENSOR[sensor_id + "/rdf.ttl"]
    data.g.add((docttl, RDF.type, FOAF.Document))  # schema:CreativeWork
    data.g.add((docttl, FOAF.primaryTopic, sensor.iri))  # schema:about

    docxml = SENSOR[sensor_id + "/rdf.xml"]
    data.g.add((docxml, RDF.type, FOAF.Document))
    data.g.add((docxml, FOAF.primaryTopic, sensor.iri))

    docjson = SENSOR[sensor_id + "/rdf.json"]
    data.g.add((docjson, RDF.type, FOAF.Document))
    data.g.add((docjson, FOAF.primaryTopic, sensor.iri))

    print(data.g.serialize(destination=rdfpath + "rdf.json", format="json-ld", auto_compact=True))
    print(data.g.serialize(destination=rdfpath + "rdf.ttl", base=SENSOR, format="longturtle"))
    print(data.g.serialize(destination=rdfpath + "rdf.xml", base=SENSOR, format="xml"))


dfs = pd.read_excel("info_Messtechnik_Uebersicht_FST_Wetterich_NEU.xlsx", sheet_name=None, skiprows=[1])

sheet_name = "Weg"
# sensor_dir = "C:/Users/NP/Documents/AIMS/metadata_hub/data/fst_measurement_equipment/"
sensor_dir = "./_generated/"

df = dfs[sheet_name]
for idx in df.index:
    row = df.iloc[idx]
    row = row.replace({np.nan: None})
    if row['Verantwortlicher WiMi'] == 'Rexer':
        generate_sensor_files(sensor_dir, sheet_name, row)
