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
