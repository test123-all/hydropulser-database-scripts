from __future__ import annotations

from typing import List

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
    def __init__(self, kraken: Kraken,
                 iri: URIRef | None = None,
                 identifier: URIRef | str | None = None,
                 label: str | None = None,
                 comment: str | None = None,
                 rdftype: URIRef | None = None,
                 isHostedBy: URIRef | None = None) -> None:
        # how do we handle multiple occurence of properties?
        # list is fine on init, _property: list = property: list
        # what do we do on change after?
        # always add and remove duplicates?
        # always overwrite?
        # can we do methods with flag on setter?
        self.g = kraken.g
        self.iri = iri
        self.identifier = identifier  # maybe needs to be renamed because of collision with rdflib resource
        self.label = label
        self.comment = comment
        self.rdftype = rdftype
        self.isHostedBy = isHostedBy

    @property
    def iri(self):
        return self._iri

    @iri.setter
    def iri(self, iri: URIRef | None):
        # maybe allow namespace instead of iri, then make iri ns + label
        # probably do this via accepting a dict like {"ns": ns, "id": id}
        if iri is None:
            self._uuid = uuid6()
            self.identifier = str(self._uuid)
            iri = URNUUID[str(self._uuid)]  # provide option to declare other namespaces
        self._iri = iri

    @property
    def identifier(self):
        identifiers = self.g.objects(subject=self.iri, predicate=DCTERMS.identifier)
        return [identifier.toPython() for identifier in identifiers]

    @identifier.setter
    def identifier(self, identifier: URIRef | str | None):
        if identifier is None:
            return
        if not isinstance(identifier, URIRef):
            identifier = Literal(identifier)

        self.g.add((self.iri, DCTERMS.identifier, identifier))

    @property
    def label(self):
        labels = self.g.objects(subject=self.iri, predicate=RDFS.label)
        return [label.toPython() for label in labels]

    @label.setter
    def label(self, label: str | None):
        # let subclasses override this
        if label is None:
            label = self.__class__.__name__ + "-" + str(self.identifier[0])

        self.g.add((self.iri, RDFS.label, Literal(label)))

    @property
    def comment(self):
        comments = self.g.objects(subject=self.iri, predicate=RDFS.comment)
        return [comment.toPython() for comment in comments]

    @comment.setter
    def comment(self, comment: str | None):
        if comment is None:
            return
        self.g.add((self.iri, RDFS.comment, Literal(comment)))

    @property
    def rdftype(self):
        types = self.g.objects(subject=self.iri, predicate=RDF.type)
        return [rdftype for rdftype in types]

    @rdftype.setter
    def rdftype(self, rdftype):
        if rdftype is None:
            return
        if not isinstance(rdftype, URIRef):
            raise ValueError("input argument \"rdftype\" must be a valid IRI")

        self.g.add((self.iri, RDF.type, rdftype))

    @property
    def isHostedBy(self):
        hosts = self.g.objects(subject=self.iri, predicate=SOSA.isHostedBy)
        return hosts

    @isHostedBy.setter
    def isHostedBy(self, iri: URIRef | None):
        if iri is None:
            return
        if not isinstance(iri, URIRef):
            raise ValueError("value of \"isHostedBy\" must be a valid IRI")

        self.g.add((self.iri, SOSA.isHostedBy, iri))
        self.g.add((iri, SOSA.hosts, self.iri))
        self.g.add((iri, RDF.type, SOSA.Platform))


class PhysicalObject(Thing):
    def __init__(self, kraken: Kraken,
                 iri: URIRef | None = None,
                 identifier: str | None = None,
                 label: str | None = None,
                 comment: str | None = None,
                 rdftype: URIRef | None = None,
                 isHostedBy: URIRef | None = None,
                 owner: str | None = None,
                 manufacturer: str | None = None,
                 serialNumber: str | None = None):
        super().__init__(kraken, iri, identifier, label, comment, rdftype, isHostedBy)

        # all following properties actually indicate schema:Product
        self.owner = owner  # alternatively use dcterms:rightsHolder
        self.manufacturer = manufacturer  # alternatively use schema:provider
        self.serialNumber = serialNumber

        self.g.add((self.iri, RDF.type, DCMITYPE.PhysicalObject))

        self.g.add((self.iri, DBO.owner, Literal(self.owner)))
        self.g.add((self.iri, SDO.manufacturer, Literal(self.manufacturer)))
        self.g.add((self.iri, SDO.serialNumber, Literal(self.serialNumber)))


class Sensor(PhysicalObject):  # Sensor(System), System(Thing) in the future
    def __init__(self, kraken: Kraken,
                 hasSensorCapability: URIRef | str | None = None,
                 iri: URIRef | None = None,
                 identifier: str | None = None,
                 label: str | None = None,
                 comment: str | None = None,
                 rdftype: URIRef | None = None,
                 isHostedBy: URIRef | None = None,
                 owner: str | None = None,
                 manufacturer: str | None = None,
                 serialNumber: str | None = None,
                 location: str | None = None):
        super().__init__(kraken, iri, identifier, label, comment, rdftype,
                         isHostedBy, owner, manufacturer, serialNumber)

        self.hasSensorCapability = hasSensorCapability
        self.location = location
        # observes
        self.g.add((self.iri, SDO.location, Literal(self.location)))

    @property
    def hasSensorCapability(self):
        capabilities = [capability for capability in self.g.objects(subject=self.iri,
                                                                    predicate=SSN_SYSTEM.hasSystemCapability)
                        if any([[rdftype == SSN_SYSTEM.MeasurementRange for rdftype
                                 in self.g.objects(subject=sysproperty, predicate=RDF.type)]
                                for sysproperty in self.g.objects(subject=capability,
                                                                  predicate=SSN.hasProperty)])]
        return capabilities

    @hasSensorCapability.setter
    def hasSensorCapability(self, hasSensorCapability):
        if not isinstance(hasSensorCapability, URIRef):  # assume its string
            hasSensorCapability = "/".join([self.iri, hasSensorCapability.strip("/")])

        self.g.add((self.iri, RDF.type, SOSA.Sensor))
        self.g.add((self.iri, SSN_SYSTEM.hasSystemCapability, hasSensorCapability))

    def observes(self, prop: URIRef) -> Sensor:
        self.g.add((self.iri, SOSA.observes, prop))

        self.g.add((prop, RDF.type, SOSA.ObservableProperty))
        feature = self.g.value(subject=prop, predicate=SSN.isPropertyOf)
        self.g.add((feature, RDF.type, SOSA.FeatureOfInterest))
        return self


class SensorCapability(Thing):
    def __init__(self, kraken: Kraken,
                 hasSystemProperty: URIRef | None = None,
                 iri: URIRef | None = None,
                 identifier: str | None = None,
                 label: str | None = None,
                 comment: str | None = None,
                 rdftype: URIRef | None = None):
        super().__init__(kraken, iri, identifier, label, comment, rdftype)

        self.hasSystemProperty = hasSystemProperty

        self.g.add((self.iri, RDF.type, SSN.Property))
        self.g.add((self.iri, RDF.type, SSN_SYSTEM.SystemCapability))

    @property
    def hasSystemProperty(self):
        systemproperties = self.g.objects(subject=self.iri, predicate=SSN_SYSTEM.hasSystemProperty)
        return [systemproperty.toPython() for systemproperty in systemproperties]

    @hasSystemProperty.setter
    def hasSystemProperty(self, hasSystemProperty):
        if hasSystemProperty is None:
            return
        if not isinstance(hasSystemProperty, URIRef):  # assume its string
            hasSystemProperty = Literal("/".join([self.iri, hasSystemProperty.strip("/")]))

        self.g.add((self.iri, SSN_SYSTEM.hasSystemProperty, hasSystemProperty))


class Property(Thing):
    def __init__(self, kraken: Kraken,
                 isPropertyOf: URIRef,
                 value=None,
                 minValue=None,
                 maxValue=None,
                 iri: URIRef | None = None,
                 identifier: str | None = None,
                 label: str | None = None,
                 comment: str | None = None,
                 rdftype: URIRef | None = None,):
        super().__init__(kraken, iri, identifier, label, comment, rdftype)

        self.isPropertyOf = isPropertyOf
        self.value = value
        self.minValue = minValue
        self.maxValue = maxValue
        # location
        # propertyID

        self.g.add((self.iri, RDF.type, SSN.Property))

    @property
    def isPropertyOf(self):
        entities = self.g.objects(subject=self.iri, predicate=SSN.isPropertyOf)
        return [entity.toPython() for entity in entities]

    @isPropertyOf.setter
    def isPropertyOf(self, isPropertyOf):
        if isPropertyOf is None:
            raise ValueError("input argument \"isPropertyOf\" is missing")

        self.g.add((self.iri, SSN.isPropertyOf, isPropertyOf))
        self.g.add((isPropertyOf, SSN.hasProperty, self.iri))

    @property
    def value(self):
        return self.g.value(subject=self.iri, predicate=SDO.value, any=False).toPython()

    @value.setter
    def value(self, value):
        if value is None:
            return

        self.g.add((self.iri, SDO.value, Literal(value)))

    @property
    def minValue(self):
        return self.g.value(subject=self.iri, predicate=SDO.minValue, any=False).toPython()

    @minValue.setter
    def minValue(self, minValue):
        if minValue is None:
            return

        self.g.add((self.iri, SDO.minValue, Literal(minValue)))

    @property
    def maxValue(self):
        return self.g.value(subject=self.iri, predicate=SDO.maxValue, any=False).toPython()

    @maxValue.setter
    def maxValue(self, maxValue):
        if maxValue is None:
            return

        self.g.add((self.iri, SDO.maxValue, Literal(maxValue)))


class PropertyValue(Property):
    def __init__(self, kraken: Kraken,
                 isPropertyOf: URIRef,
                 name: str,
                 value,
                 minValue=None,
                 maxValue=None,
                 iri: URIRef | None = None,
                 identifier: str | None = None,
                 label: str | None = None,
                 comment: str | None = None,
                 rdftype: URIRef | None = None):
        super().__init__(kraken, isPropertyOf, value, minValue, maxValue, iri, identifier, label, comment, rdftype)

        self.name = name

        self.g.add((self.iri, RDF.type, SDO.PropertyValue))

    @property
    def name(self):
        return self.g.value(subject=self.iri, predicate=SDO.name, any=False).toPython()

    @name.setter
    def name(self, name):
        if name is None:
            return

        self.g.add((self.iri, SDO.name, Literal(name)))


class Quantity(Property):
    def __init__(self, kraken: Kraken,
                 isPropertyOf: URIRef,
                 hasQuantityKind: URIRef,
                 value=None,
                 minValue=None,
                 maxValue=None,
                 unit: URIRef | None = None,
                 symbol: str | None = None,
                 iri: URIRef | None = None,
                 identifier: str | None = None,
                 label: str | None = None,
                 comment: str | None = None,
                 rdftype: URIRef | None = None):
        super().__init__(kraken, isPropertyOf, value, minValue, maxValue, iri, identifier, label, comment, rdftype)

        self.hasQuantityKind = hasQuantityKind
        self.unit = unit
        self.symbol = symbol

        self.g.add((self.iri, RDF.type, QUDT.Quantity))

    @property
    def hasQuantityKind(self):
        return self.g.value(subject=self.iri, predicate=QUDT.hasQuantityKind, any=False).toPython()

    @hasQuantityKind.setter
    def hasQuantityKind(self, hasQuantityKind):
        if hasQuantityKind is None:
            raise ValueError("input argument \"hasQuantityKind\" is missing")

        self.g.add((self.iri, QUDT.hasQuantityKind, hasQuantityKind))

    @property
    def unit(self):
        return self.g.value(subject=self.iri, predicate=QUDT.unit, any=False).toPython()

    @unit.setter
    def unit(self, unit):
        if unit is None:
            return

        self.g.add((self.iri, QUDT.unit, unit))

    @property
    def symbol(self):
        return self.g.value(subject=self.iri, predicate=QUDT.hasQuantityKind, any=False).toPython()

    @symbol.setter
    def symbol(self, symbol):
        if symbol is None:
            return

        self.g.add((self.iri, QUDT.symbol, Literal(symbol)))


class Observation(Thing):
    def __init__(self, kraken: Kraken,
                 hasResult: URIRef | List[URIRef],
                 iri: URIRef | None = None,
                 identifier: str | None = None,
                 label: str | None = None,
                 comment: str | None = None,
                 rdftype: URIRef | None = None,
                 madeBySensor: URIRef | None = None):
        # sosa:resultTime
        # sosa:phenomenonTime
        super().__init__(kraken, iri, identifier, label, comment, rdftype)

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
    def __init__(self, kraken: Kraken,
                 iri: URIRef | None = None,
                 identifier: str | None = None,
                 label: str | None = None,
                 comment: str | None = None,
                 rdftype: URIRef | None = None):
        # make this a more general "Collection", and combine with dcat:Catalog for results?

        # sosa:resultTime
        # sosa:phenomenonTime
        # sosa:madeBySensor
        # after those are implemented it may make sense to do ObservationCollection(Observation)
        super().__init__(kraken, iri, identifier, label, comment, rdftype)

        self.g.add((self.iri, RDF.type, SOSA.ObservationCollection))


class Result(Thing):
    def __init__(self, kraken: Kraken,
                 unit: URIRef,
                 h5path: str,
                 data=None,
                 iri: URIRef | None = None,
                 identifier: str | None = None,
                 label: str | None = None,
                 comment: str | None = None,
                 rdftype: URIRef | None = None,
                 creator: str | None = None):
        super().__init__(kraken, iri, identifier, label, comment, rdftype)
        accessurl = ""  # for now we only support same document references

        self.title = label
        self.creator = creator  # move to ObservationCollection = DatasetCollection
        self.unit = unit
        self.h5path = h5path  # we assume data is already at name = h5path
        if data is not None:  # if data is provided we assert name = uuid
            self.h5path += self.identifier
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
