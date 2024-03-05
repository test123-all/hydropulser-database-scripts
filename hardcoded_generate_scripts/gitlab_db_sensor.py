import os
from pathlib import Path
from urllib.parse import quote
import warnings

import rdflib
from rdflib import Namespace, Literal, URIRef
from rdflib.namespace import RDF, FOAF, SOSA, DCTERMS, XSD
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
    if (df_row["Messbereich von"] == None
            or isinstance(df_row["Messbereich von"], str)):
        raise ValueError

    if (df_row["Messbereich bis"] == None
            or isinstance(df_row["Messbereich bis"], str)):
        raise ValueError

    if (df_row["Ausgabebereich von"] == None
            or isinstance(df_row["Ausgabebereich von"], str)):
        raise ValueError

    if (df_row["Ausgabebereich bis"] == None
            or isinstance(df_row["Ausgabebereich bis"], str)):
        raise ValueError


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
                          minValue=Literal(str(df_row["Messbereich von"]), datatype=XSD.double), maxValue=Literal(str(df_row["Messbereich bis"]), datatype=XSD.double), unit=unit_dict[df_row["Messbereich Einheit"]],
                          iri=SENSOR[sensor_id + "/MeasurementRange"], identifier=None, name="measurement range",
                          rdftype=SSN_SYSTEM.MeasurementRange)

    if val_ref is not None:
        data.g.add((meas_range.iri, SDO.valueReference, Literal(val_ref)))

    sensor_actuation_range = Quantity(data, isPropertyOf=sys_capa.iri, hasQuantityKind=QUANTITYKIND.Voltage,
                                      minValue=Literal(str(df_row["Ausgabebereich von"]), datatype=XSD.double), maxValue=Literal(str(df_row["Ausgabebereich bis"]), datatype=XSD.double),
                                      unit=unit_dict[df_row["Ausgabebereich Einheit"]],
                                      iri=SENSOR[sensor_id + "/SensorActuationRange"], identifier=None, name="sensor output voltage range",
                                      rdftype=SSN_SYSTEM.ActuationRange)

    sensitivity = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/Sensitivity"],
                           comment="gain", rdftype=SSN_SYSTEM.Sensitivity, name="sensitivity", value=Literal(str(df_row["Kennlinie Steigung _ Sensitivity"]), datatype=XSD.double))

    bias = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/Bias"],
                    comment="offset", rdftype=SSN_SYSTEM.SystemProperty, name="bias",
                    value=Literal(str(df_row["Kennlinie Offset _ Bias"]), datatype=XSD.double))

    if df_row["Bias Uncertainty Unit"] in unit_dict.keys():
        bias_uncertainty_unit = unit_dict[df_row["Bias Uncertainty Unit"]]
    else:
        bias_uncertainty_unit = df_row["Bias Uncertainty Unit"]

    if df_row["Bias Uncertainty"] is None:
        bias_uncertainty_value = None
    else:
        bias_uncertainty_value = Literal(str(df_row["Bias Uncertainty"]), datatype=XSD.double)
    bias_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/BiasUncertainty"],
                    name="bias uncertainty",
                    description="The bias uncertainty of the sensor of the linear transfer function of a sensor.",
                    seeAlso=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                             URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                    conformsTo=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                    value=bias_uncertainty_value,
                    unit=bias_uncertainty_unit,
                    comment=df_row["Bias Uncertainty Comment"])

    if df_row["Sensitivity Uncertainty Unit"] in unit_dict.keys():
        sensitivity_uncertainty_unit = unit_dict[df_row["Sensitivity Uncertainty Unit"]]
    else:
        sensitivity_uncertainty_unit = df_row["Sensitivity Uncertainty Unit"]

    if df_row["Sensitivity Uncertainty Unit"] is None:
        sensitivity_uncertainty_value = None
    else:
        sensitivity_uncertainty_value = Literal(str(df_row["Sensitivity Uncertainty"]), datatype=XSD.double)
    sensitivity_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/SensitivityUncertainty"],
                                        description="The sensitivity uncertainty of the linear transfer function of a sensor.",
                                        name="sensitivity uncertainty",
                                       seeAlso=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                                URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                                       conformsTo=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                                   URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                                        value=sensitivity_uncertainty_value,
                                        unit=sensitivity_uncertainty_unit,
                                        comment=df_row["Sensitivity Uncertainty Comment"])

    if df_row["Linearity Uncertainty Unit"] in unit_dict.keys():
        linearity_uncertainty_unit = unit_dict[df_row["Linearity Uncertainty Unit"]]
    else:
        linearity_uncertainty_unit = df_row["Linearity Uncertainty Unit"]

    if df_row["Linearity Uncertainty"] is None:
        linearity_uncertainty_value = None
    else:
        linearity_uncertainty_value = Literal(str(df_row["Linearity Uncertainty"]), datatype=XSD.double)
    linearity_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/LinearityUncertainty"],
                               name="linearity uncertainty",
                               seeAlso=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                        URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                               conformsTo=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                           URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                               description="The linearity uncertainty of the linear transfer function of a sensor.",
                               value=linearity_uncertainty_value,
                               unit=linearity_uncertainty_unit,
                               comment=df_row["Linearity Uncertainty Comment"])

    if df_row["Hysteresis Uncertainty Unit"] in unit_dict.keys():
        hysteresis_uncertainty_unit = unit_dict[df_row["Hysteresis Uncertainty Unit"]]
    else:
        hysteresis_uncertainty_unit = df_row["Hysteresis Uncertainty Unit"]

    if df_row["Hysteresis Uncertainty"] is None:
        hysteresis_uncertainty_value = None
    else:
        hysteresis_uncertainty_value = Literal(str(df_row["Hysteresis Uncertainty"]), datatype=XSD.double)
    hysteresis_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/HysteresisUncertainty"],
                                name="hysteresis uncertainty",
                                seeAlso=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                         URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                                conformsTo=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                            URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                                description="The hysteresis uncertainty of the linear transfer function of a sensor.",
                                value=hysteresis_uncertainty_value,
                                unit=hysteresis_uncertainty_unit,
                                comment=df_row["Hysteresis Uncertainty Comment"])

    # We got all info we want > make dirs if they don't exist
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
    data.g.add((docttl, RDF.type, SDO.TextObject))
    data.g.add((docttl, FOAF.primaryTopic, sensor.iri))  # schema:about
    data.g.add((docttl, SDO.encodingFormat, Literal('text/turtle')))

    docxml = SENSOR[sensor_id + "/rdf.xml"]
    data.g.add((docxml, RDF.type, FOAF.Document))
    data.g.add((docxml, RDF.type, SDO.TextObject))
    data.g.add((docxml, FOAF.primaryTopic, sensor.iri))
    data.g.add((docxml, SDO.encodingFormat, Literal('application/rdf+xml')))

    docjson = SENSOR[sensor_id + "/rdf.json"]
    data.g.add((docjson, RDF.type, FOAF.Document))
    data.g.add((docjson, RDF.type, SDO.TextObject))
    data.g.add((docjson, FOAF.primaryTopic, sensor.iri))
    # TODO: FIXME: Falls iana als seite bleibt oder älter ist könnte man auch kucken ob man die URL von dort als p_ID verwendet https://www.iana.org/assignments/media-types/media-types.xhtml
    # TODO: FIXME: auch n0ochmal kucken ob das sinnvoll ist beides anzugeben, oder nur die rdf sachen
    data.g.add((docjson, SDO.encodingFormat, Literal('application/json')))
    data.g.add((docjson, SDO.encodingFormat, Literal('application/ld+json')))

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
            try:
                generate_sensor_files(f"{generated_files_directory_path}/", sheet_name, row)
            except ValueError as e:
                warnings.warn(f'There is a value error in one of the inputs in the {row["Ident-Nummer"]} line.\nSkipping Line..', category=Warning, stacklevel=1)
                pass

