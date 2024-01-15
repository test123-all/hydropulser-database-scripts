from pyshacl import validate

# TARGET SUBJECTS OF CONFIGURABLE CONFORMSTO-VALUE COMBINATION

shacl_graph = '''@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix schema: <http://schema.org/> .
@prefix ex: <http://www.example.org/> .

ex:PersonShape
    a sh:NodeShape ;
    sh:property [
        sh:path schema:name ;
        sh:minCount 1 ;
    ] .

ex:USCitizenShape
    a sh:NodeShape ;
    sh:node ex:PersonShape ;
    sh:property [
        sh:path schema:addressCountry ;
        sh:hasValue "USA" ;
        sh:minCount 1 ;
    ] .

ex:UKCitizenShape
    a sh:NodeShape ;
    sh:node ex:PersonShape ;
    sh:property [
        sh:path schema:addressCountry ;
        sh:hasValue "UK" ;
        sh:minCount 1 ;
    ] .
'''

data_graph = '''@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix schema: <http://schema.org/> .
@prefix ex: <http://www.example.org/> .

ex:Alice
    a schema:Person ;
    sh:shapesGraph ex:USCitizenShape ;
    schema:addressCountry "USA" .

ex:Bob
    a schema:Person ;
    sh:shapesGraph ex:USCitizenShape ;
    schema:addressCountry "UK" .

ex:Carol
    a schema:Person ;
    sh:shapesGraph ex:UKCitizenShape ;
    schema:addressCountry "UK" .

ex:Dan
    a schema:Person ;
    sh:shapesGraph ex:UKCitizenShape ;
    schema:addressCountry "USA" .
'''

_, _, results_text = validate(data_graph,
                              data_graph_format="ttl",
                              shacl_graph=shacl_graph,
                              shacl_graph_format="ttl",
                              inference="rdfs",
                              advanced=True,
                              debug=False)

print(results_text)
