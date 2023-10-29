import os
from pathlib import Path
from string import Template
from textwrap import dedent

from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS, DCTERMS, FOAF, SOSA

from pyKRAKEN.kraken import SDO, DBO


def generate_sensor_md(resource_dir):
    rdfdocname = "rdf.ttl"
    g = Graph().parse(resource_dir + rdfdocname)

    subjects = set([str(iri) for iri in g.subjects()])  # set of unique subjects as string
    rdfdoc = [iri for iri in subjects if rdfdocname in iri]
    if len(rdfdoc) != 1:
        raise LookupError("graph contains no subject or more than one subject that"
                          "might identify the imported graph document / file")
    rdfdoc = URIRef(rdfdoc[0])

    resource = g.value(subject=rdfdoc, predicate=FOAF.primaryTopic)

    if str(resource)[-1] == "/":
        raise ValueError("resource iri should not end in \"/\"")

    namespace_prefix, _, _ = g.compute_qname(resource)  # str(resource).rsplit("/")[-2]
    name = str(g.value(subject=resource, predicate=SDO.name, any=False))
    iri = str(resource)
    identifiers = list(g.objects(subject=resource, predicate=DCTERMS.identifier))
    uuid = [str(literal) for literal in identifiers if literal in iri]
    if len(uuid) != 1:
        raise LookupError("resource has no identifier or more than one identifier"
                          "that match its iri")
    uuid = uuid[0]

    gitpath = "https://git.rwth-aachen.de/fst-tuda/public/metadata/fst_measurement_equipment/-/"  # ask git for this
    rawpath = gitpath + "raw/main/" + str(uuid) + "/"
    blobpath = gitpath + "blob/main/" + str(uuid) + "/"

    base = iri.removesuffix(uuid)

    identifiers = [str(literal) for literal in identifiers if literal not in iri]

    mapping_header = {"prefix": namespace_prefix,
                      "name": name,
                      "iri": iri,
                      "uuid": uuid}

    mapping_id = [{"identifier": identifier} for identifier in identifiers]

    mapping_keywords = {"keywords": ", ".join([kw for kw in g.objects(subject=resource, predicate=SDO.keywords)])}

    mapping_image = [{"image": rawpath + str(img).removeprefix(base)}
                     for img in g.objects(subject=resource, predicate=SDO.image)]

    mapping_geninfo = {"comment": str(g.value(subject=resource, predicate=RDFS.comment, any=False)),
                       "manufacturer": str(g.value(subject=resource, predicate=SDO.manufacturer, any=False)),
                       "name": name,
                       "serialnumber": str(g.value(subject=resource, predicate=SDO.serialNumber, any=False)),
                       "procedure": str(g.value(subject=resource, predicate=SOSA.usedProcedure, any=False)),
                       "owner": str(g.value(subject=resource, predicate=DBO.owner, any=False)),
                       "maintainer": str(g.value(subject=resource, predicate=DBO.maintainedBy, any=False)),
                       "location": str(g.value(subject=resource, predicate=SDO.location, any=False)),
                       "modified": str(g.value(subject=resource, predicate=DCTERMS.modified, any=False)),
                       "related": str(g.value(subject=resource, predicate=DCTERMS.relation, any=False))}

    mapping_doc = [{"documentation": blobpath + str(doc).removeprefix(base),
                    "documentationlabel": str(doc).removeprefix(base)}
                   for doc in g.objects(subject=resource, predicate=SDO.documentation)]

    mapping_add_info = {"types": ", ".join([tp for tp in g.objects(subject=resource, predicate=RDF.type)])}

    form_header = Template(dedent("""\
    ## Sensor $name

    <div align="right">

    ### IRI: [`$iri`]($iri)
    ### UUID: `$uuid`
    """))

    form_id = Template(dedent("""### identifier: `$identifier`
    """))

    form_keywords = Template(dedent("""
    ## Keywords: $keywords
    """))

    form_image = Template(dedent("""
    <img width="400" src=$image>
    """))

    form_geninfo = Template(dedent("""
    ## General Info

    | property | value |
    |-:|:-|
    | comment: | $comment |
    | manufacturer: | $manufacturer |
    | name: | $name |
    | serial number: | $serialnumber |
    | used procedure: | $procedure |
    |-|-|
    | owner: | $owner |
    | maintainer: | $maintainer |
    | last known location: | $location |
    | last modification: | $modified |
    |-|-|
    | related resources: | $related |
    """))

    form_doc = Template(dedent("""| documentation: | [$documentationlabel]($documentation) |
    """))

    form_addinfo = Template(dedent("""
    <br clear="right"/>

    ## Additional Info

    &#160;

    | property | value |
    |-:|:-|
    | types: | $types |
    """))

    s = form_header.substitute(mapping_header)
    for mapping in mapping_id:
        s += form_id.substitute(mapping)
    s += dedent("""
    </div>
    """)
    s += form_keywords.substitute(mapping_keywords)
    for mapping in mapping_image:
        s += form_image.substitute(mapping)
    s += form_geninfo.substitute(mapping_geninfo)
    for mapping in mapping_doc:
        s += form_doc.substitute(mapping)
    s += form_addinfo.substitute(mapping_add_info)

    with open(resource_dir + "/README.md", "w") as f:
        print(s, file=f)


def generate_sensor_md_s_from_directory(sensors_directory_path: [str, Path] = ''):
    file_directory = Path(__file__).parent.resolve()
    search_directory = Path(f"{file_directory}/_generated/")

    with os.scandir(search_directory) as it:
    # TODO: Check whether insidethe directory are the awaited contents
        for entry in it:
            if entry.is_dir() and entry.name != ".git":
                generate_sensor_md(entry.path + "/")

    print("Succesfully created all md files")
