import os
from pathlib import Path
from urllib.parse import quote

import rdflib
from rdflib import Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, FOAF, SOSA, DCTERMS, XSD, SSN
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

SCHEMA = Namespace("https://schema.org/")
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


def main():
    data = Kraken()
    data.g.bind("fst", SENSOR)

    sensor_id = '018bb4b1-db51-77be-9ece-68f3222e0afa'

    maintainer = 'Rexer'
    #meas_tech = # df_row["Messprinzip"]
    #modified = #df_row["letzte Prüfung/ Kalibration"]
    #rel = #df_row["Zubehör"]

    # the VALVE
    sensor = Sensor(data, hasSensorCapability=SENSOR[sensor_id + "/SensorCapability"],
                    iri=SENSOR[sensor_id], identifier=sensor_id, name='4WRPEH 6 C3B12L -10/G24 K0/A1M',
                    comment='', owner="FST", manufacturer='Rexroth - Bosch Group',
                    serialNumber='R927000555', location='')

    data.g.add((sensor.iri, DCTERMS.identifier, '0811404601'))
    data.g.add((sensor.iri, DBO.maintainedBy, Literal(maintainer)))
    # data.g.add((sensor.iri, SDO.keywords, Literal(sheet_name)))
    # data.g.add((sensor.iri, DCTERMS.modified, Literal(modified)))
    # if val_ref is not None:
    #     # data.g.add((sensor.iri, SDO.keywords, Literal(val_ref)))
    # if meas_tech is not None:
    #     data.g.add((sensor.iri, SDO.keywords, Literal(meas_tech)))
    data.g.add((sensor.iri, SDO.keywords, Literal('Valve')))
    # if rel is not None:
    #     data.g.add((sensor.iri, DCTERMS.relation, Literal(rel)))

    # properties
    sys_capa = SensorCapability(data, iri=SENSOR[sensor_id + "/SensorCapability"], name="sensor capabilities",
                                comment="sensor capabilities not regarding any conditions at this time")

    meas_range = Quantity(data, isPropertyOf=sys_capa.iri, hasQuantityKind=QUANTITYKIND.VolumeFlowRate,
                          minValue=Literal(-100, datatype=XSD.double), maxValue=Literal(100, datatype=XSD.double), unit=UNIT.PERCENT,
                          iri=SENSOR[sensor_id + "/MeasurementRange"], identifier=None, name="measurement range",
                          rdftype=SSN_SYSTEM.MeasurementRange)

    # if val_ref is not None:
    #     data.g.add((meas_range.iri, SDO.valueReference, Literal(val_ref)))

    sensor_actuation_range = Quantity(data, isPropertyOf=sys_capa.iri, hasQuantityKind=QUANTITYKIND.Voltage,
                                      minValue=Literal(-10, datatype=XSD.double), maxValue=Literal(10, datatype=XSD.double),
                                      unit='Volt',
                                      iri=SENSOR[sensor_id + "/SensorActuationRange"], identifier=None, name="sensor output voltage range",
                                      rdftype=SSN_SYSTEM.ActuationRange)

    sensitivity = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/Sensitivity"],
                           comment="gain", rdftype=SSN_SYSTEM.Sensitivity, name="sensitivity", value=Literal(10, datatype=XSD.double))

    bias = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/Bias"],
                    comment="offset", rdftype=SSN_SYSTEM.SystemProperty, name="bias",
                    value=Literal(0, datatype=XSD.double))

    # if df_row["Bias Uncertainty Unit"] in unit_dict.keys():
    #     bias_uncertainty_unit = unit_dict[df_row["Bias Uncertainty Unit"]]
    # else:
    #     bias_uncertainty_unit = df_row["Bias Uncertainty Unit"]
    #
    # if df_row["Bias Uncertainty"] is None:
    #     bias_uncertainty_value = None
    # else:
    #     bias_uncertainty_value = Literal(str(df_row["Bias Uncertainty"]), datatype=XSD.double)
    # bias_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/BiasUncertainty"],
    #                 name="bias uncertainty",
    #                 description="The bias uncertainty of the sensor of the linear transfer function of a sensor.",
    #                 seeAlso=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"),
    #                 conformsTo=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"),
    #                 value=bias_uncertainty_value,
    #                 unit=bias_uncertainty_unit)
    #
    # if df_row["Sensitivity Uncertainty Unit"] in unit_dict.keys():
    #     sensitivity_uncertainty_unit = unit_dict[df_row["Sensitivity Uncertainty Unit"]]
    # else:
    #     sensitivity_uncertainty_unit = df_row["Sensitivity Uncertainty Unit"]
    #
    # if df_row["Sensitivity Uncertainty Unit"] is None:
    #     sensitivity_uncertainty_value = None
    # else:
    #     sensitivity_uncertainty_value = Literal(str(df_row["Sensitivity Uncertainty"]), datatype=XSD.double)
    # sensitivity_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/SensitivityUncertainty"],
    #                              description="The sensitivity uncertainty of the linear transfer function of a sensor.",
    #                              name="sensitivity uncertainty", seeAlso=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"), conformsTo=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"),
    #                              value=sensitivity_uncertainty_value,
    #                              unit=sensitivity_uncertainty_unit)
    #
    # if df_row["Linearity Uncertainty Unit"] in unit_dict.keys():
    #     linearity_uncertainty_unit = unit_dict[df_row["Linearity Uncertainty Unit"]]
    # else:
    #     linearity_uncertainty_unit = df_row["Linearity Uncertainty Unit"]
    #
    # if df_row["Linearity Uncertainty"] is None:
    #     linearity_uncertainty_value = None
    # else:
    #     linearity_uncertainty_value = Literal(str(df_row["Linearity Uncertainty"]), datatype=XSD.double)
    # linearity_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/LinearityUncertainty"],
    #                            name="linearity uncertainty", seeAlso=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"), conformsTo=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"),
    #                            description="The linearity uncertainty of the linear transfer function of a sensor.",
    #                            value=linearity_uncertainty_value,
    #                            unit=linearity_uncertainty_unit)
    #
    # if df_row["Hysteresis Uncertainty Unit"] in unit_dict.keys():
    #     hysteresis_uncertainty_unit = unit_dict[df_row["Hysteresis Uncertainty Unit"]]
    # else:
    #     hysteresis_uncertainty_unit = df_row["Hysteresis Uncertainty Unit"]
    #
    # if df_row["Hysteresis Uncertainty"] is None:
    #     hysteresis_uncertainty_value = None
    # else:
    #     hysteresis_uncertainty_value = Literal(str(df_row["Hysteresis Uncertainty"]), datatype=XSD.double)
    # hysteresis_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=SENSOR[sensor_id + "/HysteresisUncertainty"],
    #                             name="hysteresis uncertainty", seeAlso=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"), conformsTo=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"),
    #                             description="The hysteresis uncertainty of the linear transfer function of a sensor.",
    #                             value=hysteresis_uncertainty_value,
    #                             unit=hysteresis_uncertainty_unit)

    data.g.add((rdflib.URIRef(f'{SENSOR}{sensor_id}'), RDF.type, SOSA.Actuator))
    actuator_capability_iri = rdflib.URIRef(f"{sensor.iri}/ActuatorCapability")
    data.g.add((sensor.iri, SSN_SYSTEM.hasSystemCapability, actuator_capability_iri))

    data.g.add((actuator_capability_iri, RDF.type, SSN.Property))
    data.g.add((actuator_capability_iri, RDF.type, SSN_SYSTEM.SystemCapability))

    data.g.add((actuator_capability_iri, SCHEMA.name, Literal('actuator capabilities')))
    data.g.add((actuator_capability_iri, RDFS.comment, Literal('actuator capabilities not regarding any conditions at this time')))

    nominal_flow_iri = rdflib.URIRef(f"{sensor.iri}/NominalVolumeFlow")
    data.g.add((actuator_capability_iri, SSN.hasProperty, nominal_flow_iri))
    data.g.add((nominal_flow_iri, RDF.type, SSN.Property))
    data.g.add((nominal_flow_iri, RDF.type, QUDT.Quantity))
    data.g.add((nominal_flow_iri, RDFS.label, Literal('nominal volume flow')))
    data.g.add((nominal_flow_iri, RDFS.comment, Literal('nominal volume flow at Δp = 35bar. For a different Δp calculate flow with Q_x = Q_nominal * sqrt(Δpx/35)')))
    data.g.add((nominal_flow_iri, QUDT.hasQuantityKind, QUANTITYKIND.VolumeFlowRate))
    data.g.add((nominal_flow_iri, QUDT.symbol, Literal('Q_nominal')))
    data.g.add((nominal_flow_iri, QUDT.value, Literal(12, datatype=XSD.double)))
    data.g.add((nominal_flow_iri, QUDT.unit, UNIT.L_PER_MIN))
    data.g.add((nominal_flow_iri, SSN.isPropertyOf, actuator_capability_iri))
    # Gibt für die Genaugikeit eine angabe, die ist aber in Prozent und nicht fest
    # data.g.add((nominal_flow_iri, SSN_SYSTEM.Accuracy, Literal()))

    p_max_iri = rdflib.URIRef(f"{sensor.iri}/P_max")
    data.g.add((actuator_capability_iri, SSN.hasProperty, p_max_iri))
    data.g.add((p_max_iri, RDF.type, SSN.Property))
    data.g.add((p_max_iri, RDF.type, QUDT.Quantity))
    data.g.add((p_max_iri, RDFS.label, Literal('maximum pressure')))
    data.g.add((p_max_iri, RDFS.comment, Literal('')))
    data.g.add((p_max_iri, QUDT.hasQuantityKind, QUANTITYKIND.Pressure))
    data.g.add((p_max_iri, QUDT.symbol, Literal('P_max')))
    data.g.add((p_max_iri, QUDT.value, Literal(315, datatype=XSD.double)))
    data.g.add((p_max_iri, QUDT.unit, UNIT.BAR))
    data.g.add((p_max_iri, SSN.isPropertyOf, actuator_capability_iri))

    actuator_actuation_range_iri = rdflib.URIRef(f'{sensor.iri}/ActuatorActuationRange')
    data.g.add((actuator_capability_iri, SSN.hasProperty, actuator_actuation_range_iri))
    data.g.add((actuator_actuation_range_iri, RDF.type, SSN.Property))
    data.g.add((actuator_actuation_range_iri, RDF.type, SSN_SYSTEM.ActuationRange))
    data.g.add((actuator_actuation_range_iri, RDF.type, QUDT.Quantity))
    data.g.add((actuator_actuation_range_iri, RDFS.label, Literal('actuator actuation range')))
    data.g.add((actuator_actuation_range_iri, RDFS.comment, Literal('The possible actuation range of the valve in percent')))
    data.g.add((actuator_actuation_range_iri, QUDT.hasQuantityKind, QUANTITYKIND.VolumeFlowRate))
    data.g.add((actuator_actuation_range_iri, QUDT.symbol, Literal('Q')))
    data.g.add((actuator_actuation_range_iri, SCHEMA.minValue, Literal(-100, datatype=XSD.double)))
    data.g.add((actuator_actuation_range_iri, SCHEMA.maxValue, Literal(100, datatype=XSD.double)))
    data.g.add((actuator_actuation_range_iri, QUDT.unit, UNIT.PERCENT))
    data.g.add((actuator_actuation_range_iri, SSN.isPropertyOf, actuator_capability_iri))

    actuator_input_voltage_iri = rdflib.URIRef(f'{sensor.iri}/ActuatorInputVoltageRange')
    data.g.add((actuator_capability_iri, SSN.hasProperty, actuator_input_voltage_iri))
    data.g.add((actuator_input_voltage_iri, RDF.type, SSN.Property))
    data.g.add((actuator_input_voltage_iri, RDF.type, QUDT.Quantity))
    data.g.add((actuator_input_voltage_iri, RDFS.label, Literal('actuator input voltage range')))
    data.g.add((actuator_input_voltage_iri, RDFS.comment, Literal('The possible actuator input voltage range of the valve that causes the actuation.')))
    data.g.add((actuator_input_voltage_iri, QUDT.hasQuantityKind, QUANTITYKIND.Voltage))
    data.g.add((actuator_input_voltage_iri, QUDT.symbol, Literal('U_E')))
    data.g.add((actuator_input_voltage_iri, SCHEMA.minValue, Literal(-10, datatype=XSD.double)))
    data.g.add((actuator_input_voltage_iri, SCHEMA.maxValue, Literal(10, datatype=XSD.double)))
    data.g.add((actuator_input_voltage_iri, QUDT.unit, UNIT.V))
    data.g.add((actuator_input_voltage_iri, SSN.isPropertyOf, actuator_capability_iri))


    ############
    # We got all info we want > make dirs if they don't exist
    current_file_path = Path(__name__)
    rdfpath = str(current_file_path.parent.resolve()) + '/' + sensor_id + "/"

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

if __name__ == '__main__':
    main()
