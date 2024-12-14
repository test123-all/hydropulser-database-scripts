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

from . import gitlab_db_mdgen

SCHEMA = Namespace("https://schema.org/")
FST_NAMESPACE= Namespace("https://w3id.org/fst/resource/")

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
             "µV": UNIT.MicroV,
             "A": UNIT.A,
             "%": UNIT.PERCENT,
             "m^3/s": UNIT['M3-PER-SEC'],
             "m": UNIT.M,
             "Pa": UNIT.PA}


def generate_valve_files(valve_files_dir, df_row):
    data = Kraken()
    data.g.bind("fst", FST_NAMESPACE)

    valve_id = df_row['uuid']

    maintainer = df_row['Verantwortlicher WiMi']
    # TODO:
    #meas_tech = # df_row["Messprinzip"]
    #modified = #df_row["letzte Prüfung/ Kalibration"]
    #rel = #df_row["Zubehör"]

    # the VALVE
    valve = Sensor(data, hasSensorCapability=FST_NAMESPACE[valve_id + "/SensorCapability"],
                    iri=FST_NAMESPACE[valve_id], identifier=valve_id, name=df_row['Bezeichnung'],
                    comment='', owner="FST", manufacturer=df_row['Hersteller'],
                    serialNumber=df_row['Seriennummer'], location=df_row['Aufbewahrungsort'])

    # data.g.add((valve.iri, DCTERMS.identifier, Literal('0811404601')))
    data.g.add((valve.iri, DBO.maintainedBy, Literal(maintainer)))
    # data.g.add((valve.iri, SDO.keywords, Literal(sheet_name)))
    # data.g.add((valve.iri, DCTERMS.modified, Literal(modified)))
    # if val_ref is not None:
    #     # data.g.add((valve.iri, SDO.keywords, Literal(val_ref)))
    # if meas_tech is not None:
    #     data.g.add((valve.iri, SDO.keywords, Literal(meas_tech)))
    data.g.add((valve.iri, SDO.keywords, Literal('Valve')))
    # if rel is not None:
    #     data.g.add((valve.iri, DCTERMS.relation, Literal(rel)))

    # properties
    sensor_sys_capa = SensorCapability(data, iri=FST_NAMESPACE[valve_id + "/SensorCapability"], name="sensor capabilities",
                                comment="sensor capabilities not regarding any conditions at this time")

    sensor_meas_range = Quantity(data, isPropertyOf=sensor_sys_capa.iri, hasQuantityKind=QUANTITYKIND.OpeningRatio,
                          minValue=Literal(float(df_row['Sensor Messbereich von']), datatype=XSD.double), maxValue=Literal(float(df_row['Sensor Messbereich bis']), datatype=XSD.double), unit=unit_dict[df_row['Sensor Messbereich Unit']],
                          iri=FST_NAMESPACE[valve_id + "/SensorCapability/MeasurementRange"], identifier=None, name="sensor measurement range",
                          rdftype=SSN_SYSTEM.MeasurementRange)

    # if val_ref is not None:
    #     data.g.add((sensor_meas_range.iri, SDO.valueReference, Literal(val_ref)))

    # TODO: FIXME: If there should be a unit that also contains 'A' or 'V' for example 'V/m' this delivers the wrong
    #  quantitykind. This would be solveable through code that lookups the quantitkind through a ontology.
    #  Since the qudt unit ontology doesn't contain all possible units it needs to be extended but might be a good
    #  starting point. -> the same to-do exists in the pump files.
    if (isinstance( df_row['Sensor Ausgabebereich Unit'],str)
                and 'V' in df_row['Sensor Ausgabebereich Unit']):
        sensor_actuation_range_quantitikind = QUANTITYKIND.Voltage
    elif (isinstance(df_row['Sensor Ausgabebereich Unit'] ,str)
                and 'A' in df_row['Sensor Ausgabebereich Unit']):
        sensor_actuation_range_quantitikind = QUANTITYKIND.ElectricCurrent
    else:
        raise Exception(f"Unit {df_row['Sensor Ausgabebereich Unit']} Quantitykind is not supported yet! Please contact the maintainers.")

    sensor_actuation_range = Quantity(data, isPropertyOf=sensor_sys_capa.iri, hasQuantityKind=sensor_actuation_range_quantitikind,
                                      minValue=Literal(float(df_row['Sensor Ausgabebereich von']), datatype=XSD.double), maxValue=Literal(float(df_row['Sensor Ausgabebereich bis']), datatype=XSD.double),
                                      unit=unit_dict[df_row['Sensor Ausgabebereich Unit']],
                                      iri=FST_NAMESPACE[valve_id + "/SensorCapability" + "/ActuationRange"], identifier=None, name="sensor output range",
                                      rdftype=SSN_SYSTEM.ActuationRange)

    sensor_sensitivity = Property(data, isPropertyOf=sensor_sys_capa.iri, iri=FST_NAMESPACE[valve_id + "/SensorCapability" + "/Sensitivity"],
                           comment="gain", rdftype=SSN_SYSTEM.Sensitivity, name="sensor sensitivity", value=Literal(df_row['Kennlinie Steigung _ Sensitivity']))
    data.g.add((FST_NAMESPACE[valve_id + "/SensorCapability" + "/Sensitivity"], QUDT.unit, Literal(f"({df_row['Sensor Messbereich Unit']})/({df_row['Sensor Ausgabebereich Unit']})")))


    sensor_bias = Property(data, isPropertyOf=sensor_sys_capa.iri, iri=FST_NAMESPACE[valve_id + "/SensorCapability" + "/Bias"],
                    comment="offset", rdftype=SSN_SYSTEM.SystemProperty, name="sensor bias",
                    value=Literal(float(df_row['Kennlinie Offset _ Bias']), datatype=XSD.double))

    data.g.add((FST_NAMESPACE[valve_id + "/SensorCapability" + "/Bias"], QUDT.unit, unit_dict[df_row['Sensor Messbereich Unit']]))

    if (df_row["absolute Bias Uncertainty Unit"] is not None
            and df_row["absolute Bias Uncertainty Unit"] in unit_dict.keys()):
        absolute_bias_uncertainty_unit = unit_dict[df_row["absolute Bias Uncertainty Unit"]]
    elif (df_row["absolute Bias Uncertainty Unit"] is None
          or (isinstance(df_row["absolute Bias Uncertainty"], str)
              and df_row["absolute Bias Uncertainty"].lower() == 'unknown')):
        absolute_bias_uncertainty_unit = None
    elif (df_row["absolute Bias Uncertainty Unit"] is not None
          and df_row["absolute Bias Uncertainty Unit"] not in unit_dict.keys()):
        absolute_bias_uncertainty_unit = df_row["absolute Bias Uncertainty Unit"]

    if (df_row["absolute Bias Uncertainty"] is None
            or (isinstance(df_row["absolute Bias Uncertainty"], str)
                and df_row["absolute Bias Uncertainty"].lower() == 'unknown')):
        absolute_bias_uncertainty_value = None
    else:
        absolute_bias_uncertainty_value = Literal(str(df_row["absolute Bias Uncertainty"]), datatype=XSD.double)

    if (df_row["absolute Bias Uncertainty Comment"] is None
            or (isinstance(df_row["absolute Bias Uncertainty Comment"], str)
                and df_row["absolute Bias Uncertainty Comment"].lower() == 'unknown')):
        absolute_bias_uncertainty_comment = None
    else:
        absolute_bias_uncertainty_comment = Literal(str(df_row["absolute Bias Uncertainty Comment"]))

    if (df_row["absolute Bias Uncertainty Keywords"] is None
            or (isinstance(df_row["absolute Bias Uncertainty Keywords"], str)
                and df_row["absolute Bias Uncertainty Keywords"].lower() == 'unknown')):
        absolute_bias_uncertainty_keywords_list = None
    else:
        temp_string = str(df_row["absolute Bias Uncertainty Keywords"])
        absolute_bias_uncertainty_keywords_list = temp_string.split(';')
        del temp_string

    absolute_bias_uncertainty = Property(data, isPropertyOf=sensor_bias.iri, iri=URIRef(f"{FST_NAMESPACE}{valve_id}/SensorCapability/Bias/AbsoluteBiasUncertainty"),
                                name="bias uncertainty",
                                description="The bias uncertainty of the sensor of the linear transfer function of a sensor.",
                                seeAlso=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                         URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                                conformsTo=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                            URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                                value=absolute_bias_uncertainty_value,
                                unit=absolute_bias_uncertainty_unit,
                                comment=absolute_bias_uncertainty_comment,
                                keywords_list=absolute_bias_uncertainty_keywords_list)

    # Relative uncertainty.
    if (df_row["relative Bias Uncertainty Unit"] is not None
            and df_row["relative Bias Uncertainty Unit"] in unit_dict.keys()):
        realtive_bias_uncertainty_unit = unit_dict[df_row["relative Bias Uncertainty Unit"]]
    elif (df_row["relative Bias Uncertainty Unit"] is None
          or (isinstance(df_row["relative Bias Uncertainty"], str)
              and df_row["relative Bias Uncertainty"].lower() == 'unknown')):
        relative_bias_uncertainty_unit = None
    elif (df_row["relative Bias Uncertainty Unit"] is not None
          and df_row["relative Bias Uncertainty Unit"] not in unit_dict.keys()):
        relative_bias_uncertainty_unit = df_row["relative Bias Uncertainty Unit"]

    if (df_row["relative Bias Uncertainty"] is None
            or (isinstance(df_row["relative Bias Uncertainty"], str)
                and df_row["relative Bias Uncertainty"].lower() == 'unknown')):
        relative_bias_uncertainty_value = None
    else:
        relative_bias_uncertainty_value = Literal(str(df_row["relative Bias Uncertainty"]), datatype=XSD.double)

    if (df_row["relative Bias Uncertainty Comment"] is None
            or (isinstance(df_row["relative Bias Uncertainty Comment"], str)
                and df_row["relative Bias Uncertainty Comment"].lower() == 'unknown')):
        relative_bias_uncertainty_comment = None
    else:
        relative_bias_uncertainty_comment = Literal(str(df_row["relative Bias Uncertainty Comment"]))

    if (df_row["relative Bias Uncertainty Keywords"] is None
            or (isinstance(df_row["relative Bias Uncertainty Keywords"], str)
                and df_row["relative Bias Uncertainty Keywords"].lower() == 'unknown')):
        relative_bias_uncertainty_keywords_list = None
    else:
        temp_string = str(df_row["relative Bias Uncertainty Keywords"])
        relative_bias_uncertainty_keywords_list = temp_string.split(';')
        del temp_string

    relative_bias_uncertainty = Property(data, isPropertyOf=sensor_bias.iri, iri=URIRef(f"{FST_NAMESPACE}{valve_id}/SensorCapability/Bias/RelativeBiasUncertainty"),
                                name="bias uncertainty",
                                description="The bias uncertainty of the sensor of the linear transfer function of a sensor.",
                                seeAlso=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                         URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                                conformsTo=[URIRef("https://doi.org/10.1007/978-3-030-78354-9"),
                                            URIRef("https://dx.doi.org/10.2139/ssrn.4452038")],
                                value=relative_bias_uncertainty_value,
                                unit=relative_bias_uncertainty_unit,
                                comment=relative_bias_uncertainty_comment,
                                keywords_list=relative_bias_uncertainty_keywords_list)

    # if df_row["Sensitivity Uncertainty Unit"] in unit_dict.keys():
    #     sensitivity_uncertainty_unit = unit_dict[df_row["Sensitivity Uncertainty Unit"]]
    # else:
    #     sensitivity_uncertainty_unit = df_row["Sensitivity Uncertainty Unit"]
    #
    # if df_row["Sensitivity Uncertainty Unit"] is None:
    #     sensitivity_uncertainty_value = None
    # else:
    #     sensitivity_uncertainty_value = Literal(str(df_row["Sensitivity Uncertainty"]), datatype=XSD.double)
    # sensitivity_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=FST_NAMESPACE[valve_id + "/SensitivityUncertainty"],
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
    # linearity_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=FST_NAMESPACE[valve_id + "/LinearityUncertainty"],
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
    # hysteresis_uncertainty = Property(data, isPropertyOf=sys_capa.iri, iri=FST_NAMESPACE[valve_id + "/HysteresisUncertainty"],
    #                             name="hysteresis uncertainty", seeAlso=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"), conformsTo=URIRef("https://dx.doi.org/10.2139/ssrn.4452038"),
    #                             description="The hysteresis uncertainty of the linear transfer function of a sensor.",
    #                             value=hysteresis_uncertainty_value,
    #                             unit=hysteresis_uncertainty_unit)

    ventil = rdflib.URIRef(f'{FST_NAMESPACE}{valve_id}')
    data.g.add((ventil, RDF.type, SOSA.Actuator))
    actuator_capability_iri = rdflib.URIRef(f"{valve.iri}/ActuatorCapability")
    data.g.add((valve.iri, SSN_SYSTEM.hasSystemCapability, actuator_capability_iri))

    data.g.add((actuator_capability_iri, RDF.type, SSN.Property))
    data.g.add((actuator_capability_iri, RDF.type, SSN_SYSTEM.SystemCapability))

    data.g.add((actuator_capability_iri, SCHEMA.name, Literal('actuator capabilities')))
    data.g.add((actuator_capability_iri, RDFS.comment, Literal('actuator capabilities not regarding any conditions at this time')))

    k_vs_iri = rdflib.URIRef(f"{valve.iri}/K_vs")

    if (df_row['K_vs Wert'] is None
            or (isinstance(df_row['K_vs Wert'], str)
            and df_row['K_vs Wert'].lower() == 'unknown')):
        K_vs_value = Literal('')
        K_vs_unit = Literal('')
    else:
        K_vs_value = Literal(df_row['K_vs Wert'], datatype=XSD.double)
        K_vs_unit = URIRef(unit_dict[df_row['K_vs Wert Einheit']])

    data.g.add((valve.iri, SSN.hasProperty, k_vs_iri ))
    data.g.add((k_vs_iri , RDF.type, SSN.Property))
    data.g.add((k_vs_iri , RDF.type, QUDT.Quantity))
    data.g.add((k_vs_iri, SCHEMA.name, Literal('K_vs value')))
    # data.g.add((k_vs_iri , RDFS.label, Literal('K_vs value')))
    data.g.add((k_vs_iri , RDFS.comment, Literal(df_row['K_vs Wert Comment'])))
    data.g.add((k_vs_iri , QUDT.hasQuantityKind, QUANTITYKIND.VolumeFlowRate))
    data.g.add((k_vs_iri , QUDT.symbol, Literal('K_vs')))
    data.g.add((k_vs_iri , QUDT.value, K_vs_value))
    data.g.add((k_vs_iri , QUDT.unit, K_vs_unit))
    data.g.add((k_vs_iri , SSN.isPropertyOf, valve.iri))
    # Gibt für die Genaugikeit eine angabe, die ist aber in Prozent und nicht fest
    # data.g.add((k_vs_iri , SSN_SYSTEM.Accuracy, Literal()))

    p_max_iri = rdflib.URIRef(f"{valve.iri}/p_max")
    data.g.add((valve.iri, SSN.hasProperty, p_max_iri))
    data.g.add((p_max_iri, RDF.type, SSN.Property))
    data.g.add((p_max_iri, RDF.type, QUDT.Quantity))
    data.g.add((p_max_iri, SCHEMA.name, Literal('maximum pressure')))
    # data.g.add((p_max_iri, RDFS.label, Literal('maximum pressure')))
    data.g.add((p_max_iri, RDFS.comment, Literal('')))
    data.g.add((p_max_iri, QUDT.hasQuantityKind, QUANTITYKIND.Pressure))
    data.g.add((p_max_iri, QUDT.symbol, Literal('p_max')))
    data.g.add((p_max_iri, QUDT.value, Literal(float(df_row['maximaler Druck Wert']), datatype=XSD.double)))
    data.g.add((p_max_iri, QUDT.unit, unit_dict[df_row['maximaler Druck Einheit']]))
    data.g.add((p_max_iri, SSN.isPropertyOf, valve.iri))

    actuator_actuation_range_iri = rdflib.URIRef(f'{valve.iri}/ActuatorCapability/ActuationRange')
    data.g.add((actuator_capability_iri, SSN.hasProperty, actuator_actuation_range_iri))
    data.g.add((actuator_actuation_range_iri, RDF.type, SSN.Property))
    data.g.add((actuator_actuation_range_iri, RDF.type, SSN_SYSTEM.ActuationRange))
    data.g.add((actuator_actuation_range_iri, RDF.type, QUDT.Quantity))
    data.g.add((actuator_actuation_range_iri, SCHEMA.name, Literal('actuator actuation range')))
    # data.g.add((actuator_actuation_range_iri, RDFS.label, Literal('actuator actuation range')))
    data.g.add((actuator_actuation_range_iri, RDFS.comment, Literal('The possible actuation range of the valve in percent')))
    data.g.add((actuator_actuation_range_iri, QUDT.hasQuantityKind, QUANTITYKIND.OpeningRatio))
    # data.g.add((actuator_actuation_range_iri, QUDT.symbol, Literal('(K_v/K_vs) * 100%')))
    data.g.add((actuator_actuation_range_iri, SCHEMA.minValue, Literal(float(df_row['Actuator Actuation Range from']), datatype=XSD.double)))
    data.g.add((actuator_actuation_range_iri, SCHEMA.maxValue, Literal(float(df_row['Actuator Actuation Range to']), datatype=XSD.double)))
    data.g.add((actuator_actuation_range_iri, QUDT.unit, unit_dict[df_row['Actuator Actuation Range unit']])) # UNIT.PERCENT))
    data.g.add((actuator_actuation_range_iri, SSN.isPropertyOf, actuator_capability_iri))


    actuator_input_iri = rdflib.URIRef(f'{valve.iri}/ActuatorCapability/InputRange')
    data.g.add((actuator_capability_iri, SSN.hasProperty, actuator_input_iri))
    data.g.add((actuator_input_iri, RDF.type, SSN.Property))
    data.g.add((actuator_input_iri, RDF.type, QUDT.Quantity))
    data.g.add((actuator_input_iri, SCHEMA.name, Literal('actuator input range')))
    # data.g.add((actuator_input_iri, RDFS.label, Literal('actuator input range')))

    # TODO: FIXME: If there should be a unit that also contains 'A' or 'V' for example 'V/m' this delivers the wrong
    #  quantitykind. This would be solveable through code that lookups the quantitkind through a ontology.
    #  Since the qudt unit ontology doesn't contain all possible units it needs to be extended but might be a good
    #  starting point. -> the same to-do exists in the valve files.
    if (isinstance(df_row['Actuator Input Range unit'], str)
            and 'V' in df_row['Actuator Input Range unit']):
        data.g.add((actuator_input_iri, QUDT.symbol, Literal('U_E')))
        actuator_input_range_quantitiykind = QUANTITYKIND.Voltage
    elif (isinstance(df_row['Actuator Input Range unit'], str)
          and 'A' in df_row['Actuator Input Range unit']):
        actuator_input_range_quantitiykind = QUANTITYKIND.ElectricCurrent
    else:
        raise Exception(
            f"Unit {df_row['Actuator Input Range unit']} Quantitykind is not supported yet! Please contact the maintainers.")

    data.g.add((actuator_input_iri, RDFS.comment, Literal('The possible actuator input range of the valve that causes the actuation.')))
    data.g.add((actuator_input_iri, QUDT.hasQuantityKind, actuator_input_range_quantitiykind))
    data.g.add((actuator_input_iri, SCHEMA.minValue, Literal(float(df_row['Actuator Input Range from']), datatype=XSD.double)))
    data.g.add((actuator_input_iri, SCHEMA.maxValue, Literal(float(df_row['Actuator Input Range to']), datatype=XSD.double)))
    data.g.add((actuator_input_iri, QUDT.unit, unit_dict[df_row['Actuator Input Range unit']]))
    data.g.add((actuator_input_iri, SSN.isPropertyOf, actuator_capability_iri))

    actuator_sensitivity = Property(data, isPropertyOf=actuator_capability_iri,
                                  iri=FST_NAMESPACE[valve_id + "/ActuatorCapability" + "/Sensitivity"],
                                  comment="gain", rdftype=SSN_SYSTEM.Sensitivity, name="actuator sensitivity",
                                  value=Literal(df_row['Actuator Kennlinie _ Sensitivity']))
    data.g.add((FST_NAMESPACE[valve_id + "/ActuatorCapability" + "/Sensitivity"], QUDT.unit,
                Literal(f"({df_row['Actuator Input Range unit']})/({df_row['Actuator Actuation Range unit']})")))

    actuator_bias = Property(data, isPropertyOf=actuator_capability_iri,
                           iri=FST_NAMESPACE[valve_id + "/ActuatorCapability" + "/Bias"],
                           comment="offset", rdftype=SSN_SYSTEM.SystemProperty, name="actuator bias",
                           value=Literal(float(df_row['Actuator Kennlinie _ Bias']), datatype=XSD.double))

    data.g.add((FST_NAMESPACE[valve_id + "/ActuatorCapability" + "/Bias"], QUDT.unit, unit_dict[df_row['Actuator Input Range unit']]))

    if (df_row['Nenndurchmesser'] is None
            or (isinstance(df_row['Nenndurchmesser'], str)
            and df_row['Nenndurchmesser'].lower() == 'unknown')):
        nominal_diameter_value = Literal('')
        nominal_diameter_unit = Literal('')
    else:
        nominal_diameter_value = Literal(df_row['Nenndurchmesser'], datatype=XSD.double)
        nominal_diameter_unit = URIRef(unit_dict[df_row['Nenndurchmesser Einheit']])

    nominal_diameter_iri = rdflib.URIRef(f'{valve.iri}/NominalDiameter')
    data.g.add((valve.iri, SSN.hasProperty, nominal_diameter_iri))
    data.g.add((nominal_diameter_iri, RDF.type, SSN.Property))
    data.g.add((nominal_diameter_iri, RDF.type, QUDT.Quantity))
    data.g.add((nominal_diameter_iri, SCHEMA.name, Literal('nominal diameter')))
    # data.g.add((nominal_diameter_iri, RDFS.label, Literal('nominal diameter')))
    # data.g.add((nominal_diameter_iri, RDFS.comment,
    #             Literal('The possible actuator input range of the valve that causes the actuation.')))
    data.g.add((nominal_diameter_iri, QUDT.hasQuantityKind, QUANTITYKIND.Diameter))
    data.g.add((nominal_diameter_iri, QUDT.symbol, Literal('DN')))
    data.g.add((nominal_diameter_iri, QUDT.value, nominal_diameter_value))
    data.g.add((nominal_diameter_iri, QUDT.unit, nominal_diameter_unit))
    data.g.add((nominal_diameter_iri, SSN.isPropertyOf, valve.iri))

    ############
    # Documentation
    # img = FST_NAMESPACE[valve_id + "/img/IMG_ventil_Bosch-Rexroth_R927000555.jpg"]
    #
    # data.g.add((ventil, SDO.subjectOf, img))
    # data.g.add((ventil, SDO.image, img))

    # datasheet = FST_NAMESPACE[valve_id + "/doc/datenblatt_101000_Bosch-Rexroth_Ventil_Type_4WRPEH6_4-4Wege.pdf"]
    # data.g.add((ventil, SDO.subjectOf, datasheet))
    # data.g.add((ventil, SDO.documentation, datasheet))


    ############
    # We got all info we want > make dirs if they don't exist

    rdfpath = str(valve_files_dir) + '/' + valve_id + "/"

    docpath = rdfpath + "docs"
    imgpath = rdfpath + "img"
    Path(docpath).mkdir(parents=True, exist_ok=True)
    Path(imgpath).mkdir(parents=True, exist_ok=True)

    # documentation
    with os.scandir(imgpath) as it:
        for entry in it:
            if entry.name.lower().endswith((".png", ".jpg", "jpeg")) and entry.is_file():
                img = URIRef("img/" + quote(entry.name))
                valve.subjectOf = img
                valve.image = img

    docs = URIRef("docs/")
    valve.subjectOf = docs
    valve.documentation = docs

    with os.scandir(docpath) as it:
        for entry in it:
            if entry.is_file():
                datasheet = URIRef("docs/" + quote(entry.name))
                valve.subjectOf = datasheet
                valve.documentation = datasheet

    # rdf doc references
    docttl = FST_NAMESPACE[valve_id + "/rdf.ttl"]
    data.g.add((docttl, RDF.type, FOAF.Document))  # schema:CreativeWork
    data.g.add((docttl, FOAF.primaryTopic, valve.iri))  # schema:about

    docxml = FST_NAMESPACE[valve_id + "/rdf.xml"]
    data.g.add((docxml, RDF.type, FOAF.Document))
    data.g.add((docxml, FOAF.primaryTopic, valve.iri))

    docjson = FST_NAMESPACE[valve_id + "/rdf.json"]
    data.g.add((docjson, RDF.type, FOAF.Document))
    data.g.add((docjson, FOAF.primaryTopic, valve.iri))

    print(data.g.serialize(destination=rdfpath + "rdf.json", format="json-ld", auto_compact=True))
    print(data.g.serialize(destination=rdfpath + "rdf.ttl", base=FST_NAMESPACE, format="longturtle"))
    print(data.g.serialize(destination=rdfpath + "rdf.xml", base=FST_NAMESPACE, format="xml"))


