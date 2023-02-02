import os
from pyshacl import validate
from rdflib import Graph

# VALIDATION OF METADATA PROFILES
shapes_location = "shape-cache"
meta_shapefiles = ["AIMS-AP.shacl.ttl", "shacl-shacl.ttl"]
shape_graph = Graph()
for shapefile in meta_shapefiles:
    shape_graph.parse(f"{shapes_location}/{shapefile}")

with os.scandir(shapes_location) as shapefiles:
    for shapefile in shapefiles:
        if shapefile.name in meta_shapefiles:
            print(f"skipping meta shape {shapefile.name}\n")
            continue
        if shapefile.name.endswith(".ttl") and shapefile.is_file():

            print(shapefile.path)
            r = validate(shapefile.path,
                         data_graph_format="ttl",
                         shacl_graph=shape_graph,
                         inference="rdfs",
                         advanced=True,
                         debug=False)
            _, _, results_text = r

            print(results_text)
