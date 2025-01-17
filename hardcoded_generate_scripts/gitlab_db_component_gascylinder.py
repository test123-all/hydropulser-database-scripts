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

import gitlab_db_mdgen


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

SSN_SYSTEM = Namespace("https://www.w3.org/ns/ssn/systems/")

COMPONENT = Namespace("https://w3id.org/fst/resource/")
SUBSTANCE = Namespace("https://w3id.org/fst/resource/")

def main():
    data = Kraken(base=COMPONENT)
    # data.g.bind("fst-component", COMPONENT)
    # data.g.bind("fst-substance", SUBSTANCE)
    data.g.bind("fst", COMPONENT)

    gas_cylinder_id = "018bb4b1-db48-73b8-9d82-8a8ffb6ee225"  # str(uuid6())


    # the component = the gascylinder
    gas_cylinder = COMPONENT[gas_cylinder_id]
   
    data.g.add((gas_cylinder, RDF.type, DCMITYPE.PhysicalObject))
    
    data.g.add((gas_cylinder, RDFS.label, Literal("gas cylinder")))
    data.g.add((gas_cylinder, DCTERMS.identifier, Literal(gas_cylinder_id)))
    # data.g.add((gas_cylinder, DCTERMS.identifier, Literal("")))
    data.g.add((gas_cylinder, DBO.owner, Literal("Chair of Fluidsystems")))
    data.g.add((gas_cylinder, SDO.manufacturer, Literal("Chair of Fluidsystems")))
    # data.g.add((gas_cylinder, SDO.serialNumber, Literal("")))

    # properties
    displacement_area = COMPONENT[gas_cylinder_id + "/A_d"]
    data.g.add((gas_cylinder, SSN.hasProperty, displacement_area))
    data.g.add((displacement_area, RDF.type, SSN.Property))
    data.g.add((displacement_area, RDF.type, QUDT.Quantity))
    data.g.add((displacement_area, RDFS.label, Literal("displacement area")))
    data.g.add((displacement_area, QUDT.symbol, Literal("A_d")))
    data.g.add((displacement_area, QUDT.hasQuantityKind, QUANTITYKIND.Area))
    data.g.add((displacement_area, QUDT.unit, UNIT.M2))
    data.g.add((displacement_area, QUDT.value, Literal("-0.000804200000000000", datatype=XSD.double)))
    data.g.add((displacement_area, RDFS.comment, Literal("negative direction")))
    # TODO: There might be sophisticated special data types for uncertainties in the future 12.2023
    data.g.add((displacement_area, SSN_SYSTEM.Accuracy, Literal("1.00562380841419e-06", datatype=XSD.double)))
    # Source: Manufacturing acurracy of the piston diameter 0.02 mm


    volume_design_point = COMPONENT[gas_cylinder_id + "/V1"]
    data.g.add((gas_cylinder, SSN.hasProperty, volume_design_point))
    data.g.add((volume_design_point, RDF.type, SSN.Property))
    data.g.add((volume_design_point, RDF.type, QUDT.Quantity))
    data.g.add((volume_design_point, RDFS.label, Literal("volume design point")))
    data.g.add((volume_design_point, QUDT.symbol, Literal("V1")))
    data.g.add((volume_design_point, QUDT.hasQuantityKind, QUANTITYKIND.Volume))
    data.g.add((volume_design_point, QUDT.unit, UNIT.M3))
    data.g.add((volume_design_point, QUDT.value, Literal("0.000043", datatype=XSD.double)))
    # TODO: There might be sophisticated special data types for uncertainties in the future 12.2023
    data.g.add((volume_design_point, SSN_SYSTEM.Accuracy, Literal("337e-9", datatype=XSD.double)))
    #source: Bachelorthesis Louis Hill

    volume_design_point0 = COMPONENT[gas_cylinder_id + "/V0"]
    data.g.add((gas_cylinder, SSN.hasProperty, volume_design_point0))
    data.g.add((volume_design_point0, RDF.type, SSN.Property))
    data.g.add((volume_design_point0, RDF.type, QUDT.Quantity))
    data.g.add((volume_design_point0, RDFS.label, Literal("volume design point")))
    data.g.add((volume_design_point0, QUDT.symbol, Literal("V0")))
    data.g.add((volume_design_point0, QUDT.hasQuantityKind, QUANTITYKIND.Volume))
    data.g.add((volume_design_point0, QUDT.unit, UNIT.M3))
    data.g.add((volume_design_point0, QUDT.value, Literal("0.000043", datatype=XSD.double)))
    # TODO: There might be sophisticated special data types for uncertainties in the future 12.2023
    data.g.add((volume_design_point0, SSN_SYSTEM.Accuracy, Literal("337e-9", datatype=XSD.double)))
    #source: Bachelorthesis Louis Hill

    wall_area = COMPONENT[gas_cylinder_id + "/A_w"]
    data.g.add((gas_cylinder, SSN.hasProperty, wall_area))
    data.g.add((wall_area, RDF.type, SSN.Property))
    data.g.add((wall_area, RDF.type, QUDT.Quantity))
    data.g.add((wall_area, RDFS.label, Literal("wall area")))
    data.g.add((wall_area, QUDT.symbol, Literal("A_w")))
    data.g.add((wall_area, QUDT.hasQuantityKind, QUANTITYKIND.Area))
    data.g.add((wall_area, QUDT.unit, UNIT.M2))
    data.g.add((wall_area, QUDT.value, Literal("0.00686", datatype=XSD.double)))
    # TODO: There might be sophisticated special data types for uncertainties in the future 12.2023
    data.g.add((wall_area, SSN_SYSTEM.Accuracy, Literal("38e-6", datatype=XSD.double)))
    #source: Bachelorthesis Louis Hill

    specific_surface_area = COMPONENT[gas_cylinder_id + "/s"]
    data.g.add((gas_cylinder, SSN.hasProperty, specific_surface_area))
    data.g.add((specific_surface_area, RDF.type, SSN.Property))
    data.g.add((specific_surface_area, RDF.type, QUDT.Quantity))
    data.g.add((specific_surface_area, RDFS.label, Literal("specific surface area")))
    data.g.add((specific_surface_area, QUDT.symbol, Literal("s")))
    data.g.add((specific_surface_area, QUDT.hasQuantityKind, QUANTITYKIND.InverseLength))
    data.g.add((specific_surface_area, QUDT.unit, UNIT["NUM-PER-M"]))
    data.g.add((specific_surface_area, QUDT.value, Literal("159.534883720930", datatype=XSD.double)))
    # TODO: There might be sophisticated special data types for uncertainties in the future 12.2023
    data.g.add((specific_surface_area, SSN_SYSTEM.Accuracy, Literal("1.531088979916640", datatype=XSD.double)))
    #source: Propagation of uncertainty according to Gauß

    # documentation this can probably be automated
    img = COMPONENT[gas_cylinder_id + "/img/IMG_gas_cylinder_mounted_in_hydropulser.jpg"]
    data.g.add((gas_cylinder, SDO.subjectOf, img))
    data.g.add((gas_cylinder, SDO.image, img))

    docs = COMPONENT[gas_cylinder_id + "/CAD"]
    data.g.add((gas_cylinder, SDO.subjectOf, docs))
    data.g.add((gas_cylinder, SDO.documentation, docs))

    thesis = COMPONENT[gas_cylinder_id + "/doc/report_210215_S436_Konstruktion_Aufbau_und_Inbetriebnahme_eines_Prüfaufbaus_zur_Messung_instationärer_Transportvorgänge_Hill.pdf"]
    data.g.add((gas_cylinder, SDO.subjectOf, thesis))
    data.g.add((gas_cylinder, SDO.documentation, thesis))

    datasheet = COMPONENT[gas_cylinder_id + "/doc/Zeichnungen_gesamt_Hill.pdf"]
    data.g.add((gas_cylinder, SDO.subjectOf, datasheet))
    data.g.add((gas_cylinder, SDO.documentation, datasheet))

    # rdf doc references
    docttl = COMPONENT[gas_cylinder_id + "/rdf.ttl"]
    data.g.add((docttl, RDF.type, FOAF.Document))
    data.g.add((docttl, FOAF.primaryTopic, gas_cylinder))

    docxml = COMPONENT[gas_cylinder_id + "/rdf.xml"]
    data.g.add((docxml, RDF.type, FOAF.Document))
    data.g.add((docxml, FOAF.primaryTopic, gas_cylinder))

    docjson = COMPONENT[gas_cylinder_id + "/rdf.json"]
    data.g.add((docjson, RDF.type, FOAF.Document))
    data.g.add((docjson, FOAF.primaryTopic, gas_cylinder))


    current_python_file_dir_path = Path(__file__).parent.resolve()
    dir_path = Path(f"{current_python_file_dir_path}/{gas_cylinder_id}")

    try:
        dir_path.mkdir()
    except FileExistsError:
        pass

    file_path = f"{dir_path}/rdf"
    print(data.g.serialize(destination=f"{file_path}.json", format="json-ld", auto_compact=True))
    print(data.g.serialize(destination=f"{file_path}.ttl", format="longturtle", encoding="utf-8"))
    print(data.g.serialize(destination=f"{file_path}.xml", format="xml"))

    gitlab_db_mdgen.generate_sensor_md(f'{dir_path}/')


if __name__ == '__main__':
    main()
