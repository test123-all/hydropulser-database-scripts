from pathlib import Path

from rdflib import Namespace, Literal
from rdflib.namespace import DCAT, DCMITYPE, DCTERMS, RDF, RDFS, XSD, SSN, SDO, FOAF
from pyKRAKEN.kraken import (
    DBO,
    QUDT,
    UNIT,
    QUANTITYKIND,
    Kraken
)

from hardcoded_generate_scripts.gitlab_db_mdgen import generate_sensor_md


SSN_SYSTEM = Namespace("https://www.w3.org/ns/ssn/systems/")

# this should ideally be something like e.g.:
# https://fst.tu-darmstadt.de/namespaces/components/id/
# or w3id
# which redirects to e.g.
# https://fst.tu-darmstadt.de/namespaces/components/doc/
# which redirects to a webserver with static html generated by this, or just directly to
# ns_root = "https://git.rwth-aachen.de/fst-tuda/projects/rdm/datasheets-mockup/"
# FST = Namespace(ns_root + "-/blob/main/")
# TEST_RIG= Namespace(FST["component/"])
# SUBSTANCE = Namespace(FST["substance/"])

TEST_RIG = Namespace("https://w3id.org/fst/resource/")


def main():
    data = Kraken(base=TEST_RIG)
    # data.g.bind("fst-component", TEST_RIG)
    # data.g.bind("fst-substance", SUBSTANCE)
    data.g.bind("fst", TEST_RIG)

    test_rig_id = "018beaa3-8fe7-7dca-ab77-895aa89a269f"  # str(uuid6())

    # the TEST_RIG= the air spring
    test_rig = TEST_RIG[test_rig_id]
    data.g.add((test_rig, RDF.type, DCMITYPE.PhysicalObject))
    # data.g.add((test_rig, DCTERMS.hasPart, air))


    data.g.add((test_rig, SDO.name, Literal("Sirupmischanlage")))
    data.g.add((test_rig, DBO.maintainedBy, Literal("Wetterich")))
    # data.g.add((test_rig, RDFS.label, Literal("350 Damper Test System")))
    data.g.add((test_rig, DCTERMS.identifier, Literal(test_rig_id)))
    # data.g.add((test_rig, DCTERMS.identifier, Literal("350.5")))
    data.g.add((test_rig, DBO.owner, Literal("FST")))
    data.g.add((test_rig, SDO.manufacturer, Literal("FST")))
    data.g.add((test_rig, DCTERMS.modified, Literal("None")))
    #data.g.add((test_rig, SDO.location, Literal("Ölhalle"))) # Möchte man das so im internet stehen haben?
    # data.g.add((test_rig, SDO.serialNumber, Literal("")))
    data.g.add((test_rig, SDO.description, Literal("TODO:")))
    data.g.add((test_rig, SDO.keywords, Literal("test-rig"))) # -> das beißt sich evtl. mit unseren definitionen oder wir unterscheiden einfach dazwischen und sagen, dass in measurments etwas immer ein test rig und/oder test object sein kann, ganz egal von der ursprünglich definierten klasse (, die es noch nicht gibt)
    data.g.add((test_rig, SDO.keywords, Literal("test-stand")))
    data.g.add((test_rig, SDO.keywords, Literal("hardware-in-the-loop")))
    data.g.add((test_rig, SDO.keywords, Literal("real-time-simulation")))


    # # TODO: There might be sophisticated special data types for uncertainties in the future 12.2023
    # data.g.add((operating_temperature_range, SSN_SYSTEM.Accuracy, Literal("3.024219668711204", datatype=XSD.double)))#

    # documentation this can probably be automated
    img = TEST_RIG[test_rig_id + "/IMG/IMG_sirupmischanlage.jpg"]
    data.g.add((test_rig, SDO.subjectOf, img))
    data.g.add((test_rig, SDO.image, img))
    #
    # docs = TEST_RIG[test_rig_id + "/CAD"]
    # data.g.add((test_rig, SDO.subjectOf, docs))
    # data.g.add((test_rig, SDO.documentation, docs))
    #
    # datasheet = TEST_RIG[test_rig_id + "/CAD/air_spring/HH-AR-0521-000_TB_ZB_LUFTFEDER_LH_RH_EA.pdf"]
    # data.g.add((test_rig, SDO.subjectOf, datasheet))
    # data.g.add((test_rig, SDO.documentation, datasheet))


    # rdf doc references
    docttl = TEST_RIG[test_rig_id + "/rdf.ttl"]
    data.g.add((docttl, RDF.type, FOAF.Document))
    data.g.add((docttl, FOAF.primaryTopic, test_rig))

    docxml = TEST_RIG[test_rig_id + "/rdf.xml"]
    data.g.add((docxml, RDF.type, FOAF.Document))
    data.g.add((docxml, FOAF.primaryTopic, test_rig))

    docjson = TEST_RIG[test_rig_id + "/rdf.json"]
    data.g.add((docjson, RDF.type, FOAF.Document))
    data.g.add((docjson, FOAF.primaryTopic, test_rig))

    # documentation extended
    if False:
        data.g.add((img, DCTERMS.subject, test_rig))

        data.g.add((docs, RDF.type, DCAT.Catalog))
        data.g.add((docs, RDF.type, SDO.CreativeWorkSeries))
        data.g.add((docs, DCTERMS.title, Literal("CAD Vibracoustic Luftfeder")))
        data.g.add((docs, DCTERMS.description, Literal("CAD Daten und Technische Zeichnungen Vibracoustic Luftfeder")))
        data.g.add((docs, DCTERMS.identifier, Literal("git-commit-SHA:")))
        data.g.add((docs, SDO.version, Literal("1.0.0")))
        data.g.add((docs, SDO.url, docs))
        data.g.add((docs, DCTERMS.publisher, Literal("Manuel Rexer"))) # Alternatively rdflib.URIRef("https://orcid.org/0000-0003-0559-1156") could also be an idea
        data.g.add((docs, DCTERMS.creator, Literal("Manuel Rexer")))
        data.g.add((docs, DCTERMS.created, Literal("22-07-19", datatype=XSD.date)))
        data.g.add((docs, DCTERMS.rightsHolder, Literal("Vibracoustic SE ")))
        data.g.add((docs, DCTERMS.subject, test_rig))

        data.g.add((datasheet, RDF.type, DCAT.Resource))
        data.g.add((datasheet, RDF.type, SDO.CreativeWork))
        data.g.add((datasheet, DCTERMS.title, Literal("TB ZB Luftfeder DK2 LH / RH")))
        data.g.add((datasheet, DCTERMS.description, Literal("Technische Zeichnung Vibracoustic Luftfeder")))
        data.g.add((datasheet, DCTERMS.identifier, Literal("git-commit-SHA:")))
        data.g.add((datasheet, DCTERMS.identifier, Literal("Drawing-no.:HH-AR-0521-000")))
        data.g.add((datasheet, SDO.version, Literal("1.0.0-Ea")))
        data.g.add((datasheet, SDO.url, datasheet))
        data.g.add((datasheet, DCTERMS.publisher, Literal("Vibracoustic SE ")))
        data.g.add((datasheet, DCTERMS.rightsHolder, Literal("Vibracoustic SE ")))
        data.g.add((datasheet, DCTERMS.creator, Literal("Heinsohn")))
        data.g.add((datasheet, DCTERMS.created, Literal("09-11-16", datatype=XSD.date)))
        data.g.add((datasheet, DCTERMS.contributor, Literal("Müller")))
        data.g.add((datasheet, DCTERMS.contributor, Literal("Jurk")))
        data.g.add((datasheet, DCTERMS.modified, Literal("31-01-17", datatype=XSD.date)))
        data.g.add((datasheet, DCTERMS.modified, Literal("28-11-17", datatype=XSD.date)))
        data.g.add((datasheet, DCTERMS.modified, Literal("21-02-18", datatype=XSD.date)))
        data.g.add((datasheet, DCTERMS.modified, Literal("30-11-18", datatype=XSD.date)))
        data.g.add((datasheet, DCTERMS.subject, test_rig))
        data.g.add((docs, DCTERMS.hasPart, datasheet))

    current_python_file_dir_path = Path(__file__).parent.resolve()
    dir_path = Path(f"{current_python_file_dir_path}/{test_rig_id}")

    try:
        dir_path.mkdir()
    except FileExistsError:
        pass

    file_path = f"{dir_path}/rdf"
    print(data.g.serialize(destination=f"{file_path}.json", format="json-ld", auto_compact=True))
    print(data.g.serialize(destination=f"{file_path}.ttl", base=TEST_RIG, format="longturtle", encoding="utf-8"))
    print(data.g.serialize(destination=f"{file_path}.xml", base=TEST_RIG, format="xml"))

    generate_sensor_md(f'{dir_path}/')

if __name__ == '__main__':
    main()
