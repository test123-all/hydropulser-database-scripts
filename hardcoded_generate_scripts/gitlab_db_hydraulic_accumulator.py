from pathlib import Path

from rdflib import Namespace, Literal, URIRef
from rdflib.namespace import DCAT, DCMITYPE, DCTERMS, RDF, RDFS, XSD, SSN, SDO, FOAF
from pyKRAKEN.kraken import (
    DBO,
    QUDT,
    UNIT,
    QUANTITYKIND,
    Kraken
)

# this should ideally be something like e.g.:
# https://fst.tu-darmstadt.de/namespaces/components/id/
# or w3id
# which redirects to e.g.
# https://fst.tu-darmstadt.de/namespaces/components/doc/
# which redirects to a webserver with static html generated by this, or just directly to
# ns_root = "https://git.rwth-aachen.de/fst-tuda/projects/rdm/datasheets-mockup/"
# FST = Namespace(ns_root + "-/blob/main/")
# COMPONENT = Namespace(FST["component/"])
# SUBSTANCE = Namespace(FST["substance/"])
schema = Namespace('https://schema.org/')

unit_dict = {"bar": UNIT.BAR,
             "mbar": UNIT.MilliBAR,
             "psi": UNIT.PSI,
             "kPa": UNIT.KiloPA,
             "MPa": UNIT.MegaPA,
             "°C": UNIT.DEG_C,
             "K": UNIT.K,
             "kN": UNIT.KiloN,
             "mm": UNIT.MilliM,
             "cm": UNIT.CentiM,
             "Liter": UNIT.L,
             "cm^3": UNIT.CentiM3,
             "dm^3": UNIT.DeciM3,
             "m^3": UNIT.M3}

def generate_gitlab_hydraulic_accumulator_files(save_to_dir: [str, Path],
                                   hydraulic_accumulator_id: str,
                                   identifier: str,
                                   manufacturer: str,
                                   serial_number: str,
                                   hydraulic_accumulator_manufacturing_date: str,
                                   hydraulic_accumulator_comment: str,
                                   operating_pressure_value: [int, float],
                                   operating_pressure_unit: str,
                                   maximum_pressure_value: [int, float],
                                   maximum_pressure_unit: str,
                                   volume_value: [int, float],
                                   volume_unit: str,
                                   volume_accuracy: [int, float],
                                   operating_temperature_range_minvalue: [int, float],
                                   operating_temperature_range_maxvalue: [int, float],
                                   operating_temperature_range_unit: str):


    SSN_SYSTEM = Namespace("https://www.w3.org/ns/ssn/systems/")
    COMPONENT = Namespace("https://w3id.org/fst/resource/")
    SUBSTANCE = Namespace("https://w3id.org/fst/resource/")

    data = Kraken(base=COMPONENT)
    # data.g.bind("fst-component", COMPONENT)
    # data.g.bind("fst-substance", SUBSTANCE)
    data.g.bind("fst", COMPONENT)

    #hydraulic_accumulator_id = "1ed6c2f8-282a-64b4-94d0-4ee51dfba10e"  # str(uuid6())
    # air_id = "1ed6cc2c-da26-661f-92f3-02c4bb63c743"

    # the component = the air spring
    hydraulic_accumulator = COMPONENT[hydraulic_accumulator_id]
    # air = SUBSTANCE[air_id]
    data.g.add((hydraulic_accumulator, RDF.type, DCMITYPE.PhysicalObject))
    # data.g.add((hydraulic_accumulator, DCTERMS.hasPart, air))
    data.g.add((hydraulic_accumulator, RDFS.label, Literal("hydraulic accumulator")))
    data.g.add((hydraulic_accumulator, DCTERMS.identifier, Literal(hydraulic_accumulator_id)))
    data.g.add((hydraulic_accumulator, DCTERMS.identifier, Literal(identifier)))
    data.g.add((hydraulic_accumulator, DBO.owner, Literal("FST")))
    data.g.add((hydraulic_accumulator, SDO.manufacturer, Literal(manufacturer)))
    data.g.add((hydraulic_accumulator, SDO.serialNumber, Literal(serial_number)))
    # The comment gets the "Schlagzahl" Information.
    data.g.add((hydraulic_accumulator, RDFS.comment, Literal(hydraulic_accumulator_comment)))
    # The second comment gets the manufacturing date
    data.g.add((hydraulic_accumulator, RDFS.comment, Literal(hydraulic_accumulator_manufacturing_date)))

    # properties
    operating_pressure = COMPONENT[hydraulic_accumulator_id + "/p_operating"]
    data.g.add((hydraulic_accumulator, SSN.hasProperty, operating_pressure))
    data.g.add((operating_pressure, RDF.type, SSN.Property))
    data.g.add((operating_pressure, RDF.type, QUDT.Quantity))
    data.g.add((operating_pressure, RDFS.label, Literal("operating pressure")))
    data.g.add((operating_pressure, QUDT.symbol, Literal("p_operating")))
    data.g.add((operating_pressure, QUDT.hasQuantityKind, QUANTITYKIND.Pressure))
    data.g.add((operating_pressure, QUDT.unit, unit_dict[operating_pressure_unit]))
    data.g.add((operating_pressure, QUDT.value, Literal(operating_pressure_value)))

    maximum_pressure = COMPONENT[hydraulic_accumulator_id + "/p_max"]
    data.g.add((hydraulic_accumulator, SSN.hasProperty, maximum_pressure))
    data.g.add((maximum_pressure, RDF.type, SSN.Property))
    data.g.add((maximum_pressure, RDF.type, QUDT.Quantity))
    data.g.add((maximum_pressure, RDFS.label, Literal("maximum working pressure")))
    data.g.add((maximum_pressure, QUDT.symbol, Literal("p_max")))
    data.g.add((maximum_pressure, QUDT.hasQuantityKind, QUANTITYKIND.Pressure))
    data.g.add((maximum_pressure, QUDT.unit, unit_dict[maximum_pressure_unit]))
    data.g.add((maximum_pressure, QUDT.value, Literal(maximum_pressure_value)))

    volume = COMPONENT[hydraulic_accumulator_id + "/V0"]
    data.g.add((hydraulic_accumulator, SSN.hasProperty, volume))
    data.g.add((volume, RDF.type, SSN.Property))
    data.g.add((volume, RDF.type, QUDT.Quantity))
    data.g.add((volume, RDFS.label, Literal("volume")))
    data.g.add((volume, QUDT.symbol, Literal("V0")))
    data.g.add((volume, QUDT.hasQuantityKind, QUANTITYKIND.Volume))
    data.g.add((volume, QUDT.unit, unit_dict[volume_unit]))
    data.g.add((volume, QUDT.value, Literal(volume_value)))
    # TODO: There might be sophisticated special data types for uncertainties in the future 12.2023
    data.g.add((volume, SSN_SYSTEM.Accuracy, Literal(volume_accuracy)))
    data.g.add((volume, RDFS.comment, Literal("Accuracy of the nominal volume estimated as 1% of the nominal volume by Mr. Rexer 12.2023")))

    operating_temperature_range = COMPONENT[hydraulic_accumulator_id + "/T_operating_range"]
    data.g.add((hydraulic_accumulator, SSN.hasProperty, operating_temperature_range))
    data.g.add((operating_temperature_range, RDF.type, SSN.Property))
    data.g.add((operating_temperature_range, RDF.type, QUDT.Quantity))
    data.g.add((operating_temperature_range, RDFS.label, Literal("temperature operating range")))
    data.g.add((operating_temperature_range, QUDT.symbol, Literal("T_operating_range")))
    data.g.add((operating_temperature_range, QUDT.hasQuantityKind, QUANTITYKIND.Area))
    data.g.add((operating_temperature_range, QUDT.unit, unit_dict[operating_temperature_range_unit]))
    data.g.add((operating_temperature_range, schema.minValue, Literal(operating_temperature_range_minvalue, datatype=XSD.double)))
    data.g.add((operating_temperature_range, schema.maxValue, Literal(operating_temperature_range_maxvalue, datatype=XSD.double)))

    ## documentation this can probably be automated
    #img = COMPONENT[hydraulic_accumulator_id + "/IMG_20190809_113156_Bokeh.jpg"]
    #data.g.add((hydraulic_accumulator, SDO.subjectOf, img))
    #data.g.add((hydraulic_accumulator, SDO.image, img))

    #docs = COMPONENT[hydraulic_accumulator_id + "/CAD"]
    #data.g.add((hydraulic_accumulator, SDO.subjectOf, docs))
    #data.g.add((hydraulic_accumulator, SDO.documentation, docs))

    #datasheet = COMPONENT[hydraulic_accumulator_id + "/CAD/air_spring/HH-AR-0521-000_TB_ZB_LUFTFEDER_LH_RH_EA.pdf"]
    #data.g.add((hydraulic_accumulator, SDO.subjectOf, datasheet))
    #data.g.add((hydraulic_accumulator, SDO.documentation, datasheet))

    # rdf doc references
    docttl = COMPONENT[hydraulic_accumulator_id + "/rdf.ttl"]
    data.g.add((docttl, RDF.type, FOAF.Document))
    data.g.add((docttl, FOAF.primaryTopic, hydraulic_accumulator))

    docxml = COMPONENT[hydraulic_accumulator_id + "/rdf.xml"]
    data.g.add((docxml, RDF.type, FOAF.Document))
    data.g.add((docxml, FOAF.primaryTopic, hydraulic_accumulator))

    docjson = COMPONENT[hydraulic_accumulator_id + "/rdf.json"]
    data.g.add((docjson, RDF.type, FOAF.Document))
    data.g.add((docjson, FOAF.primaryTopic, hydraulic_accumulator))

    # current_python_file_dir_path = Path(__file__).parent.resolve()
    dir_path = Path(f"{save_to_dir}/{hydraulic_accumulator_id}")

    try:
        dir_path.mkdir()
    except FileExistsError:
        pass

    file_path = f"{dir_path}/rdf"
    print(data.g.serialize(destination=f"{file_path}.json", format="json-ld", auto_compact=True))
    print(data.g.serialize(destination=f"{file_path}.ttl", base=SUBSTANCE, format="longturtle", encoding="utf-8"))
    print(data.g.serialize(destination=f"{file_path}.xml", base=SUBSTANCE, format="xml"))


