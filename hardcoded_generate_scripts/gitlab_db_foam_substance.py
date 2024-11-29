from pathlib import Path

from rdflib import Namespace, Literal
from rdflib.namespace import DCMITYPE, RDF, RDFS, XSD, SSN, SDO, FOAF, DCTERMS
from pyKRAKEN.kraken import (
    DBO,
    QUDT,
    UNIT,
    QUANTITYKIND,
    Kraken
)

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
             "kg/m^3": UNIT.KiloGM_PER_M3,
             "Pa": UNIT.PA,
             "%": UNIT.PERCENT,
             "1/cm": UNIT.PER_CentiM,
             "1/m": UNIT.PER_M}


def generate_foam_db_files(df_row, path_for_generated_pID_files):
    SUBSTANCE = Namespace("https://w3id.org/fst/resource/")

    data = Kraken(base=SUBSTANCE)
    # data.g.bind("fst-substance", FOAM_SUBSTANCE)
    data.g.bind("fst", SUBSTANCE)

    # Choose your ID
    foam_id = df_row['UUID']

    # The substance component.
    foam = SUBSTANCE[foam_id]
    data.g.add((foam, RDF.type, DCMITYPE.PhysicalObject))
    data.g.add((foam, RDF.type, SDO.ChemicalSubstance))
    data.g.add((foam, RDFS.label, Literal(df_row['material_name'])))
    data.g.add((foam, RDFS.label, Literal(df_row['Bezeichnung'])))
    data.g.add((foam, DBO.owner, Literal("FST")))
    data.g.add((foam, SDO.manufacturer, Literal(df_row['Hersteller'])))
    data.g.add((foam, DBO.maintainedBy, Literal(df_row['Verantwortlicher WiMi'])))
    data.g.add((foam, RDFS.comment, Literal(df_row['Bemerkung'])))
    data.g.add((foam, DCTERMS.identifier, Literal(foam_id)))
    data.g.add((foam, DCTERMS.identifier, Literal(f"FST-INV:{df_row['Ident-Nummer']}")))

    net_density = SUBSTANCE[foam_id + "/NetDensity"]
    data.g.add((foam, SSN.hasProperty, net_density))
    data.g.add((net_density, RDF.type, SSN.Property))
    data.g.add((net_density, RDF.type, QUDT.Quantity))
    data.g.add((net_density, RDFS.label, Literal("net density")))
    # data.g.add((net_density, QUDT.symbol, Literal("R")))
    data.g.add((net_density, QUDT.hasQuantityKind, QUANTITYKIND.Density))
    data.g.add((net_density, SDO.minValue, Literal(df_row['net_density min'], datatype=XSD.double)))
    data.g.add((net_density, SDO.maxValue, Literal(df_row['net_density max'], datatype=XSD.double)))
    data.g.add((net_density, QUDT.unit, unit_dict[df_row['net_density unit']]))
    # data.g.add((net_density, QUDT.value, Literal("287", datatype=XSD.double)))
    data.g.add((net_density, RDFS.comment, Literal(df_row['net_density comment'])))
    data.g.add((net_density, SSN.isPropertyOf, foam))

    compression_strength = SUBSTANCE[foam_id + "/CompressionStrength"]
    data.g.add((foam, SSN.hasProperty, compression_strength))
    data.g.add((compression_strength, RDF.type, SSN.Property))
    data.g.add((compression_strength, RDF.type, QUDT.Quantity))
    data.g.add((compression_strength, RDFS.label, Literal("compression strength")))
    # data.g.add((compression_strength, QUDT.symbol, Literal("R")))
    data.g.add((compression_strength, QUDT.hasQuantityKind, QUANTITYKIND.NormalStress))
    data.g.add((compression_strength, SDO.minValue, Literal(df_row['compression_strength min'], datatype=XSD.double)))
    data.g.add((compression_strength, SDO.maxValue, Literal(df_row['compression_strength max'], datatype=XSD.double)))
    data.g.add((compression_strength, QUDT.unit, unit_dict[df_row['compression_strength unit']]))
    # data.g.add((compression_strength, QUDT.value, Literal("287", datatype=XSD.double)))
    data.g.add((compression_strength, RDFS.comment, Literal(df_row['compression_strength comment'])))
    data.g.add((compression_strength, SSN.isPropertyOf, foam))

    tensile_strength = SUBSTANCE[foam_id + "/TensileStrength"]
    data.g.add((foam, SSN.hasProperty, tensile_strength))
    data.g.add((tensile_strength, RDF.type, SSN.Property))
    data.g.add((tensile_strength, RDF.type, QUDT.Quantity))
    data.g.add((tensile_strength, RDFS.label, Literal("tensile strength")))
    # data.g.add((tensile_strength, QUDT.symbol, Literal("R")))
    data.g.add((tensile_strength, QUDT.hasQuantityKind, QUANTITYKIND.NormalStress))
    data.g.add((tensile_strength, SDO.minValue, Literal(df_row['tensile_strength min'], datatype=XSD.double)))
    # data.g.add((tensile_strength, SDO.maxValue, Literal(df_row['tensile_strength max'], datatype=XSD.double)))
    data.g.add((tensile_strength, QUDT.unit, unit_dict[df_row['tensile_strength unit']]))
    # data.g.add((tensile_strength, QUDT.value, Literal("287", datatype=XSD.double)))
    data.g.add((tensile_strength, RDFS.comment, Literal(df_row['tensile_strength comment'])))
    data.g.add((tensile_strength, SSN.isPropertyOf, foam))

    elongation_at_break = SUBSTANCE[foam_id + "/ElongationAtBreak"]
    data.g.add((foam, SSN.hasProperty, elongation_at_break))
    data.g.add((elongation_at_break, RDF.type, SSN.Property))
    data.g.add((elongation_at_break, RDF.type, QUDT.Quantity))
    data.g.add((elongation_at_break, RDFS.label, Literal("elongation at break")))
    # data.g.add((elongation_at_break, QUDT.symbol, Literal("R")))
    data.g.add((elongation_at_break, QUDT.hasQuantityKind, QUANTITYKIND.Strain))
    data.g.add((elongation_at_break, SDO.minValue, Literal(df_row['elongation_at_break min'], datatype=XSD.double)))
    # data.g.add((elongation_at_break, SDO.maxValue, Literal(df_row['elongation_at_break max'], datatype=XSD.double)))
    data.g.add((elongation_at_break, QUDT.unit, unit_dict[df_row['elongation_at_break unit']]))
    # data.g.add((elongation_at_break, QUDT.value, Literal("287", datatype=XSD.double)))
    data.g.add((elongation_at_break, RDFS.comment, Literal(df_row['elongation_at_break comment'])))
    data.g.add((elongation_at_break, SSN.isPropertyOf, foam))

    number_of_pores = SUBSTANCE[foam_id + "/NumberOfPores"]
    data.g.add((foam, SSN.hasProperty, number_of_pores))
    data.g.add((number_of_pores, RDF.type, SSN.Property))
    data.g.add((number_of_pores, RDF.type, QUDT.Quantity))
    data.g.add((number_of_pores, RDFS.label, Literal("number of pores")))
    # data.g.add((number_of_pores, QUDT.symbol, Literal("R")))
    # data.g.add((number_of_pores, QUDT.hasQuantityKind, QUANTITYKIND.)) TODO: No COUNT per Area
    data.g.add((number_of_pores, SDO.minValue, Literal(df_row['number_of_pores min'], datatype=XSD.double)))
    data.g.add((number_of_pores, SDO.maxValue, Literal(df_row['number_of_pores max'], datatype=XSD.double)))
    data.g.add((number_of_pores, QUDT.unit, unit_dict[df_row['number_of_pores unit']]))
    # data.g.add((number_of_pores, QUDT.value, Literal("287", datatype=XSD.double)))
    # data.g.add((number_of_pores, RDFS.comment, Literal(df_row['number_of_pores comment'])))
    data.g.add((number_of_pores, SSN.isPropertyOf, foam))

    # rdf doc references
    docttl = SUBSTANCE[foam_id + "/rdf.ttl"]
    data.g.add((docttl, RDF.type, FOAF.Document))
    data.g.add((docttl, FOAF.primaryTopic, foam))

    docxml = SUBSTANCE[foam_id + "/rdf.xml"]
    data.g.add((docxml, RDF.type, FOAF.Document))
    data.g.add((docxml, FOAF.primaryTopic, foam))

    docjson = SUBSTANCE[foam_id + "/rdf.json"]
    data.g.add((docjson, RDF.type, FOAF.Document))
    data.g.add((docjson, FOAF.primaryTopic, foam))


    pID_dir_path = Path(f"{path_for_generated_pID_files}/{foam_id}")

    try:
        pID_dir_path.mkdir()
    except FileExistsError:
        pass

    print(data.g.serialize(destination=f"{pID_dir_path}/rdf.json", format="json-ld", auto_compact=True))
    print(data.g.serialize(destination=f"{pID_dir_path}/rdf.ttl", base=SUBSTANCE, format="longturtle", encoding="utf-8"))
    print(data.g.serialize(destination=f"{pID_dir_path}/rdf.xml", base=SUBSTANCE, format="xml"))
