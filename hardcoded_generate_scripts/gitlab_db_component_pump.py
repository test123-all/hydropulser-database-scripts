import os
from pathlib import Path
from urllib.parse import quote

import rdflib
from rdflib import Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, FOAF, SOSA, DCTERMS, XSD, SSN, DCMITYPE
import pandas as pd
import numpy as np

from pyKRAKEN.kraken import (
    SDO,
    DBO,
    UNIT,
    QUDT,
    QUANTITYKIND,
    SSN_SYSTEM,
    Kraken,
    Sensor,
    SensorCapability,
    Property,
    Quantity
)

from . import gitlab_db_mdgen


SCHEMA = Namespace("https://schema.org/")
FST_NAMESPACE = Namespace("https://w3id.org/fst/resource/")

unit_dict = {"bar": UNIT.BAR,
             "mbar": UNIT.MilliBAR,
             "psi": UNIT.PSI,
             "kPa": UNIT.KiloPA,
             "MPa": UNIT.MegaPA,
             "Pa": UNIT.PA,
             "°C": UNIT.DEG_C,
             "K": UNIT.K,
             "N": UNIT.N,
             "kN": UNIT.KiloN,
             "mm": UNIT.MilliM,
             "cm": UNIT.CentiM,
             "V": UNIT.V,
             "mV": UNIT.MilliV,
             "µV": UNIT.MicroV,
             "1/s": UNIT.REV_PER_SEC,
             "W": UNIT.W,
             "A": UNIT.A}


COMPONENT = Namespace("https://w3id.org/fst/resource/")
SUBSTANCE = Namespace("https://w3id.org/fst/resource/")

def generate_pump_files(pump_files_dir, df_row):
    data = Kraken(base=COMPONENT)
    # data.g.bind("fst-component", COMPONENT)
    # data.g.bind("fst-substance", SUBSTANCE)
    data.g.bind("fst", COMPONENT)

    pump_id = df_row['uuid']  # str(uuid6())

    # The component = the air spring

    pump = rdflib.URIRef(f'{FST_NAMESPACE}{pump_id}')
    data.g.add((pump, RDF.type, DCMITYPE.PhysicalObject))
    data.g.add((pump, RDF.type, SOSA.Actuator))
    data.g.add((pump, RDFS.label, Literal("Pump")))
    data.g.add((pump, DCTERMS.identifier, Literal(pump_id)))
    data.g.add((pump, DCTERMS.identifier, Literal(f"{df_row['Bezeichnung']}")))
    data.g.add((pump, DBO.owner, Literal("FST")))
    data.g.add((pump, SDO.manufacturer, Literal(f"{df_row['Hersteller']}")))
    data.g.add((pump, SDO.serialNumber, Literal(f"{df_row['Seriennummer']}")))

    actuator_capability_iri = rdflib.URIRef(f"{pump}/ActuatorCapability")
    data.g.add((pump, SSN_SYSTEM.hasSystemCapability, actuator_capability_iri))
    data.g.add((actuator_capability_iri, RDF.type, SSN.Property))
    data.g.add((actuator_capability_iri, RDF.type, SSN_SYSTEM.SystemCapability))
    data.g.add((actuator_capability_iri, SCHEMA.name, Literal('actuator capabilities')))
    data.g.add((actuator_capability_iri, RDFS.comment,
                Literal('actuator capabilities not regarding any conditions at this time')))

    if df_row['Ausgabebereich Einheit'] == '1/s':
        actuator_actuation_range_iri = rdflib.URIRef(f'{pump}/ActuationRange')
        data.g.add((actuator_capability_iri, SSN.hasProperty, actuator_actuation_range_iri))
        data.g.add((actuator_actuation_range_iri, RDF.type, SSN.Property))
        data.g.add((actuator_actuation_range_iri, RDF.type, SSN_SYSTEM.ActuationRange))
        data.g.add((actuator_actuation_range_iri, RDF.type, QUDT.Quantity))
        data.g.add((actuator_actuation_range_iri, RDFS.label, Literal('actuation range')))
        data.g.add((actuator_actuation_range_iri, RDFS.comment, Literal('The possible actuation range (rate of rotation) of the pump in 1/s')))
        data.g.add((actuator_actuation_range_iri, QUDT.hasQuantityKind, QUANTITYKIND.AngularVelocity))
        data.g.add((actuator_actuation_range_iri, QUDT.symbol, Literal('ω')))
        data.g.add((actuator_actuation_range_iri, SCHEMA.minValue, Literal(float(df_row['Ausgabebereich von']), datatype=XSD.double)))
        data.g.add((actuator_actuation_range_iri, SCHEMA.maxValue, Literal(float(df_row['Ausgabebereich bis']), datatype=XSD.double)))
        data.g.add((actuator_actuation_range_iri, QUDT.unit, unit_dict[f"{df_row['Ausgabebereich Einheit']}"]))
        data.g.add((actuator_actuation_range_iri, SSN.isPropertyOf, actuator_capability_iri))
    else:
        raise Exception(f"Unit {df_row['Ausgabebereich Einheit']} is not supported yet! Please contact the maintainers.")

    actuator_input_voltage_iri = rdflib.URIRef(f'{pump}/ActuatorInputVoltageRange')
    data.g.add((actuator_capability_iri, SSN.hasProperty, actuator_input_voltage_iri))
    data.g.add((actuator_input_voltage_iri, RDF.type, SSN.Property))
    data.g.add((actuator_input_voltage_iri, RDF.type, QUDT.Quantity))
    data.g.add((actuator_input_voltage_iri, RDFS.label, Literal('actuator input voltage range')))
    data.g.add((actuator_input_voltage_iri, RDFS.comment, Literal('The possible actuator input voltage range of the pump that causes the actuation.')))
    data.g.add((actuator_input_voltage_iri, QUDT.hasQuantityKind, QUANTITYKIND.Voltage))
    data.g.add((actuator_input_voltage_iri, QUDT.symbol, Literal('U_E')))
    data.g.add((actuator_input_voltage_iri, SCHEMA.minValue, Literal(float(df_row['Eingabebereich von']), datatype=XSD.double)))
    data.g.add((actuator_input_voltage_iri, SCHEMA.maxValue, Literal(float(df_row['Eingabebereich bis']), datatype=XSD.double)))
    data.g.add((actuator_input_voltage_iri, QUDT.unit, unit_dict[f"{df_row['Eingabebereich Einheit']}"]))
    data.g.add((actuator_input_voltage_iri, SSN.isPropertyOf, actuator_capability_iri))

    # // new
    # properties
    rated_power = COMPONENT[pump_id + "/P_N"]
    data.g.add((pump, SSN.hasProperty, rated_power))
    data.g.add((rated_power, RDF.type, SSN.Property))
    data.g.add((rated_power, RDF.type, QUDT.Quantity))
    data.g.add((rated_power, RDFS.label, Literal("nominal/rated power"))) # TODO: add it in german Nennleistung
    data.g.add((rated_power, QUDT.symbol, Literal("P_N")))
    data.g.add((rated_power, QUDT.hasQuantityKind, QUANTITYKIND.Power))
    data.g.add((rated_power, QUDT.unit, unit_dict[f"{df_row['Motornennleistung Einheit']}"])) #TODO
    data.g.add((rated_power, QUDT.value, Literal(float(df_row['Motornennleistung']), datatype=XSD.double))) # TODO:
    data.g.add((rated_power, DCTERMS.description, Literal("The nominal/rated power of the pump.")))
    # data.g.add((rated_power, SSN_SYSTEM.Accuracy, Literal("2.352441913686447e-04", datatype=XSD.double)))
    # source: datasheet, Area derived from Force and pressure, uncertainty assumptions: F+-8N, p+-0.1bar
    # data.g.add((rated_power, RDFS.comment, Literal("negative direction")))

    input_power = COMPONENT[pump_id + "/P_in"] # TODO :RANGE!
    data.g.add((pump, SSN.hasProperty, input_power))
    data.g.add((input_power, RDF.type, SSN.Property))
    data.g.add((input_power, RDF.type, QUDT.Quantity))
    data.g.add((input_power, RDFS.label, Literal("input power"))) # Motoraufnahmeleistung
    data.g.add((input_power, QUDT.symbol, Literal("P_in")))
    data.g.add((input_power, QUDT.hasQuantityKind, QUANTITYKIND.Power))
    data.g.add((input_power, QUDT.unit, unit_dict[f"{df_row['Leistungsaufnahme Einheit']}"])) #TODO
    data.g.add((input_power, SCHEMA.minValue, Literal(float(df_row['Leistungsaufnahme von']), datatype=XSD.double)))  # TODO:
    data.g.add((input_power, SCHEMA.maxValue, Literal(float(df_row['Leistungsaufnahme bis']), datatype=XSD.double)))  # TODO:
    data.g.add((input_power, DCTERMS.description, Literal("The input power of the pump."))) # TODO:
    # data.g.add((input_power, SSN_SYSTEM.Accuracy, Literal("2.352441913686447e-04", datatype=XSD.double)))
    # source: datasheet, Area derived from Force and pressure, uncertainty assumptions: F+-8N, p+-0.1bar
    # data.g.add((input_power, RDFS.comment, Literal("negative direction")))

    current_demand = COMPONENT[pump_id + "/I_demand"]
    data.g.add((pump, SSN.hasProperty, current_demand))
    data.g.add((current_demand, RDF.type, SSN.Property))
    data.g.add((current_demand, RDF.type, QUDT.Quantity))
    data.g.add((current_demand, RDFS.label, Literal("Current demand")))  # Motoraufnahmeleistung
    data.g.add((current_demand, QUDT.symbol, Literal("I_demand")))
    data.g.add((current_demand, QUDT.hasQuantityKind, QUANTITYKIND.ElectricCurrent))
    data.g.add((current_demand, QUDT.unit, unit_dict[f"{df_row['Stromaufnahmebereich Einheit']}"]))  # TODO
    data.g.add((current_demand, SCHEMA.minValue, Literal(float(df_row['Stromaufnahmebereich von']), datatype=XSD.double)))  # TODO:
    data.g.add((current_demand, SCHEMA.maxValue, Literal(float(df_row['Stromaufnahmebereich bis']), datatype=XSD.double)))  # TODO:
    data.g.add((current_demand, DCTERMS.description, Literal("The electric current demand of the pump.")))  # TODO:
    # data.g.add((current_demand, SSN_SYSTEM.Accuracy, Literal("2.352441913686447e-04", datatype=XSD.double)))
    # source: datasheet, Area derived from Force and pressure, uncertainty assumptions: F+-8N, p+-0.1bar
    # data.g.add((current_demand, RDFS.comment, Literal("negative direction")))


    sensitivity = Property(data, isPropertyOf=actuator_actuation_range_iri, iri=URIRef(f"{FST_NAMESPACE}{pump_id}/Sensitivity"),
                           comment="gain", rdftype=SSN_SYSTEM.Sensitivity, name="sensitivity",
                           value=Literal(float(df_row['Kennlinie Steigung _ Sensitivity']), datatype=XSD.double))

    bias = Property(data, isPropertyOf=actuator_actuation_range_iri, iri=URIRef(f"{FST_NAMESPACE}{pump_id}/Bias"),
                    comment="offset", rdftype=SSN_SYSTEM.SystemProperty, name="bias",
                    value=Literal(float(df_row['Kennlinie Offset _ Bias']), datatype=XSD.double))


    power_connection = COMPONENT[pump_id + "/PowerConnection"]  # TODO :RANGE!
    data.g.add((pump, SSN.hasProperty, power_connection))
    data.g.add((power_connection, RDF.type, SSN.Property))
    data.g.add((power_connection, RDF.type, QUDT.Quantity))
    data.g.add((power_connection, RDFS.label, Literal("power connection")))  # Motoraufnahmeleistung
    # data.g.add((power_connection, QUDT.symbol, Literal("I_demand")))
    # data.g.add((power_connection, QUDT.hasQuantityKind, QUANTITYKIND.))
    # data.g.add((power_connection, QUDT.unit, UNIT.))  # TODO
    data.g.add((power_connection, QUDT.value, Literal(f"{df_row['Netzanschluss']}")))  # TODO:
    data.g.add((power_connection, DCTERMS.description, Literal("The power connection of the pump.")))  # TODO:
    # data.g.add((power_connection, SSN_SYSTEM.Accuracy, Literal("2.352441913686447e-04", datatype=XSD.double)))
    # source: datasheet, Area derived from Force and pressure, uncertainty assumptions: F+-8N, p+-0.1bar
    # data.g.add((power_connection, RDFS.comment, Literal("negative direction")))

    p_max_iri = rdflib.URIRef(f"{pump}/P_max")
    data.g.add((actuator_capability_iri, SSN.hasProperty, p_max_iri))
    data.g.add((p_max_iri, RDF.type, SSN.Property))
    data.g.add((p_max_iri, RDF.type, QUDT.Quantity))
    data.g.add((p_max_iri, RDFS.label, Literal('maximum pressure')))
    # data.g.add((p_max_iri, RDFS.comment, Literal('')))
    data.g.add((p_max_iri, QUDT.hasQuantityKind, QUANTITYKIND.Pressure))
    data.g.add((p_max_iri, QUDT.symbol, Literal('P_max')))
    data.g.add((p_max_iri, QUDT.value, Literal(float(df_row['maximaler Druck Wert']), datatype=XSD.double)))
    data.g.add((p_max_iri, QUDT.unit, unit_dict[f"{df_row['maximaler Druck Einheit']}"]))
    data.g.add((p_max_iri, SSN.isPropertyOf, actuator_capability_iri))


    # TODO: Bild
    # # documentation this can probably be automated
    # img = COMPONENT[pump_id + "/IMG_20190809_113156_Bokeh.jpg"]
    # data.g.add((pump, SDO.subjectOf, img))
    # data.g.add((pump, SDO.image, img))

    # docs = COMPONENT[pump_id + "/CAD"]
    # data.g.add((pump, SDO.subjectOf, docs))
    # data.g.add((pump, SDO.documentation, docs))
    #
    # datasheet = COMPONENT[pump_id + "/CAD/air_spring/HH-AR-0521-000_TB_ZB_LUFTFEDER_LH_RH_EA.pdf"]
    # data.g.add((pump, SDO.subjectOf, datasheet))
    # data.g.add((pump, SDO.documentation, datasheet))

    # rdf doc references
    docttl = COMPONENT[pump_id + "/rdf.ttl"]
    data.g.add((docttl, RDF.type, FOAF.Document))
    data.g.add((docttl, FOAF.primaryTopic, pump))

    docxml = COMPONENT[pump_id + "/rdf.xml"]
    data.g.add((docxml, RDF.type, FOAF.Document))
    data.g.add((docxml, FOAF.primaryTopic, pump))

    docjson = COMPONENT[pump_id + "/rdf.json"]
    data.g.add((docjson, RDF.type, FOAF.Document))
    data.g.add((docjson, FOAF.primaryTopic, pump))

    dir_path = Path(f"{pump_files_dir}/{pump_id}")
    try:
        dir_path.mkdir()
    except FileExistsError:
        pass

    temp_file_path = f"{pump_files_dir}/{pump_id}/rdf"
    print(data.g.serialize(destination=f"{temp_file_path}.json", format="json-ld", auto_compact=True))
    print(data.g.serialize(destination=f"{temp_file_path}.ttl", base=SUBSTANCE, format="longturtle", encoding="utf-8"))
    print(data.g.serialize(destination=f"{temp_file_path}.xml", base=SUBSTANCE, format="xml"))

    gitlab_db_mdgen.generate_sensor_md(str(dir_path))
