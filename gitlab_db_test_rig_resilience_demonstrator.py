import uuid6
from pathlib import Path

from rdflib import Namespace, Literal
from rdflib.namespace import DCAT, DCMITYPE, DCTERMS, RDF, XSD, SDO, FOAF
from pyKRAKEN.kraken import (
    DBO,
    Kraken
)

from hardcoded_generate_scripts.gitlab_db_mdgen import generate_sensor_md

SSN_SYSTEM = Namespace("https://www.w3.org/ns/ssn/systems/")
TEST_RIG = Namespace("https://w3id.org/fst/resource/")

def main():
    data = Kraken(base=TEST_RIG)
    # data.g.bind("fst-component", TEST_RIG)
    # data.g.bind("fst-substance", SUBSTANCE)
    data.g.bind("fst", TEST_RIG)

    test_rig_id = "0192fd1d-3b09-734b-b4e3-621fc590d00c"
    test_rig = TEST_RIG[test_rig_id]
    data.g.add((test_rig, RDF.type, DCMITYPE.PhysicalObject))
    data.g.add((test_rig, SDO.name, Literal("Resilienzdemonstrator")))
    data.g.add((test_rig, DBO.maintainedBy, Literal("Logan")))
    data.g.add((test_rig, DCTERMS.identifier, Literal(test_rig_id)))
    data.g.add((test_rig, DBO.owner, Literal("FST")))
    data.g.add((test_rig, SDO.manufacturer, Literal("FST")))
    data.g.add((test_rig, DCTERMS.modified, Literal("None")))
    # data.g.add((test_rig, SDO.location, Literal("Ölhalle"))) # Möchte man das so im internet stehen haben?
    # data.g.add((test_rig, SDO.serialNumber, Literal("")))
    data.g.add((test_rig, SDO.description, Literal("https://www.fst.tu-darmstadt.de/forschung_fst/pruefstaende/resilienz/resilienzpruefstand.de.jsp"))) # Hier würde ich gerne einen Link zur Web-Seite des Demonstrators stehen haben https://www.fst.tu-darmstadt.de/forschung_fst/pruefstaende/resilienz/resilienzpruefstand.de.jsp
    data.g.add((test_rig, SDO.keywords, Literal("test-rig"))) # -> das beißt sich evtl. mit unseren definitionen oder wir unterscheiden einfach dazwischen und sagen, dass in measurments etwas immer ein test rig und/oder test object sein kann, ganz egal von der ursprünglich definierten klasse (, die es noch nicht gibt)
    data.g.add((test_rig, SDO.keywords, Literal("test-stand")))
    data.g.add((test_rig, SDO.keywords, Literal("resilience")))
    data.g.add((test_rig, SDO.keywords, Literal("adaptivity")))
    data.g.add((test_rig, SDO.keywords, Literal("urban water distribution systems")))
    data.g.add((test_rig, SDO.keywords, Literal("distributed control")))
    data.g.add((test_rig, SDO.keywords, Literal("time series analysis")))

    img = TEST_RIG[test_rig_id + "/IMG/image_241018_Resilienzdemonstrator_Foto_Logan.jpg"]
    data.g.add((test_rig, SDO.subjectOf, img))
    data.g.add((test_rig, SDO.image, img))

    docttl = TEST_RIG[test_rig_id + "/rdf.ttl"]
    data.g.add((docttl, RDF.type, FOAF.Document))
    data.g.add((docttl, FOAF.primaryTopic, test_rig))

    docxml = TEST_RIG[test_rig_id + "/rdf.xml"]
    data.g.add((docxml, RDF.type, FOAF.Document))
    data.g.add((docxml, FOAF.primaryTopic, test_rig))

    docjson = TEST_RIG[test_rig_id + "/rdf.json"]
    data.g.add((docjson, RDF.type, FOAF.Document))
    data.g.add((docjson, FOAF.primaryTopic, test_rig))

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