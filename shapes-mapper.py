import os
from pyshacl import validate
from rdflib import Graph

# VALIDATION OF METADATA PROFILES
# shapes_location = "shape-cache"
shapes_location = "C:/Users/NP/Documents/AIMS/usecase/shapes"
meta_shapefiles = ["AIMS-AP.shacl.ttl", "shacl-shacl.ttl"]
shape_graph = Graph()
for shapefile in meta_shapefiles:
    shape_graph.parse(f"shape-cache/{shapefile}")

for root, _, filenames in os.walk(shapes_location):
    for filename in filenames:
        if filename in meta_shapefiles:
            print(f"skipping meta shape {filename}\n")
            continue
        if filename.endswith(".ttl"):
            filepath = "/".join([root, filename])

            print(filepath)
            r = validate(filepath,
                         data_graph_format="ttl",
                         shacl_graph=shape_graph,
                         inference="rdfs",
                         advanced=True,
                         debug=False)
            _, _, results_text = r

            print(results_text)
