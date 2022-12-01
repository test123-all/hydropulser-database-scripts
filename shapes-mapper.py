import os
from pyshacl import validate
from rdflib import Graph
from rdflib.namespace import RDF, SH

g = Graph()
g.parse("shapes/Thing.shacl.ttl")

# fail if no shape found
shapes = g[: RDF.type: SH.NodeShape]
try:
    shape = next(shapes)
except StopIteration:
    raise LookupError("no shapes found in source file!")

# fail if another shape found
try:
    next(shapes)
except StopIteration:
    pass
else:
    raise LookupError("more than one shape found in source file!")


for o in g[shape: SH.property]:
    print(o)


# VALIDATION

with os.scandir("shapes") as it:
    for entry in it:
        if entry.name.endswith(".ttl") and entry.is_file():

            print(entry.path)
            r = validate(entry.path,
                         data_graph_format="ttl",
                         inference="rdfs",
                         debug=False)
            conforms, results_graph, results_text = r

            print(results_text)
