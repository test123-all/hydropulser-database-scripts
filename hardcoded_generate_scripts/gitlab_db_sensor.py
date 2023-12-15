import os
from pathlib import Path
from urllib.parse import quote

from rdflib import Namespace, Literal, URIRef
from rdflib.namespace import RDF, FOAF, SOSA, DCTERMS
import pandas as pd
import numpy as np

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


SENSOR = Namespace("https://w3id.org/fst/resource/")

quantitykind_dict = {"Druck": QUANTITYKIND.Pressure,
                     "Kraft": QUANTITYKIND.Force,
                     "Temperatur": QUANTITYKIND.Temperature,
                     "Weg": QUANTITYKIND.Displacement}

unit_dict = {"bar": UNIT.BAR,
             "mbar": UNIT.MilliBAR,
             "psi": UNIT.PSI,
             "kPa": UNIT.KiloPA,
             "MPa": UNIT.MegaPA,
             "°C": UNIT.DEG_C,
             "K": UNIT.K,
             "N": UNIT.N,
             "kN": UNIT.KiloN,
             "mm": UNIT.MilliM,
             "cm": UNIT.CentiM,
             "V": UNIT.V,
             "mV": UNIT.MilliV,
             "µV": UNIT.MicroV}


def generate_sensor_files(sensor_dir, sheet_name, df_row):
    data = Kraken()
    data.g.bind("fst", SENSOR)

    sensor_id = df_row["uuid"]  # str(uuid6())
    fst_id = df_row["Ident-Nummer"]
    if sheet_name == "Druck":
        val_ref = df_row["absolut/ relativ"]
    else:
        val_ref = None
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

    sensor_actuation_range = Quantity(data, isPropertyOf=sys_capa.iri, hasQuantityKind=QUANTITYKIND.Voltage,
                                      minValue=df_row["Ausgabebereich von"], maxValue=df_row["Ausgabebereich bis"],
                                      unit=unit_dict[df_row["Ausgabebereich Einheit"]],
                                      iri=SENSOR[sensor_id + "/SensorActuationRange"], identifier=None, name="sensor output voltage range",
                                      rdftype=SSN_SYSTEM.ActuationRange)

    sensitivity = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/Sensitivity"],
                           comment="gain", rdftype=SSN_SYSTEM.Sensitivity, name="sensitivity", value=df_row["Kennlinie Steigung _ Sensitivity"])

    bias = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/Bias"],
                    comment="offset", rdftype=SSN_SYSTEM.SystemProperty, name="bias",
                    value=df_row["Kennlinie Offset _ Bias"])

    bias_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/BiasUncertainty"],
                    name="bias uncertainty",
                    description="The bias uncertainty of the sensor of the linear transfer function of a sensor.",
                    seeAlso=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"),
                    conformsTo=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"),
                    value=df_row["Bias Uncertainty"])

    sensitivity_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/SensitivityUncertainty"],
                                 description="The sensitivity uncertainty of the linear transfer function of a sensor.",
                                 name="sensitivity uncertainty", seeAlso=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"), conformsTo=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"),
                                 value=df_row["Sensitivity Uncertainty"])

    linearity_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/LinearityUncertainty"],
                               name="linearity uncertainty", seeAlso=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"), conformsTo=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"),
                               description="The linearity uncertainty of the linear transfer function of a sensor.",
                               value=df_row["Linearity Uncertainty"])

    hysteresis_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/HysteresisUncertainty"],
                                name="hysteresis uncertainty", seeAlso=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"), conformsTo=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"),
                                description="The hysteresis uncertainty of the linear transfer function of a sensor.",
                                value=df_row["Hysteresis Uncertainty"])

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



def run_script(sensor_table_path: [Path, str], generated_files_directory_path: [Path, str]):
    SUPPORTED_SENSOR_TABLE_SHEET_NAMES = ["Druck",
                                          "Kraft",
                                          "Temperatur",
                                          "Weg"]

    # Get the path of the direcotry of this file
    directory_path = Path(__file__).parent.resolve()

    dfs = pd.read_excel(sensor_table_path, sheet_name=None, skiprows=[1])
    # sensor_dir = "C:/Users/NP/Documents/AIMS/metadata_hub/data/fst_measurement_equipment/"
    try:
        generated_files_directory_path.mkdir()
    except FileExistsError:
        pass

    for sheet_name in SUPPORTED_SENSOR_TABLE_SHEET_NAMES:
        df = dfs[sheet_name]
        for idx in df.index:
            row = df.iloc[idx]
            row = row.replace({np.nan: None})

            # TODO: Add some control code that checks if the necessary minimal set of information is present
            generate_sensor_files(f"{generated_files_directory_path}/", sheet_name, row)
