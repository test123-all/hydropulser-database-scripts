from __future__ import annotations

from typing import List, Union

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import DCAT, DCMITYPE, DCTERMS, RDF, RDFS, SOSA, SSN, SDO, FOAF
from uuid6 import uuid6

H5PATH_RDF_METADATA = "/rdf-metadata"  # could be an input instead, necessary if multiple graphs allowed

FST = Namespace("https://git.rwth-aachen.de/fst-tuda/.../")  # change to resolvable URL (e.g. project or wiki)
URNUUID = Namespace("urn:uuid:")
DBO = Namespace("http://dbpedia.org/ontology/")
QUDT = Namespace("http://qudt.org/schema/qudt/")
QUANTITYKIND = Namespace("http://qudt.org/vocab/quantitykind/")
UNIT = Namespace("http://qudt.org/vocab/unit/")
SSN_SYSTEM = Namespace("http://www.w3.org/ns/ssn/systems/")


# wrapper for graph to automate configuration and possibly behavior
class Kraken(object):
    """
    proxy Class for RDF metadata stored together with multidimensional arrays in an hdf5 file
    according to AIMS application profile.
    """
    # iri strategy object / function as input

    def __init__(self, filepath: str = None) -> None:
        if filepath is None:
            filepath = ""

        g = Graph()

        # could separate binds via subclass of namespace manager, or wrapper?
        g.bind("fst", FST)
        g.bind("uuid", URNUUID)
        g.bind("rdf", RDF)
        g.bind("rdfs", RDFS)
        g.bind("dcterms", DCTERMS)
        g.bind("dcmitype", DCMITYPE)
        g.bind("dcat", DCAT)
        g.bind("sosa", SOSA)
        g.bind("ssn", SSN)
        g.bind("schema", SDO)
        g.bind("dbo", DBO)
        g.bind("qudt", QUDT)
        g.bind("quantitykind", QUANTITYKIND)
        g.bind("unit", UNIT)
        g.bind("ssn-system", SSN_SYSTEM)
        g.bind("foaf", FOAF)

        self.g = g  # is this allowed? apparently
        self.filepath = filepath

        # something like: make new dict entry for each rdf:type, holding a new dict for entities of this type
        self.index = []


class Thing(object):
    def __init__(self, kraken: Kraken, iri: URIRef, label: str) -> None:
        # maybe allow namespace instead of iri, then make iri ns + name
        if iri is None:
            uuid = uuid6()
            iri = URNUUID[str(uuid)]

        # let subclasses override this
        if label is None:
            label = self.__class__.__name__ + "-" + str(uuid)

        self.g = kraken.g
        self.iri = iri
        self.label = label

        self.g.add((self.iri, RDFS.label, Literal(self.label)))

    @property
    def iri(self):
        return self.iri

    def isHostedBy(self, iri: URIRef) -> Thing:
        self.g.add((self.iri, SOSA.isHostedBy, iri))
        self.g.add((iri, SOSA.hosts, self.iri))
        self.g.add((iri, RDF.type, SOSA.Platform))
        # could be an attribute with set/get method instead?
        # return self for now, to enable method cascading (chaining)
        return self


class PhysicalObject(Thing):
    def __init__(self, kraken: Kraken, iri: URIRef, label: str, identifier: str, owner: str, manufacturer: str):
        super().__init__(kraken, iri, label)

        # all following properties actually indicate schema:Product
        self.identifier = identifier
        self.owner = owner  # alternatively use dcterms:rightsHolder
        self.manufacturer = manufacturer  # alternatively use schema:provider

        self.g.add((self.iri, RDF.type, DCMITYPE.PhysicalObject))

        self.g.add((self.iri, DCTERMS.identifier, Literal(self.identifier)))
        self.g.add((self.iri, DBO.owner, Literal(self.owner)))
        self.g.add((self.iri, SDO.manufacturer, Literal(self.manufacturer)))


class Sensor(PhysicalObject):  # Sensor(System), System(Thing) in the future
    def __init__(self, kraken: Kraken, iri: URIRef, label: str, identifier: str,
                 serialNumber: str, owner: str, manufacturer: str, location: str):
        super().__init__(kraken, iri, label, identifier, owner, manufacturer)

        self.serialNumber = serialNumber
        self.location = location

        # validation against shape here

        self.g.add((self.iri, RDF.type, SOSA.Sensor))
        self.g.add((self.iri, SDO.location, Literal(self.location)))
        self.g.add((self.iri, SDO.serialNumber, Literal(self.serialNumber)))

    def observes(self, iri: URIRef) -> Sensor:
        # technically, observing something makes anything a sosa:sensor
        self.g.add((self.iri, SOSA.observes, iri))
        return self


class Observation(Thing):
    def __init__(self, kraken: Kraken, iri: URIRef, label: str, madeBySensor: URIRef,
                 hasResult: Union[URIRef, List[URIRef]]):
        # sosa:resultTime
        # sosa:phenomenonTime
        super().__init__(kraken, iri, label)

        if isinstance(hasResult, URIRef):
            hasResult = [hasResult]

        self.madeBySensor = madeBySensor
        self.hasResult = hasResult

        self.g.add((self.iri, RDF.type, SOSA.Observation))
        self.g.add((self.iri, SOSA.madeBySensor, self.madeBySensor))

        self.observedProperty = self.g.value(
            subject=self.madeBySensor, predicate=SOSA.observes, any=False)
        self.hasFeatureOfInterest = self.g.value(
            subject=self.observedProperty, predicate=SSN.isPropertyOf, any=False)

        self.g.add((self.iri, SOSA.observedProperty, self.observedProperty))
        self.g.add((self.iri, SOSA.hasFeatureOfInterest,
                   self.hasFeatureOfInterest))

        for element in self.hasResult:
            self.g.add((self.iri, SOSA.hasResult, element))

    def isMemberOf(self, iri: URIRef) -> Observation:
        self.g.add((iri, SOSA.hasMember, self.iri))
        return self


class ObservationCollection(Thing):
    def __init__(self, kraken: Kraken, iri: URIRef, label: str):
        # make this a more general "Collection", and combine with dcat:Catalog for results?

        # sosa:resultTime
        # sosa:phenomenonTime
        # sosa:madeBySensor
        # after those are implemented it may make sense to do ObservationCollection(Observation)
        super().__init__(kraken, iri, label)

        self.g.add((self.iri, RDF.type, SOSA.ObservationCollection))


class ObservableProperty(Thing):
    def __init__(self, kraken: Kraken, iri: URIRef, label: str,
                 hasQuantityKind: URIRef, isPropertyOf: URIRef):
        super().__init__(kraken, iri, label)

        self.hasQuantityKind = hasQuantityKind
        self.isPropertyOf = isPropertyOf

        self.g.add((self.iri, RDF.type, SOSA.ObservableProperty))
        self.g.add((self.iri, RDF.type, QUDT.Quantity))
        self.g.add((self.iri, QUDT.hasQuantityKind, self.hasQuantityKind))
        # location?

        self.g.add((self.isPropertyOf, RDF.type, SOSA.FeatureOfInterest))
        self.g.add((self.isPropertyOf, SSN.hasProperty, self.iri))
        self.g.add((self.iri, SSN.isPropertyOf, self.isPropertyOf))


class Result(Thing):
    def __init__(self, kraken: Kraken, iri: URIRef, label: str, creator: str, unit: URIRef, h5path: str, data):
        super().__init__(kraken, iri, label)
        accessurl = ""  # for now we only support same document references

        (_, _, uuidstr) = self.g.compute_qname(self.iri)

        self.title = label
        self.creator = creator  # move to ObservationCollection = DatasetCollection
        self.unit = unit
        self.h5path = h5path + uuidstr
        self.data = data

        d = URIRef(accessurl + "#" + H5PATH_RDF_METADATA + self.h5path)

        self.g.add((self.iri, RDF.type, SOSA.Result))
        self.g.add((self.iri, RDF.type, QUDT.QuantityValue))
        self.g.add((self.iri, RDF.type, DCAT.Dataset))
        self.g.add((self.iri, DCTERMS.title, Literal(self.title)))
        self.g.add((self.iri, DCTERMS.creator, Literal(self.creator)))
        self.g.add((self.iri, QUDT.unit, self.unit))
        # use DCAT.distribution also?
        self.g.add((self.iri, QUDT.numericValue, d))
        # timestamp, t0, dt
        # maybe this needs to be a result collection ?

        self.g.add((d, RDF.type, DCAT.Distribution))
        self.g.add((d, DCAT.accessURL, URIRef(accessurl + "#" + self.h5path)))
