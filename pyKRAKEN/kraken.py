from __future__ import annotations

from typing import List

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import DCAT, DCMITYPE, DCTERMS, RDF, RDFS, SOSA, SSN, FOAF
from uuid6 import uuid6

H5PATH_RDF_METADATA = "/rdf-metadata"  # could be an input instead, necessary if multiple graphs allowed

FST = Namespace("https://w3id.org/fst/resource/")
URNUUID = Namespace("urn:uuid:")
SDO = Namespace("https://schema.org/")
DBO = Namespace("https://dbpedia.org/ontology/")
QUDT = Namespace("https://qudt.org/schema/qudt/")
QUANTITYKIND = Namespace("https://qudt.org/vocab/quantitykind/")
UNIT = Namespace("https://qudt.org/vocab/unit/")
SSN_SYSTEM = Namespace("https://www.w3.org/ns/ssn/systems/")

# wrapper for graph to automate configuration and possibly behavior
class Kraken(object):
    """
    proxy Class for RDF metadata stored together with multidimensional arrays in an hdf5 file
    according to AIMS application profile.
    """
    # iri strategy object / function as input

    def __init__(self, filepath: str = None, base: [Namespace, URIRef] = None) -> None:
        if filepath is None:
            filepath = ""

        g = Graph(base=base)

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
                 name: str | None = None,
                 comment: str | None = None,
                 description: str | None = None,
                 seeAlso: [str] | [URIRef] | None = None,
                 conformsTo: [str] | [URIRef] | None = None,
                 subjectOf: URIRef | None = None,
                 image: URIRef | None = None,
                 documentation: URIRef | None = None,
                 rdftype: URIRef | None = None,
                 isHostedBy: URIRef | None = None,
                 keywords_list: [str] | None = None,) -> None:
        # how do we handle multiple occurence of properties?
        # list is fine on init, _property: list = property: list
        # what do we do on change after?
        # always add and remove duplicates?
        # always overwrite?
        # can we do methods with flag on setter?
        self.g = kraken.g
        self.iri = iri
        self.identifier = identifier  # maybe needs to be renamed because of collision with rdflib resource
        self.name = name
        self.comment = comment
        self.description = description
        self.seeAlso = seeAlso
        self.conformsTo = conformsTo
        self.subjectOf = subjectOf
        self.image = image
        self.documentation = documentation
        self.rdftype = rdftype
        self.isHostedBy = isHostedBy
        self.keywords_list = keywords_list

    @property
    def iri(self):
        return self._iri

    @iri.setter
    def iri(self, iri: URIRef | None):
        # maybe allow namespace instead of iri, then make iri ns + name
        # probably do this via accepting a dict like {"ns": ns, "id": id}
        if iri is None:
            self._uuid = uuid6()
            iri = URNUUID[str(self._uuid)]  # provide option to declare other namespaces
            self._iri = iri
            self.identifier = str(self._uuid)
        else:
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
    def name(self):
        names = self.g.objects(subject=self.iri, predicate=SDO.name)
        return [name.toPython() for name in names]

    @name.setter
    def name(self, name: str | None):
        # let subclasses override this
        if name is None:
            name = self.__class__.__name__ + "-" + str(self.identifier[0])

        self.g.add((self.iri, SDO.name, Literal(name)))

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
    def description(self):
        descriptions = self.g.objects(subject=self.iri, predicate=SDO.description)
        return [description.toPython() for description in descriptions]

    @description.setter
    def description(self, description: str | None):
        if description is None:
            return
        self.g.add((self.iri, SDO.description, Literal(description)))

    @property
    def seeAlso(self):
        see_also_generator = self.g.objects(subject=self.iri, predicate=RDFS.seeAlso)
        return [see_also.toPython() for see_also in see_also_generator]

    @seeAlso.setter
    def seeAlso(self, seeAlso: [str] | [URIRef] | None):
        if seeAlso is None:
            return

        for item in seeAlso:
            if isinstance(item, URIRef):
                self.g.add((self.iri, RDFS.seeAlso, item))
            elif isinstance(item, str):
                self.g.add((self.iri, RDFS.seeAlso, Literal(item)))
            else:
                # TODO:
                raise ValueError

    @property
    def conformsTo(self):
        conforms_to_generator = self.g.objects(subject=self.iri, predicate=DCTERMS.conformsTo)
        return [conforms_to_.toPython() for conforms_to_ in conforms_to_generator]

    @conformsTo.setter
    def conformsTo(self, conformsTo: [str] | [URIRef] | None):
        if conformsTo is None:
            return

        for item in conformsTo:
            if isinstance(item, URIRef):
                self.g.add((self.iri, DCTERMS.conformsTo, item))
            elif isinstance(item, str):
                self.g.add((self.iri, DCTERMS.conformsTo, Literal(item)))
            else:
                # TODO:
                raise ValueError

    @property
    def subjectOf(self):
        subjectOfs = self.g.objects(subject=self.iri, predicate=SDO.subjectOf)
        return [subjectOf.toPython() for subjectOf in subjectOfs]

    @subjectOf.setter
    def subjectOf(self, subjectOf):
        if subjectOf is None:
            return
        if not isinstance(subjectOf, URIRef):
            raise ValueError("input argument \"subjectOf\" must be a valid IRI")

        self.g.add((self.iri, SDO.subjectOf, subjectOf))

    @property
    def image(self):
        images = self.g.objects(subject=self.iri, predicate=SDO.image)
        return [image.toPython() for image in images]

    @image.setter
    def image(self, image):
        if image is None:
            return
        if not isinstance(image, URIRef):
            raise ValueError("input argument \"image\" must be a valid IRI")

        self.g.add((self.iri, SDO.image, image))

    @property
    def documentation(self):
        documentations = self.g.objects(subject=self.iri, predicate=SDO.documentation)
        return [documentation.toPython() for documentation in documentations]

    @documentation.setter
    def documentation(self, documentation):
        if documentation is None:
            return
        if not isinstance(documentation, URIRef):
            raise ValueError("input argument \"documentation\" must be a valid IRI")

        self.g.add((self.iri, SDO.documentation, documentation))

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

    @property
    def keywords_list(self):
        keywords_list = self.g.objects(subject=self.iri, predicate=DCTERMS.identifier)
        return [keyword.toPython() for keyword in keywords_list]

    @keywords_list.setter
    def keywords_list(self, keywords_list: [str] | None):
        if keywords_list is None:
            return
        for keyword in keywords_list:
            # TODO: Could keywords also be URIRefs? technical that should be possible but is there a relevant use case?
            #  -> terms with efficient multi language lookup and broad search (broader topic search through different keywords connected to the selected one(s))

            self.g.add((self.iri, SDO.keywords, Literal(keyword.strip())))


class PhysicalObject(Thing):
    def __init__(self, kraken: Kraken,
                 iri: URIRef | None = None,
                 identifier: str | None = None,
                 name: str | None = None,
                 comment: str | None = None,
                 subjectOf: URIRef | None = None,
                 image: URIRef | None = None,
                 documentation: URIRef | None = None,
                 rdftype: URIRef | None = None,
                 isHostedBy: URIRef | None = None,
                 owner: str | None = None,
                 manufacturer: str | None = None,
                 serialNumber: str | None = None):
        super().__init__(kraken, iri, identifier, name, comment, subjectOf, image, documentation, rdftype, isHostedBy)

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
                 name: str | None = None,
                 comment: str | None = None,
                 subjectOf: URIRef | None = None,
                 image: URIRef | None = None,
                 documentation: URIRef | None = None,
                 rdftype: URIRef | None = None,
                 isHostedBy: URIRef | None = None,
                 owner: str | None = None,
                 manufacturer: str | None = None,
                 serialNumber: str | None = None,
                 location: str | None = None):
        super().__init__(kraken, iri, identifier, name, comment, subjectOf, image, documentation,
                         rdftype, isHostedBy, owner, manufacturer, serialNumber)

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
            hasSensorCapability = URIRef("/".join([self.iri, hasSensorCapability.strip("/")]))

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
                 name: str | None = None,
                 comment: str | None = None,
                 subjectOf: URIRef | None = None,
                 image: URIRef | None = None,
                 documentation: URIRef | None = None,
                 rdftype: URIRef | None = None):
        super().__init__(kraken, iri, identifier, name, comment, subjectOf, image, documentation, rdftype)

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
                 unit: URIRef | None = None,
                 minValue=None,
                 maxValue=None,
                 iri: URIRef | None = None,
                 identifier: str | None = None,
                 name: str | None = None,
                 comment: str | None = None,
                 description: str | None = None,
                 seeAlso: [str] | [URIRef] | None = None,
                 conformsTo: [str] | [URIRef] | None = None,
                 subjectOf: URIRef | None = None,
                 image: URIRef | None = None,
                 documentation: URIRef | None = None,
                 rdftype: URIRef | None = None,
                 keywords_list: [str] | None = None,):
        super().__init__(kraken, iri, identifier, name, comment,
                         description=description,
                         seeAlso=seeAlso,
                         conformsTo=conformsTo,
                         subjectOf=subjectOf,
                         image=image,
                         documentation=documentation,
                         rdftype=rdftype,
                         keywords_list=keywords_list,)

        self.isPropertyOf = isPropertyOf
        self.value = value
        self.minValue = minValue
        self.maxValue = maxValue
        self.unit = unit
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

    @property
    def unit(self):
        return self.g.value(subject=self.iri, predicate=QUDT.unit, any=False).toPython()

    @unit.setter
    def unit(self, unit):
        if unit is None:
            return
        elif isinstance(unit, URIRef):
            self.g.add((self.iri, QUDT.unit, unit))
        elif isinstance(unit, str):
            self.g.add((self.iri, QUDT.unit, Literal(unit)))
        else:
            # TODO:
            raise ValueError



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
                 name: str | None = None,
                 comment: str | None = None,
                 subjectOf: URIRef | None = None,
                 image: URIRef | None = None,
                 documentation: URIRef | None = None,
                 rdftype: URIRef | None = None):
        super().__init__(kraken, isPropertyOf,
                         value=value,
                         minValue=minValue,
                         maxValue=maxValue,
                         iri=iri,
                         identifier=identifier,
                         name=name,
                         comment=comment,
                         subjectOf=subjectOf,
                         image=image,
                         documentation=documentation,
                         rdftype=rdftype)

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
        elif isinstance(unit, URIRef):
            self.g.add((self.iri, QUDT.unit, unit))
        elif isinstance(unit, str):
            self.g.add((self.iri, QUDT.unit, Literal(unit)))
        else:
            # TODO:
            raise ValueError

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
                 name: str | None = None,
                 comment: str | None = None,
                 subjectOf: URIRef | None = None,
                 image: URIRef | None = None,
                 documentation: URIRef | None = None,
                 rdftype: URIRef | None = None,
                 observedProperty: URIRef | None = None):
        # sosa:resultTime
        # sosa:phenomenonTime
        super().__init__(kraken, iri, identifier, name, comment, subjectOf, image, documentation, rdftype)

        if isinstance(hasResult, URIRef):
            hasResult = [hasResult]

        self.observedProperty = observedProperty
        self.hasResult = hasResult

        self.g.add((self.iri, RDF.type, SOSA.Observation))
        self.g.add((self.iri, SOSA.observedProperty, self.observedProperty))

        self.madeBySensor = self.g.value(
            predicate=SOSA.observes, object=self.observedProperty, any=False)
        self.hasFeatureOfInterest = self.g.value(
            subject=self.observedProperty, predicate=SSN.isPropertyOf, any=False)

        self.g.add((self.iri, SOSA.madeBySensor, self.madeBySensor))
        self.g.add((self.iri, SOSA.hasFeatureOfInterest, self.hasFeatureOfInterest))

        for element in self.hasResult:
            self.g.add((self.iri, SOSA.hasResult, element))

    def isMemberOf(self, iri: URIRef) -> Observation:
        self.g.add((iri, SOSA.hasMember, self.iri))
        return self


class ObservationCollection(Thing):
    def __init__(self, kraken: Kraken,
                 iri: URIRef | None = None,
                 identifier: str | None = None,
                 name: str | None = None,
                 comment: str | None = None,
                 subjectOf: URIRef | None = None,
                 image: URIRef | None = None,
                 documentation: URIRef | None = None,
                 rdftype: URIRef | None = None):
        # make this a more general "Collection", and combine with dcat:Catalog for results?

        # sosa:resultTime
        # sosa:phenomenonTime
        # sosa:madeBySensor
        # after those are implemented it may make sense to do ObservationCollection(Observation)
        super().__init__(kraken, iri, identifier, name, comment, subjectOf, image, documentation, rdftype)

        self.g.add((self.iri, RDF.type, SOSA.ObservationCollection))

    def isMemberOf(self, iri: URIRef) -> Observation:
        self.g.add((iri, SOSA.hasMember, self.iri))
        return self


class Result(Thing):
    def __init__(self, kraken: Kraken,
                 unit: URIRef,
                 h5path: str,
                 data=None,
                 iri: URIRef | None = None,
                 identifier: str | None = None,
                 name: str | None = None,
                 comment: str | None = None,
                 subjectOf: URIRef | None = None,
                 image: URIRef | None = None,
                 documentation: URIRef | None = None,
                 rdftype: URIRef | None = None,
                 creator: str | None = None):
        super().__init__(kraken, iri, identifier, name, comment, subjectOf, image, documentation, rdftype)
        accessurl = ""  # for now we only support same document references

        self.title = name
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
