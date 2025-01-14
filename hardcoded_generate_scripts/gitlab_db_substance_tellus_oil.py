from pathlib import Path

from rdflib import Namespace, Literal
from rdflib.namespace import DCMITYPE, DCTERMS, RDF, RDFS, XSD, SSN, SDO, FOAF
from pyKRAKEN.kraken import (
    DBO,
    QUDT,
    UNIT,
    QUANTITYKIND,
    Kraken
)
import pandas as pd
import h5py
import numpy as np


def create_hdf5():
    # Read out the data of the excel sheet
    current_python_file_dir_path = Path(__file__).parent.resolve()
    df_viskositaet = pd.read_excel(f"{current_python_file_dir_path}/Öl_Shell//SHELL_Kinematische Viskosität/Viskosität_SHELL.xlsx")
    df_dichte = pd.read_excel(f"{current_python_file_dir_path}/Öl_Shell//SHELL_Dichte/Dichte_SHELL.xlsx")

    temperature_data = df_viskositaet['[K]'][0:11]
    kinematic_viscosity_data = df_viskositaet['kinematische Viskositaet [mm²/s]'][0:11]
    kinematic_viscosity_std_deviation_data = df_viskositaet['Standardabweichnung kinematische Viskositaet [mm²/s]'][0:11]
    dichte_data = df_dichte['Dichte [g/l]'][0:11]


    # Create the hdf5 file with the datasets
    with h5py.File(f'shell_tellus_oil.hdf5', 'w') as f:
        grp_substance = f.create_group('substance') #f'{substance_name_en}')
        grp_substance.attrs['http://www.w3.org/1999/02/22-rdf-syntax-ns#type'] = 'http://schema.org/ChemicalSubstance'
        grp_substance.attrs['http://www.w3.org/1999/02/22-rdf-syntax-ns#type'] = 'http://purl.org/dc/dcmitype/PhysicalObject'
        # grp_substance.attrs['http://www.w3.org/2000/01/rdf-schema#label'] = f'{chemical_composition}'
        grp_substance.attrs['http://schema.org/name'] = 'Shell Tellus Oil 46'
        # TODO: Check with a assertion that the vectors and the read out value is correct
        grp_substance.attrs['http://www.w3.org/2000/01/rdf-schema#comment'] = (
                "'temperatures' is the index vector to the given look-up tables. To find the value for a given "
                "temperature 'T' inside the lookup tables, you search for the index of the given temperature "
                "'T' in 'temperatures'. Then, use the index "
                "to access the lookup tables with lookup_table[index_T].\n"
                "Example:\n"
                f"For T=293.15K, you get index_T=1, and kinematic_viscosity[1]=133.11173 or density[1]=863.00 ."
                )

        grp_index_vectors = grp_substance.create_group('index_vectors')
        # TODO: was gebe ich dann bei index_vectors und n_dimensional_lookup_tables für attribute an?
        temperatures_column_vector = grp_index_vectors.create_dataset('temperatures', data=temperature_data)
        temperatures_column_vector.attrs['http://qudt.org/schema/qudt/hasQuantityKind'] = 'http://qudt.org/vocab/quantitykind/Temperature'
        temperatures_column_vector.attrs['http://qudt.org/schema/qudt/unit'] = 'http://qudt.org/vocab/unit/K'
        temperatures_column_vector.attrs['http://www.w3.org/1999/02/22-rdf-syntax-ns#type'] = 'http://qudt.org/2.1/schema/qudt/Quantity'
        temperatures_column_vector.attrs['http://qudt.org/2.1/schema/qudt/symbol'] = 'T'
        temperatures_column_vector.attrs['http://qudt.org/schema/keywords'] = ['index_vector']

        grp_dependend = grp_substance.create_group('n_dimensional_lookup_tables')
        kinematic_viscosity = grp_dependend.create_dataset('kinematic_viscosity', data=kinematic_viscosity_data)
        kinematic_viscosity.attrs['http://qudt.org/schema/qudt/hasQuantityKind'] = 'http://qudt.org/vocab/quantitykind/KinematicViscosity'
        kinematic_viscosity.attrs['http://qudt.org/schema/qudt/unit'] = 'http://qudt.org/vocab/quantitykind/MilliM-PER-SEC'
        kinematic_viscosity.attrs['http://www.w3.org/1999/02/22-rdf-syntax-ns#type'] = 'http://qudt.org/2.1/schema/qudt/Quantity'
        kinematic_viscosity.attrs['http://qudt.org/2.1/schema/qudt/symbol'] = 'ν'
        kinematic_viscosity.attrs['http://qudt.org/schema/keywords'] = ['lookup_table']

        # kinematic_viscosity_std_deviation = grp_dependend.create_dataset('kinematic_viscosity_standard_deviation', data=kinematic_viscosity_std_deviation_data)
        # kinematic_viscosity_std_deviation.attrs['http://qudt.org/schema/qudt/hasQuantityKind'] = 'http://qudt.org/vocab/quantitykind/KinematicViscosity'
        # kinematic_viscosity_std_deviation.attrs['http://qudt.org/schema/qudt/unit'] = 'http://qudt.org/vocab/quantitykind/MilliM-PER-SEC'
        # kinematic_viscosity_std_deviation.attrs['http://www.w3.org/1999/02/22-rdf-syntax-ns#type'] = 'http://qudt.org/2.1/schema/qudt/Quantity'
        # #kinematic_viscosity_std_deviation.attrs['http://qudt.org/2.1/schema/qudt/symbol'] = 'ν'
        # kinematic_viscosity_std_deviation.attrs['http://qudt.org/schema/keywords'] = ['lookup_table']

        density = grp_dependend.create_dataset('density', data=dichte_data)
        density.attrs['http://qudt.org/schema/qudt/hasQuantityKind'] = 'http://qudt.org/vocab/quantitykind/Density'
        density.attrs['http://qudt.org/schema/qudt/unit'] = 'http://qudt.org/vocab/unit/GM-PER-L'
        density.attrs['http://www.w3.org/1999/02/22-rdf-syntax-ns#type'] = 'http://qudt.org/2.1/schema/qudt/Quantity'
        density.attrs['http://qudt.org/2.1/schema/qudt/symbol'] = 'ρ'
        density.attrs['http://qudt.org/schema/keywords'] = ['lookup_table']

def create_rdf(substance_uuid):
    # Create rdf data for the substance
    SUBSTANCE = Namespace("https://w3id.org/fst/resource/")

    data = Kraken(base=SUBSTANCE)
    # data.g.bind("fst-substance", SUBSTANCE)
    data.g.bind("fst", SUBSTANCE)

    # a subcomponent = the air
    substance = SUBSTANCE[substance_uuid]
    data.g.add((substance, RDF.type, DCMITYPE.PhysicalObject))
    data.g.add((substance, RDF.type, SDO.ChemicalSubstance))

    #data.g.add((substance, RDFS.label, Literal(chemical_composition)))
    data.g.add((substance, SDO.name, Literal('Shell Tellus Oil 46')))
    data.g.add((substance, DBO.owner, Literal("FST")))
    data.g.add((substance, DCTERMS.identifier, Literal(substance_uuid)))
    data.g.add((substance, DCTERMS.identifier, Literal("001B0669")))
    data.g.add((substance, DCTERMS.identifier, Literal("140001010640")))
    #data.g.add((substance, SDO.chemicalComposition, Literal(chemical_composition)))
    data.g.add((substance, SDO.producer, Literal("Shell")))

    # systematic_uncertainty_temperature
    # kapillarkonstante
    # kinematic_viscosity
    # systematic error of measurement
    # standard_deviation_kinematic_viscosity
    # Hagebachkorrektur
    # Theoretisch brauche ich nur die kinematische viskosität und die dichte

    ## Describe the hdf5
    doc_hdf5 = SUBSTANCE[substance_uuid + "/shell_tellus_oil_46.hdf5"]
    data.g.add((doc_hdf5, RDF.type, FOAF.Document))
    data.g.add((doc_hdf5, FOAF.primaryTopic, substance))
    data.g.add((doc_hdf5, SDO.encodingFormat, Literal('application/x-hdf5')))
    # TODO: Change it that way that the example is valid for every file
    data.g.add((doc_hdf5, SDO.description, Literal((
            "'temperatures' is the index vector to the given look-up tables. To find the value for a given "
            "temperature 'T' inside the lookup tables, you search for the index of the given temperature "
            "'T' in 'temperatures'. Then, use the index "
            "to access the lookup tables with lookup_table[index_T].\n"
            "Example:\n"
            f"For T=293.15K, you get index_T=1, and kinematic_viscosity[1]=133.11173 or density[1]=863.00 ."

    ))))
    doc_hdf5_temperatures_vector = SUBSTANCE[substance_uuid + "/shell_tellus_oil_46.hdf5/temperatures_vector"]
    data.g.add((doc_hdf5_temperatures_vector, RDF.type, SDO.Dataset))
    data.g.add((doc_hdf5_temperatures_vector, SDO.contentUrl, Literal('/substance/index_vectors/temperatures')))
    data.g.add((doc_hdf5_temperatures_vector, SDO.isPartOf, doc_hdf5))
    data.g.add((doc_hdf5_temperatures_vector, SDO.description, Literal(
        'first index vector that is used to get the correct index in the lookup tables for a given temperature')))
    data.g.add((doc_hdf5_temperatures_vector, SDO.keywords, Literal('index_vector')))

    doc_hdf5_kinematic_viscosity = SUBSTANCE[substance_uuid + "/shell_tellus_oil_46.hdf5/kinematic_viscosity"]
    data.g.add((doc_hdf5_kinematic_viscosity, RDF.type, SDO.Dataset))
    data.g.add((doc_hdf5_kinematic_viscosity, SDO.contentUrl, Literal('/substance/n_dimensional_lookup_tables/kinematic_viscosity')))
    data.g.add((doc_hdf5_kinematic_viscosity, SDO.isPartOf, doc_hdf5))
    data.g.add((doc_hdf5_kinematic_viscosity, SDO.description, Literal(
        'first index vector that is used to get the correct index in the lookup tables for a given temperature')))
    data.g.add((doc_hdf5_kinematic_viscosity, SDO.keywords, Literal('lookup_table')))

    # doc_hdf5_kinematic_viscosity_std_deviation = SUBSTANCE[substance_uuid + "/shell_tellus_oil_46.hdf5/kinematic_viscosity_standard_deviation"]
    # data.g.add((doc_hdf5_kinematic_viscosity_std_deviation, RDF.type, SDO.Dataset))
    # data.g.add((doc_hdf5_kinematic_viscosity_std_deviation, SDO.contentUrl, Literal('/substance/n_dimensional_lookup_tables/kinematic_viscosity_standard_deviation')))
    # data.g.add((doc_hdf5_kinematic_viscosity_std_deviation, SDO.isPartOf, doc_hdf5))
    # data.g.add((doc_hdf5_kinematic_viscosity_std_deviation, SDO.description, Literal(
    #     'first index vector that is used to get the correct index in the lookup tables for a given temperature')))
    # data.g.add((doc_hdf5_kinematic_viscosity_std_deviation, SDO.keywords, Literal('lookup_table')))

    doc_hdf5_density = SUBSTANCE[substance_uuid + "/shell_tellus_oil_46.hdf5/density"]
    data.g.add((doc_hdf5_density, RDF.type, SDO.Dataset))
    data.g.add((doc_hdf5_density, SDO.contentUrl, Literal('/substance/n_dimensional_lookup_tables/density')))
    data.g.add((doc_hdf5_density, SDO.isPartOf, doc_hdf5))
    data.g.add((doc_hdf5_density, SDO.description, Literal(
        'first index vector that is used to get the correct index in the lookup tables for a given temperature')))
    data.g.add((doc_hdf5_density, SDO.keywords, Literal('lookup_table')))


    # Add the hasPart predicates to the hdf5 file
    data.g.add((doc_hdf5, SDO.hasPart, doc_hdf5_temperatures_vector))

    data.g.add((doc_hdf5, SDO.hasPart, doc_hdf5_kinematic_viscosity))
    # data.g.add((doc_hdf5, SDO.hasPart, doc_hdf5_kinematic_viscosity_std_deviation))
    data.g.add((doc_hdf5, SDO.hasPart, doc_hdf5_density))

    # ---Describe the properties of the substance and link them to the hdf5 datasets
    kinematic_viscosity = SUBSTANCE[substance_uuid + "/kinematic_viscosity"]
    data.g.add((substance, SSN.hasProperty, kinematic_viscosity))
    data.g.add((kinematic_viscosity, SSN.isPropertyOf, substance))
    data.g.add((kinematic_viscosity, RDF.type, SSN.Property))
    data.g.add((kinematic_viscosity, RDF.type, QUDT.Quantity))
    data.g.add((kinematic_viscosity, RDFS.label, Literal("kinematic viscosity of the substance")))
    data.g.add((kinematic_viscosity, QUDT.symbol, Literal("ν")))
    data.g.add((kinematic_viscosity, QUDT.hasQuantityKind, QUANTITYKIND.KinematicViscosity))
    data.g.add((kinematic_viscosity, QUDT.unit, UNIT["MilliM-PER-SEC"]))
    data.g.add((kinematic_viscosity, SDO.dataset, doc_hdf5_kinematic_viscosity))

    # kinematic_viscosity_standard_deviation = SUBSTANCE[substance_uuid + "/kinematic_viscosity_standard_deviation"]
    # data.g.add((substance, SSN.hasProperty, kinematic_viscosity_standard_deviation))
    # data.g.add((kinematic_viscosity_standard_deviation, SSN.isPropertyOf, substance))
    # data.g.add((kinematic_viscosity_standard_deviation, RDF.type, SSN.Property))
    # data.g.add((kinematic_viscosity_standard_deviation, RDF.type, QUDT.Quantity))
    # data.g.add((kinematic_viscosity_standard_deviation, RDFS.label, Literal("standard deviation of the kinematic viscosity of the substance")))
    # #data.g.add((kinematic_viscosity_standard_deviation, QUDT.symbol, Literal("ν")))
    # data.g.add((kinematic_viscosity_standard_deviation, QUDT.hasQuantityKind, QUANTITYKIND.KinematicViscosity))
    # data.g.add((kinematic_viscosity_standard_deviation, QUDT.unit, UNIT["MilliM-PER-SEC"]))
    # data.g.add((kinematic_viscosity_standard_deviation, SDO.dataset, doc_hdf5_kinematic_viscosity_std_deviation))

    density = SUBSTANCE[substance_uuid + "/density"]
    data.g.add((substance, SSN.hasProperty, density))
    data.g.add((density, SSN.isPropertyOf, substance))
    data.g.add((density, RDF.type, SSN.Property))
    data.g.add((density, RDF.type, QUDT.Quantity))
    data.g.add((density, RDFS.label, Literal("density of the substance")))
    data.g.add((density, QUDT.symbol, Literal("ρ")))
    data.g.add((density, QUDT.hasQuantityKind, QUANTITYKIND.Density))
    data.g.add((density, QUDT.unit, UNIT["GM-PER-L"]))
    data.g.add((density, SDO.dataset, doc_hdf5_density))

    # TODO: add a comment or description or keywords to define that this is a index vector and that is the first of lookuptables
    # TODO: Theoretically there need to be a type index vector and lookup table in the future and a predicate that connects them
    #  If I should want to describe at which position the index vector stand in the lookup table i need another term/type a quad
    #  statement that describes the index position would also be possible
    # TODO: If i describe .. that depend on different physical  quantities how I would split them into different data sets for
    #  example I want to describe that c_v of s substance depends on the temperature and pressure.

    # rdf doc references
    docttl = SUBSTANCE[substance_uuid + "/rdf.ttl"]
    data.g.add((docttl, RDF.type, FOAF.Document))
    data.g.add((docttl, RDF.type, SDO.TextObject))
    data.g.add((docttl, FOAF.primaryTopic, substance))
    data.g.add((docttl, SDO.encodingFormat, Literal('text/turtle')))

    docxml = SUBSTANCE[substance_uuid + "/rdf.xml"]
    data.g.add((docxml, RDF.type, FOAF.Document))
    data.g.add((docttl, RDF.type, SDO.TextObject))
    data.g.add((docxml, FOAF.primaryTopic, substance))
    data.g.add((docxml, SDO.encodingFormat, Literal('text/xml')))
    data.g.add((docxml, SDO.encodingFormat, Literal('application/rdf+xml')))

    docjson = SUBSTANCE[substance_uuid + "/rdf.json"]
    data.g.add((docjson, RDF.type, FOAF.Document))
    data.g.add((docttl, RDF.type, SDO.TextObject))
    data.g.add((docjson, FOAF.primaryTopic, substance))
    # TODO: FIXME: Falls iana als seite bleibt oder älter ist könnte man auch kucken ob man die URL von dort als p_ID verwendet https://www.iana.org/assignments/media-types/media-types.xhtml
    # TODO: FIXME: auch n0ochmal kucken ob das sinnvoll ist beides anzugeben, oder nur die rdf sachen
    data.g.add((docjson, SDO.encodingFormat, Literal('application/json')))
    data.g.add((docjson, SDO.encodingFormat, Literal('application/ld+json')))

    current_python_file_dir_path = Path(__file__).parent.resolve()
    dir_path = Path(f"{current_python_file_dir_path}/{substance_uuid}")

    try:
        dir_path.mkdir()
    except FileExistsError:
        pass

    file_path = f"{dir_path}/rdf"
    print(data.g.serialize(destination=f"{file_path}.json", format="json-ld", auto_compact=True))
    print(data.g.serialize(destination=f"{file_path}.ttl", base=SUBSTANCE, format="longturtle", encoding="utf-8"))
    print(data.g.serialize(destination=f"{file_path}.xml", base=SUBSTANCE, format="xml"))


def main ():
    # TODO:
    substance_uuid = '018bb4b1-db4e-7c6c-9563-d15648bdbe15'

    create_hdf5()
    create_rdf(substance_uuid)



if __name__ == '__main__':
    main()
