from rdflib import Namespace, Literal
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
ns_root = "https://git.rwth-aachen.de/fst-tuda/projects/rdm/datasheets-mockup/"
FST = Namespace(ns_root + "-/blob/main/")
COMPONENT = Namespace(FST["component/"])
SUBSTANCE = Namespace(FST["substance/"])


data = Kraken()
data.g.bind("fst-component", COMPONENT)
data.g.bind("fst-substance", SUBSTANCE)

airspring_id = "1ed6c2f8-282a-64b4-94d0-4ee51dfba10e"  # str(uuid6())
air_id = "1ed6cc2c-da26-661f-92f3-02c4bb63c743"

# the component = the air spring
airspring = COMPONENT[airspring_id]
air = SUBSTANCE[air_id]
data.g.add((airspring, RDF.type, DCMITYPE.PhysicalObject))
data.g.add((airspring, DCTERMS.hasPart, air))
data.g.add((airspring, RDFS.label, Literal("air spring")))
data.g.add((airspring, DCTERMS.identifier, Literal(airspring_id)))
data.g.add((airspring, DCTERMS.identifier, Literal("Part-no.:TAB.026.134.R")))
data.g.add((airspring, DBO.owner, Literal("FST")))
data.g.add((airspring, SDO.manufacturer, Literal("Vibracoustic")))
data.g.add((airspring, SDO.serialNumber, Literal("4K0-616-001-E")))

# properties
displacement_area = COMPONENT[airspring_id + "/A_d"]
data.g.add((airspring, SSN.hasProperty, displacement_area))
data.g.add((displacement_area, RDF.type, SSN.Property))
data.g.add((displacement_area, RDF.type, QUDT.Quantity))
data.g.add((displacement_area, RDFS.label, Literal("displacement area")))
data.g.add((displacement_area, QUDT.symbol, Literal("A_d")))
data.g.add((displacement_area, QUDT.hasQuantityKind, QUANTITYKIND.Area))
data.g.add((displacement_area, QUDT.unit, UNIT.M2))
data.g.add((displacement_area, QUDT.value, Literal("-0.01362", datatype=XSD.double)))
data.g.add((displacement_area, RDFS.comment, Literal("negative direction")))

volume_design_point = COMPONENT[airspring_id + "/V1"]
data.g.add((airspring, SSN.hasProperty, volume_design_point))
data.g.add((volume_design_point, RDF.type, SSN.Property))
data.g.add((volume_design_point, RDF.type, QUDT.Quantity))
data.g.add((volume_design_point, RDFS.label, Literal("volume design point")))
data.g.add((volume_design_point, QUDT.symbol, Literal("V1")))
data.g.add((volume_design_point, QUDT.hasQuantityKind, QUANTITYKIND.Volume))
data.g.add((volume_design_point, QUDT.unit, UNIT.M3))
data.g.add((volume_design_point, QUDT.value, Literal("0.00292", datatype=XSD.double)))

volume_design_point0 = COMPONENT[airspring_id + "/V0"]
data.g.add((airspring, SSN.hasProperty, volume_design_point0))
data.g.add((volume_design_point0, RDF.type, SSN.Property))
data.g.add((volume_design_point0, RDF.type, QUDT.Quantity))
data.g.add((volume_design_point0, RDFS.label, Literal("volume design point")))
data.g.add((volume_design_point0, QUDT.symbol, Literal("V0")))
data.g.add((volume_design_point0, QUDT.hasQuantityKind, QUANTITYKIND.Volume))
data.g.add((volume_design_point0, QUDT.unit, UNIT.M3))
data.g.add((volume_design_point0, QUDT.value, Literal("0.00292", datatype=XSD.double)))

wall_area = COMPONENT[airspring_id + "/A_w"]
data.g.add((airspring, SSN.hasProperty, wall_area))
data.g.add((wall_area, RDF.type, SSN.Property))
data.g.add((wall_area, RDF.type, QUDT.Quantity))
data.g.add((wall_area, RDFS.label, Literal("wall area")))
data.g.add((wall_area, QUDT.symbol, Literal("A_w")))
data.g.add((wall_area, QUDT.hasQuantityKind, QUANTITYKIND.Area))
data.g.add((wall_area, QUDT.unit, UNIT.M2))
data.g.add((wall_area, QUDT.value, Literal("0.173", datatype=XSD.double)))

spec_surface_area = COMPONENT[airspring_id + "/s"]
data.g.add((airspring, SSN.hasProperty, spec_surface_area))
data.g.add((spec_surface_area, RDF.type, SSN.Property))
data.g.add((spec_surface_area, RDF.type, QUDT.Quantity))
data.g.add((spec_surface_area, RDFS.label, Literal("specific surface area")))
data.g.add((spec_surface_area, QUDT.symbol, Literal("s")))
data.g.add((spec_surface_area, QUDT.hasQuantityKind, QUANTITYKIND.InverseLength))
data.g.add((spec_surface_area, QUDT.unit, UNIT["NUM-PER-M"]))
data.g.add((spec_surface_area, QUDT.value, Literal("59.246575342465754", datatype=XSD.double)))

# documentation
img = COMPONENT[airspring_id + "/IMG_20190809_113156_Bokeh.jpg"]
data.g.add((airspring, SDO.subjectOf, img))
data.g.add((airspring, SDO.image, img))

docs = COMPONENT[airspring_id + "/CAD"]
data.g.add((airspring, SDO.subjectOf, docs))
data.g.add((airspring, SDO.documentation, docs))

datasheet = COMPONENT[airspring_id + "/CAD/air_spring/HH-AR-0521-000_TB_ZB_LUFTFEDER_LH_RH_EA.pdf"]
data.g.add((airspring, SDO.subjectOf, datasheet))
data.g.add((airspring, SDO.documentation, datasheet))

# rdf doc references
docttl = COMPONENT[airspring_id + "/rdf.ttl"]
data.g.add((docttl, RDF.type, FOAF.Document))
data.g.add((docttl, FOAF.primaryTopic, airspring))

docxml = COMPONENT[airspring_id + "/rdf.xml"]
data.g.add((docxml, RDF.type, FOAF.Document))
data.g.add((docxml, FOAF.primaryTopic, airspring))

docjson = COMPONENT[airspring_id + "/rdf.json"]
data.g.add((docjson, RDF.type, FOAF.Document))
data.g.add((docjson, FOAF.primaryTopic, airspring))

# documentation extended
if False:
    data.g.add((img, DCTERMS.subject, airspring))

    data.g.add((docs, RDF.type, DCAT.Catalog))
    data.g.add((docs, RDF.type, SDO.CreativeWorkSeries))
    data.g.add((docs, DCTERMS.title, Literal("CAD Vibracoustic Luftfeder")))
    data.g.add((docs, DCTERMS.description, Literal("CAD Daten und Technische Zeichnungen Vibracoustic Luftfeder")))
    data.g.add((docs, DCTERMS.identifier, Literal("git-commit-SHA:")))
    data.g.add((docs, SDO.version, Literal("1.0.0")))
    data.g.add((docs, SDO.url, docs))
    data.g.add((docs, DCTERMS.publisher, Literal("Manuel Rexer")))
    data.g.add((docs, DCTERMS.creator, Literal("Manuel Rexer")))
    data.g.add((docs, DCTERMS.created, Literal("22-07-19", datatype=XSD.date)))
    data.g.add((docs, DCTERMS.rightsHolder, Literal("Vibracoustic SE ")))
    data.g.add((docs, DCTERMS.subject, airspring))

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
    data.g.add((datasheet, DCTERMS.subject, airspring))
    data.g.add((docs, DCTERMS.hasPart, datasheet))

path = "C:/Users/NP/Documents/AIMS/datasheets-mockup/component/" + airspring_id + "/"
print(data.g.serialize(destination=path + "rdf.json", format="json-ld", auto_compact=True))
print(data.g.serialize(destination=path + "rdf.ttl", base=COMPONENT, format="longturtle"))
print(data.g.serialize(destination=path + "rdf.xml", base=COMPONENT, format="xml"))
