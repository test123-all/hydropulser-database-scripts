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
                     "Weg": QUANTITYKIND.Displacement,
                     "Leistung": QUANTITYKIND.Power,
                     "Volumenstrom": QUANTITYKIND.VolumeFlowRate}

unit_dict = {"bar": UNIT.BAR,
             "mbar": UNIT.MilliBAR,
             "psi": UNIT.PSI,
             "Pa": UNIT.PA,
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
             "µV": UNIT.MicroV,
             "A": UNIT.A,
             "W": UNIT.W,
             "m^3/s": UNIT['M3-PER-SEC'],
             "m^3/h": UNIT['M3-PER-HR']}


def generate_sensor_files(sensor_dir, sheet_name, df_row):
    if (df_row["Sensor Messbereich von"] == None
            or isinstance(df_row["Sensor Messbereich von"], str)):
        raise ValueError

    if (df_row["Sensor Messbereich bis"] == None
            or isinstance(df_row["Sensor Messbereich bis"], str)):
        raise ValueError

    if (df_row["Sensor Ausgabebereich von"] == None
            or isinstance(df_row["Sensor Ausgabebereich von"], str)):
        raise ValueError

    if (df_row["Sensor Ausgabebereich bis"] == None
            or isinstance(df_row["Sensor Ausgabebereich bis"], str)):
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
                          minValue=Literal(str(df_row["Sensor Messbereich von"]), datatype=XSD.double), maxValue=Literal(str(df_row["Sensor Messbereich bis"]), datatype=XSD.double), unit=unit_dict[df_row["Sensor Messbereich Einheit"]],
                          iri=SENSOR[sensor_id + "/SensorCapability/MeasurementRange"], identifier=None, name="sensor measurement range",
                          rdftype=SSN_SYSTEM.MeasurementRange)

    if val_ref is not None:
        data.g.add((meas_range.iri, SDO.valueReference, Literal(val_ref)))

    sensor_actuation_range = Quantity(data, isPropertyOf=sys_capa.iri, hasQuantityKind=QUANTITYKIND.Voltage,
                                      minValue=Literal(str(df_row["Sensor Ausgabebereich von"]), datatype=XSD.double), maxValue=Literal(str(df_row["Sensor Ausgabebereich bis"]), datatype=XSD.double),
                                      unit=unit_dict[df_row["Sensor Ausgabebereich Einheit"]],
                                      iri=SENSOR[sensor_id + "/SensorCapability/ActuationRange"], identifier=None, name="sensor output range",
                                      rdftype=SSN_SYSTEM.ActuationRange)
    sensitivity = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/SensorCapability/Sensitivity"],
                           comment="gain", rdftype=SSN_SYSTEM.Sensitivity, name="sensitivity",
                           value=Literal(str(df_row["Sensor Kennlinie _ Sensitivity"]), datatype=XSD.double),
                           unit=Literal(f'({str(df_row["Sensor Messbereich Einheit"])})/({str(df_row["Sensor Ausgabebereich Einheit"])})'),)

    bias = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/SensorCapability/Bias"],
                    comment="offset", rdftype=SSN_SYSTEM.SystemProperty, name="bias",
                    value=Literal(str(df_row["Sensor Kennlinie _ Bias"]), datatype=XSD.double),
                    unit=unit_dict[df_row["Sensor Messbereich Einheit"]])

    if (df_row["Absolute Bias Uncertainty Unit"] is not None
            and df_row["Absolute Bias Uncertainty Unit"] in unit_dict.keys()):
        absolute_bias_uncertainty_unit = unit_dict[df_row["Absolute Bias Uncertainty Unit"]]
    elif (df_row["Absolute Bias Uncertainty Unit"] is None
          or (isinstance(df_row["Absolute Bias Uncertainty"], str)
              and df_row["Absolute Bias Uncertainty"].lower() == 'unknown')):
        absolute_bias_uncertainty_unit = None
    elif (df_row["Absolute Bias Uncertainty Unit"] is not None
            and df_row["Absolute Bias Uncertainty Unit"] not in unit_dict.keys()):
        absolute_bias_uncertainty_unit = df_row["Absolute Bias Uncertainty Unit"]

    if (df_row["Absolute Bias Uncertainty"] is None
            or (isinstance(df_row["Absolute Bias Uncertainty"], str)
                and df_row["Absolute Bias Uncertainty"].lower() == 'unknown')):
        absolute_bias_uncertainty_value = None
    else:
        absolute_bias_uncertainty_value = Literal(str(df_row["Absolute Bias Uncertainty"]), datatype=XSD.double)

    if (df_row["Absolute Bias Uncertainty Comment"] is None
            or (isinstance(df_row["Absolute Bias Uncertainty Comment"], str)
                and df_row["Absolute Bias Uncertainty Comment"].lower() == 'unknown')):
        absolute_bias_uncertainty_comment = None
    else:
        absolute_bias_uncertainty_comment = Literal(str(df_row["Absolute Bias Uncertainty Comment"]))

    if (df_row["Absolute Bias Uncertainty Keywords"] is None
            or (isinstance(df_row["Absolute Bias Uncertainty Keywords"], str)
                and df_row["Absolute Bias Uncertainty Keywords"].lower() == 'unknown')):
        absolute_bias_uncertainty_keywords_list = None
    else:
        temp_string = str(df_row["Absolute Bias Uncertainty Keywords"])
        absolute_bias_uncertainty_keywords_list = temp_string.split(';')
        del temp_string

    absolute_bias_uncertainty = Property(data, isPropertyOf=bias.iri, iri=SENSOR[sensor_id + "/SensorCapability/Bias/AbsoluteBiasUncertainty"],
                    name="bias uncertainty",
                    description="The absolute bias uncertainty of the sensor of the linear transfer function of a sensor.",
                    seeAlso=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                             URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                    conformsTo=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                    value=absolute_bias_uncertainty_value,
                    unit=absolute_bias_uncertainty_unit,
                    comment=absolute_bias_uncertainty_comment,
                    keywords_list=absolute_bias_uncertainty_keywords_list)

    if (df_row["Relative Bias Uncertainty Unit"] is not None
            and df_row["Relative Bias Uncertainty Unit"] in unit_dict.keys()):
        relative_bias_uncertainty_unit = unit_dict[df_row["Relative Bias Uncertainty Unit"]]
    elif (df_row["Relative Bias Uncertainty Unit"] is None
          or (isinstance(df_row["Relative Bias Uncertainty"], str)
              and df_row["Relative Bias Uncertainty"].lower() == 'unknown')):
        relative_bias_uncertainty_unit = None
    elif (df_row["Relative Bias Uncertainty Unit"] is not None
            and df_row["Relative Bias Uncertainty Unit"] not in unit_dict.keys()):
        relative_bias_uncertainty_unit = df_row["Relative Bias Uncertainty Unit"]

    if (df_row["Relative Bias Uncertainty"] is None
            or (isinstance(df_row["Relative Bias Uncertainty"], str)
                and df_row["Relative Bias Uncertainty"].lower() == 'unknown')):
        relative_bias_uncertainty_value = None
    else:
        relative_bias_uncertainty_value = Literal(str(df_row["Relative Bias Uncertainty"]), datatype=XSD.double)

    if (df_row["Relative Bias Uncertainty Comment"] is None
            or (isinstance(df_row["Relative Bias Uncertainty Comment"], str)
                and df_row["Relative Bias Uncertainty Comment"].lower() == 'unknown')):
        relative_bias_uncertainty_comment = None
    else:
        relative_bias_uncertainty_comment = Literal(str(df_row["Relative Bias Uncertainty Comment"]))

    if (df_row["Relative Bias Uncertainty Keywords"] is None
            or (isinstance(df_row["Relative Bias Uncertainty Keywords"], str)
                and df_row["Relative Bias Uncertainty Keywords"].lower() == 'unknown')):
        relative_bias_uncertainty_keywords_list = None
    else:
        temp_string = str(df_row["Relative Bias Uncertainty Keywords"])
        relative_bias_uncertainty_keywords_list = temp_string.split(';')
        del temp_string

    relative_bias_uncertainty = Property(data, isPropertyOf=bias.iri, iri=SENSOR[sensor_id + "/SensorCapability/Bias/RelativeBiasUncertainty"],
                    name="bias uncertainty",
                    description="The relative bias uncertainty of the sensor of the linear transfer function of a sensor.",
                    seeAlso=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                             URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                    conformsTo=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                    value=relative_bias_uncertainty_value,
                    unit=relative_bias_uncertainty_unit,
                    comment=relative_bias_uncertainty_comment,
                    keywords_list=relative_bias_uncertainty_keywords_list)

    if (df_row["Sensitivity Uncertainty Unit"] is not None
            and df_row["Sensitivity Uncertainty Unit"] in unit_dict.keys()):
        sensitivity_uncertainty_unit = unit_dict[df_row["Sensitivity Uncertainty Unit"]]
    elif (df_row["Sensitivity Uncertainty Unit"] is None
          or (isinstance(df_row["Sensitivity Uncertainty"], str)
              and df_row["Sensitivity Uncertainty"].lower() == 'unknown')):
        sensitivity_uncertainty_unit = None
    elif (df_row["Sensitivity Uncertainty Unit"] is not None
          and df_row["Sensitivity Uncertainty Unit"] not in unit_dict.keys()):
        sensitivity_uncertainty_unit = df_row["Sensitivity Uncertainty Unit"]

    if (df_row["Sensitivity Uncertainty"] is None
            or (isinstance(df_row["Sensitivity Uncertainty"], str)
                and df_row["Sensitivity Uncertainty"].lower() == 'unknown')):
        sensitivity_uncertainty_value = None
    else:
        sensitivity_uncertainty_value = Literal(str(df_row["Sensitivity Uncertainty"]), datatype=XSD.double)

    if (df_row["Sensitivity Uncertainty Comment"] is None
            or (isinstance(df_row["Sensitivity Uncertainty Comment"], str)
                and df_row["Sensitivity Uncertainty Comment"].lower() == 'unknown')):
        sensitivity_uncertainty_comment= None
    else:
        sensitivity_uncertainty_comment = Literal(str(df_row["Sensitivity Uncertainty Comment"]))

    if (df_row["Sensitivity Uncertainty Keywords"] is None
            or (isinstance(df_row["Sensitivity Uncertainty Keywords"], str)
                and df_row["Sensitivity Uncertainty Keywords"].lower() == 'unknown')):
        sensitivity_uncertainty_keywords_list = None
    else:
        temp_string = str(df_row["Sensitivity Uncertainty Keywords"])
        sensitivity_uncertainty_keywords_list = temp_string.split(';')
        del temp_string

    sensitivity_uncertainty = Property(data, isPropertyOf=sensitivity.iri, iri=SENSOR[sensor_id + "/SensorCapability/Sensitivity/SensitivityUncertainty"],
                                        description="The sensitivity uncertainty of the linear transfer function of a sensor.",
                                        name="sensitivity uncertainty",
                                       seeAlso=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                                URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                                       conformsTo=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                                   URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                                        value=sensitivity_uncertainty_value,
                                        unit=sensitivity_uncertainty_unit,
                                        comment=sensitivity_uncertainty_comment,
                                        keywords_list=sensitivity_uncertainty_keywords_list)

    if (df_row["Linearity Uncertainty Unit"] is not None
            and df_row["Linearity Uncertainty Unit"] in unit_dict.keys()):
        linearity_uncertainty_unit = unit_dict[df_row["Linearity Uncertainty Unit"]]
    elif (df_row["Linearity Uncertainty Unit"] is None
            or (isinstance(df_row["Linearity Uncertainty Unit"], str)
                and df_row["Linearity Uncertainty Unit"].lower() == 'unknown')):
        linearity_uncertainty_unit = None
    elif (df_row["Linearity Uncertainty Unit"] is not None
          and df_row["Linearity Uncertainty Unit"] not in unit_dict.keys()):
        linearity_uncertainty_unit = df_row["Linearity Uncertainty Unit"]

    if (df_row["Linearity Uncertainty"] is None
            or (isinstance(df_row["Linearity Uncertainty"], str)
                and df_row["Linearity Uncertainty"].lower() == 'unknown')):
        linearity_uncertainty_value = None
    else:
        linearity_uncertainty_value = Literal(str(df_row["Linearity Uncertainty"]), datatype=XSD.double)

    if (df_row["Linearity Uncertainty Comment"] is None
            or (isinstance(df_row["Linearity Uncertainty Comment"], str)
                and df_row["Linearity Uncertainty Comment"].lower() == 'unknown')):
        linearity_uncertainty_comment = None
    else:
        linearity_uncertainty_comment = Literal(str(df_row["Linearity Uncertainty Comment"]))

    if (df_row["Linearity Uncertainty Keywords"] is None
            or (isinstance(df_row["Linearity Uncertainty Keywords"], str)
                and df_row["Linearity Uncertainty Keywords"].lower() == 'unknown')):
        linearity_uncertainty_keywords_list = None
    else:
        temp_string = str(df_row["Linearity Uncertainty Keywords"])
        linearity_uncertainty_keywords_list = temp_string.split(';')
        del temp_string

    linearity_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/SensorCapability/LinearityUncertainty"],
                               name="linearity uncertainty",
                               seeAlso=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                        URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                               conformsTo=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                           URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                               description="The linearity uncertainty of the linear transfer function of a sensor.",
                               value=linearity_uncertainty_value,
                               unit=linearity_uncertainty_unit,
                               comment=linearity_uncertainty_comment,
                               keywords_list=linearity_uncertainty_keywords_list)

    if (df_row["Hysteresis Uncertainty Unit"] is not None
            and df_row["Hysteresis Uncertainty Unit"] in unit_dict.keys()):
        hysteresis_uncertainty_unit = unit_dict[df_row["Hysteresis Uncertainty Unit"]]
    elif (df_row["Hysteresis Uncertainty Unit"] is None
          or (isinstance(df_row["Hysteresis Uncertainty Unit"], str)
              and df_row["Hysteresis Uncertainty Unit"].lower() == 'unknown')):
        hysteresis_uncertainty_unit = None
    elif (df_row["Hysteresis Uncertainty Unit"] is not None
          and df_row["Hysteresis Uncertainty Unit"] not in unit_dict.keys()):
        hysteresis_uncertainty_unit = df_row["Hysteresis Uncertainty Unit"]

    if (df_row["Hysteresis Uncertainty"] is None
            or (isinstance(df_row["Hysteresis Uncertainty"], str)
                and df_row["Hysteresis Uncertainty"].lower() == 'unknown')):
        hysteresis_uncertainty_value = None
    else:
        hysteresis_uncertainty_value = Literal(str(df_row["Hysteresis Uncertainty"]), datatype=XSD.double)

    if (df_row["Hysteresis Uncertainty Comment"] is None
            or (isinstance(df_row["Hysteresis Uncertainty Comment"], str)
                and df_row["Hysteresis Uncertainty Comment"].lower() == 'unknown')):
        hysteresis_uncertainty_comment = None
    else:
        hysteresis_uncertainty_comment = Literal(str(df_row["Hysteresis Uncertainty Comment"]))

    if (df_row["Hysteresis Uncertainty Keywords"] is None
            or (isinstance(df_row["Hysteresis Uncertainty Keywords"], str)
                and df_row["Hysteresis Uncertainty Keywords"].lower() == 'unknown')):
        hysteresis_uncertainty_keywords_list = None
    else:
        temp_string = str(df_row["Hysteresis Uncertainty Keywords"])
        hysteresis_uncertainty_keywords_list = temp_string.split(';')
        del temp_string

    hysteresis_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/SensorCapability/HysteresisUncertainty"],
                                name="hysteresis uncertainty",
                                seeAlso=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                         URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                                conformsTo=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                            URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                                description="The hysteresis uncertainty of the linear transfer function of a sensor.",
                                value=hysteresis_uncertainty_value,
                                unit=hysteresis_uncertainty_unit,
                                comment=hysteresis_uncertainty_comment,
                                keywords_list=hysteresis_uncertainty_keywords_list)

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

    print(f'#### Sensor {sensor.identifier}')
    print(data.g.serialize(destination=rdfpath + "rdf.json", format="json-ld", auto_compact=True))
    print(data.g.serialize(destination=rdfpath + "rdf.ttl", base=SENSOR, format="longturtle"))
    print(data.g.serialize(destination=rdfpath + "rdf.xml", base=SENSOR, format="xml"))



def run_script(sensor_table_path: [Path, str], generated_files_directory_path: [Path, str]):
    SUPPORTED_SENSOR_TABLE_SHEET_NAMES = ["Druck",
                                          "Kraft",
                                          "Temperatur",
                                          "Weg",
                                          "Leistung",
                                          "Volumenstrom"]


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

