from string import Template
from rdflib import Graph, URIRef
from rdflib.namespace import RDFS, DCTERMS, SDO, FOAF

resource_dir = "C:/Users/NP/Documents/AIMS/datasheets-mockup/component/" \
               "1ed6c2f8-282a-64b4-94d0-4ee51dfba10e"
g = Graph().parse(resource_dir + "/rdf.ttl")
rdfdocname = "rdf.ttl"

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
label = str(g.value(subject=resource, predicate=RDFS.label, any=False))
iri = str(resource)
identifiers = list(g.objects(subject=resource, predicate=DCTERMS.identifier))
uuid = [str(literal) for literal in identifiers if literal in iri]
if len(uuid) != 1:
    raise LookupError("resource has no identifier or more than one identifier"
                      "that match its iri")
uuid = uuid[0]
identifiers = [str(literal) for literal in identifiers if literal not in iri]


mapping_header = {"prefix": namespace_prefix,
                  "label": label,
                  "iri": iri,
                  "uuid": uuid}

mapping_id = [{"identifier": identifier} for identifier in identifiers]

mapping_geninfo = {"comment": str(g.value(subject=resource, predicate=RDFS.comment, any=False)),
                   "manufacturer": str(g.value(subject=resource, predicate=SDO.manufacturer, any=False)),
                   "serialnumber": str(g.value(subject=resource, predicate=SDO.serialNumber, any=False)),
                   "image": str(g.value(subject=resource, predicate=SDO.image, any=False).replace("/blob/", "/raw/")),
                   "location": str(g.value(subject=resource, predicate=SDO.location, any=False))}

mapping_doc = [{"documentation": str(doc)} for doc in g.objects(subject=resource, predicate=SDO.documentation)]


form_header = Template("""## $prefix $label

<div align="right">

### IRI: [`$iri`]($iri)
### UUID: `$uuid`
""")

form_id = Template("""### identifier: `$identifier`
""")

form_geninfo = Template("""
</div>

## General Info

<img align="right" width="400" src=$image>

&#160;

| property | value |
|-:|:-|
| comment: | $comment |
| manufacturer: | $manufacturer |
| serial number: | $serialnumber |
|-|-|
| last known location: | $location |
""")

form_doc = Template("""| documentation: | $documentation |
""")

form_addinfo = Template("""
<br clear="right"/>

## Additional Info

&#160;

| property | value |
|-:|:-|
""")

s = form_header.substitute(mapping_header)
for mapping in mapping_id:
    s += form_id.substitute(mapping)
s += form_geninfo.substitute(mapping_geninfo)
for mapping in mapping_doc:
    s += form_doc.substitute(mapping)
s += form_addinfo.substitute()

with open(resource_dir + "/page.md", "w") as f:
    print(s, file=f)
