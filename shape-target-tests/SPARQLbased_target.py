from pyshacl import validate

# TARGET SUBJECTS OF CONFORMSTO-VALUE COMBINATION

shacl_graph = '''@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix schema: <http://schema.org/> .
@prefix ex: <http://www.example.org/> .

ex:  # could just replace "ex" in SPARQL query, analog to dcterms:conformsTo
    sh:declare [
        sh:prefix "ex" ;
        sh:namespace "http://www.example.org/"^^xsd:anyURI ;
    ] .

ex:USCitizenShape
    a sh:NodeShape ;
    sh:target [
        a sh:SPARQLTarget ;
        sh:prefixes ex: ;
        sh:select """
            SELECT ?this
            WHERE {
                ?this <http://purl.org/dc/terms/conformsTo> ex:USCitizenShape .
            }
            """ ;
    ] ;
    sh:property [
        sh:path schema:addressCountry ;
        sh:hasValue "USA" ;
        sh:minCount 1 ;
    ] .
'''

data_graph = '''@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix schema: <http://schema.org/> .
@prefix ex: <http://www.example.org/> .

ex:Alice
    a schema:Person ;
    dcterms:conformsTo ex:USCitizenShape ;
    schema:addressCountry "USA" .

ex:Bob
    a schema:Person ;
    dcterms:conformsTo ex:USCitizenShape ;
    schema:addressCountry "UK" .

ex:Carol
    a schema:Person ;
    dcterms:conformsTo ex:UKCitizenShape ;
    schema:addressCountry "UK" .

ex:Dan
    a schema:Person ;
    dcterms:conformsTo ex:UKCitizenShape ;
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
