from pyshacl import validate

# TARGET SUBJECTS OF CONFIGURABLE CONFORMSTO-VALUE COMBINATION

shacl_graph = '''@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix schema: <http://schema.org/> .
@prefix ex: <http://www.example.org/> .

ex:ConformsToShapeTarget
    a sh:SPARQLTargetType ;
    rdfs:subClassOf sh:Target ;
    sh:labelTemplate "All Subjects that conform to {$conformsTo}" ;
    sh:parameter [
        sh:path dcterms:conformsTo ;
        sh:description "The shape that the focus nodes claim to conform to." ;
        sh:class sh:NodeShape ;
        sh:nodeKind sh:IRI ;
    ] ;
    sh:select """
        SELECT ?this
        WHERE {
            ?this <http://purl.org/dc/terms/conformsTo> $conformsTo .
        }
        """ .

ex:PersonShape
    a sh:NodeShape ;
    sh:property [
        sh:path schema:name ;
        sh:minCount 1 ;
    ] .

ex:USCitizenShape
    a sh:NodeShape ;
    sh:node ex:PersonShape ;
    sh:target [
        a ex:ConformsToShapeTarget ;
        dcterms:conformsTo ex:USCitizenShape ;
    ] ;
    sh:property [
        sh:path schema:addressCountry ;
        sh:hasValue "USA" ;
        sh:minCount 1 ;
    ] .

ex:UKCitizenShape
    a sh:NodeShape ;
    sh:node ex:PersonShape ;
    sh:target [
        a ex:ConformsToShapeTarget ;
        dcterms:conformsTo ex:UKCitizenShape ;
    ] ;
    sh:property [
        sh:path schema:addressCountry ;
        sh:hasValue "UK" ;
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
