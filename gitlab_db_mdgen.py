from string import Template
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS, FOAF

g = Graph().parse("test.ttl")
docname = "rdf.ttl"

subjects = set([str(iri) for iri in g.subjects()])  # set of unique subjects as string
doc = [iri for iri in subjects if docname in iri]
if len(doc) is not 1:
   raise LookupError("graph contains no subject or more than one subject that might identify the graph document / file")
doc = URIRef(doc[0])

resource = g.value(subject=doc, predicate=FOAF.primaryTopic)

if str(resource)[-1] is "/":
   raise ValueError("resource iri should not end in \"/\"")

namespace_qname = str(resource).rsplit("/")[-2]
label = str(g.value(subject=resource, predicate=RDFS.label))
iri = str(resource)

mapping1 = {"type": namespace_qname,
            "label": label,
            "iri": iri,
            "identifier": "1ed6c963-669f-62b7-8af6-3727686f020d"}
mapping2 = {"comment": "Drucksensor",
            "manufacturer": "Keller",
            "serialnumber": "1011240",
            "imageURL": "https://git.rwth-aachen.de/fst-tuda/projects/rdm/datasheets-mockup/-/raw/main/components/1ed6c2f8-282a-64b4-94d0-4ee51dfba10e/IMG_20190809_113156_Bokeh.jpg",
            "location": "Sirup Mischanlage",
            "doc": "1ed6c963-669f-62b7-8af6-3727686f020d/link-to-doc-directory"}

form1 = Template("""## $type $label

<div align="right">

### IRI: [`$iri`]($iri)
### ID: `$identifier`

</div>

""")

form2 = Template("""## General Info

<img align="right" width="400" src=$imageURL>

&#160;

| property | value |
|-:|:-|
| comment: | $comment |
| manufacturer: | $manufacturer |
| serial number: | $serialnumber |
|-|-|
| last known location: | $location |
| documentation: | $doc |

<br clear="right"/>

## Additional Info

&#160;

| property | value |
|-:|:-|""")

s = form1.substitute(mapping1)
s += form2.substitute(mapping2)

with open("test.md", "w") as f:
   print(s, file=f)
