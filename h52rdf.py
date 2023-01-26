from itertools import chain
from datetime import datetime
from urllib.parse import quote
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD, DCTERMS, SOSA, SDO
from pyKRAKEN.kraken import (FST, QUANTITYKIND, UNIT, Kraken, PhysicalObject, ObservationCollection,
                             Observation, Quantity, Sensor, Result)
import h5py


def safeval(val):
    if isinstance(val, bytes):
        val = val.decode(encoding="latin-1", errors="replace")
    return val


def confirmattr(obj, expectedkey, expectedval=None):
    try:
        val = obj.attrs[expectedkey]
    except KeyError:
        print("object "+obj.name+" does not have expected attr "+expectedkey)
        return False

    if expectedval is None:
        return True

    val = safeval(val)
    if not val == expectedval:
        print("object " + obj.name + " has attribute " + expectedkey + " with value "
              + val + " instead of expected value " + expectedval)
        return False

    return True


filepath_source = "data/KF_80_2900.h5"
filepath = filepath_source.removesuffix(".h5") + "_rdf_embedded.h5"

TRNS = Namespace(FST["testrig/HydraulicSmall/"])
data = Kraken()

sourcefile = h5py.File(filepath_source, "r")
for h5run in sourcefile.values():
    if not confirmattr(h5run, expectedkey="kkn_CLASS", expectedval="MSMTRUN"):
        continue

    h5testrigname = safeval(h5run.attrs["testrig_name"]).lstrip("/").rsplit("/")[-1]
    match h5testrigname:
        case "hydraulic_small":
            testriglabel = "small test rig for displacement pumps"
        case _:
            testriglabel = h5testrigname

    testrig = PhysicalObject(data, iri=URIRef(TRNS.rstrip("/")), identifier=h5testrigname, label=testriglabel, owner="FST", manufacturer="FST")

    h5testrig = h5run["test_rig"]

    for h5actor in chain(h5testrig["actors"].values(), h5testrig["components"].values()):
        actorname = h5actor.name.rsplit("/")[-1]
        manufacturer = safeval(h5actor.attrs["manufacturer"])
        identifier = safeval(h5actor.attrs["type"])  # should be actual identifier
        # all of this should be items in lookup service > match uuid by name
        match actorname:  # make this a dictionary in the meantime?
            case "ball_valve":
                actorname = "BallValve"
                actorlabel = "electric ball valve"
                propname = TRNS["BallValve/FlowCoefficient"]
                proplabel = "flow coefficient of ball valve"
                propqkind = QUANTITYKIND.VolumeFlowRate
                propfeature = testrig.iri
            case "e-motor":
                actorname = "ElectricMotor"
                actorlabel = "electric motor for the pump shaft"
                propname = TRNS["rotational_speed"]
                proplabel = "rotational speed of pump shaft"
                propqkind = QUANTITYKIND["REV-PER-MIN"]
                propfeature = testrig.iri
            case "electric_drive_ball_valve":
                actorname = "BallValve/ElectricDrive"
                actorlabel = "electric drive for the ball valve"
                propname = TRNS["valve_position"]
                proplabel = "position of ball valve"
                propqkind = QUANTITYKIND.PERCENT
                propfeature = TRNS["BallValve"]  # lets hope there are no weird files where this does not work
            case "frequency_converter":
                actorname = "ElectricMotor/InverterDrive"  # probably this is a ssn:hasSubsystem situation
                actorlabel = "inverter drive"
                propname = TRNS["rotational_speed"]
                proplabel = "rotational speed of electric motor"
                propqkind = QUANTITYKIND["REV-PER-MIN"]
                propfeature = TRNS["ElectricMotor"]  # lets hope there are no weird files where this does not work
            case "needle_valve":
                actorname = "NeedleValve"
                actorlabel = "needle valve"
                propname = TRNS["NeedleValve/FlowCoefficient"]
                proplabel = "flow coefficient of needle valve"
                propqkind = QUANTITYKIND.VolumeFlowRate
                propfeature = testrig.iri
            case "heat exchanger":
                actorname = "HeatExchanger"
                actorlabel = "heat exchanger"
                propname = TRNS["temperature_tank"]  # <HydraulicFluid/>Temperature
                proplabel = "temperature of hydraulic fluid at tank"
                propqkind = QUANTITYKIND.Temperature
                propfeature = testrig.iri  # <HydraulicFluid/>Temperature
            case "oil_filter":
                actorname = "OilFilter"
                actorlabel = "oil filter"
                propname = TRNS["ParticleNumberDensity"]  # <HydraulicFluid/>ParticleNumberDensity
                proplabel = "number density of contamination particles in hydraulic fluid"
                propqkind = QUANTITYKIND.ParticleNumberDensity
                propfeature = testrig.iri  # <HydraulicFluid/>ParticleNumberDensity
            case _:
                raise LookupError("unrecognized componant or actor name")

        actor = PhysicalObject(data, iri=TRNS[actorname], identifier=identifier, label=actorlabel, comment=actorlabel,
                               isHostedBy=testrig.iri, owner="FST", manufacturer=manufacturer, serialNumber=identifier)
        actuatedproperty = Quantity(data, hasQuantityKind=propqkind, isPropertyOf=propfeature, iri=propname, label=proplabel)
        data.g.add((actor.iri, RDF.type, SOSA.Actuator))
        data.g.add((actor.iri, SOSA.actsOnProperty, actuatedproperty.iri))

    # ./operation/nom_rot_speed > actuatedProperty @FoI = Pump, actor = e motor, FU
    # ./operation/nom_temp > actuatedProperty @FoI = oil, actor = heat ex
    # the above can be results of actuations?
    # ./operation/hydraulic_oil > property
    h5pump = h5run["unit_under_test"]
    pumpname = safeval(h5run.attrs["pump_type"])  # pumps should be items in lookup service, match by this
    manufacturer = safeval(h5run.attrs["pump_manufacturer"])
    pump = PhysicalObject(data, iri=TRNS[pumpname], identifier=pumpname, label=pumpname, 
                          isHostedBy=testrig.iri, owner="FST", manufacturer=manufacturer)
    # ./geometry > property @FoI Pump

    h5pipelines = h5run["pipelines/measured"]
    for obj in h5pipelines.values():
        h5pipeline = obj["scaled"]
        pipename = obj.name.rsplit("/")[-1]
        if not confirmattr(h5pipeline, expectedkey="kkn_CLASS", expectedval="PIPELINE"):
            continue

        instruments = list(h5pipeline["instruments"].values())
        if len(instruments) != 1:
            raise LookupError("more instruments than expected found for " + pipename)
        sensor = instruments[0]
        sensortype = safeval(sensor.attrs["device_type"])
        if confirmattr(sensor, "manufacturer"):
            manufacturer = safeval(sensor.attrs["manufacturer"])
        elif confirmattr(sensor, "device_manufacturer"):
            manufacturer = safeval(sensor.attrs["device_manufacturer"])
        else:
            manufacturer = "unknown"
        serialnumber = safeval(sensor.attrs["serial_number"])
        sensoriri = TRNS[quote(serialnumber, safe='')]

        match pipename:
            case "pressure_1":
                sensorlabel = "pressure sensor"
                propname = TRNS["pressure_1"]
                proplabel = "pressure at measurement location 1"
                propqkind = QUANTITYKIND.Pressure
                propfeature = testrig.iri
            case "pressure_2":
                sensorlabel = "pressure sensor"
                propname = TRNS["pressure_2"]
                proplabel = "pressure at measurement location 2"
                propqkind = QUANTITYKIND.Pressure
                propfeature = testrig.iri
            case "pressure_3":
                sensorlabel = "pressure sensor"
                propname = TRNS["pressure_3"]
                proplabel = "pressure at measurement location 3"
                propqkind = QUANTITYKIND.Pressure
                propfeature = testrig.iri
            case "rotational_speed":
                sensorlabel = "rotational speed sensor"
                propname = TRNS["rotational_speed"]
                proplabel = "rotational speed of pump shaft"
                propqkind = QUANTITYKIND["REV-PER-MIN"]
                propfeature = testrig.iri
            case "torque":
                sensorlabel = "torque sensor"
                propname = TRNS["torque"]
                proplabel = "torque of pump shaft"
                propqkind = QUANTITYKIND.Torque
                propfeature = testrig.iri
            case "temperature_1":
                sensorlabel = "temperature sensor"
                propname = TRNS["temperature_1"]
                proplabel = "temperature of hydraulic fluid at measurement location 1"
                propqkind = QUANTITYKIND.Temperature
                propfeature = testrig.iri
            case "temperature_2":
                sensorlabel = "temperature sensor"
                propname = TRNS["temperature_2"]
                proplabel = "temperature of hydraulic fluid at measurement location 2"
                propqkind = QUANTITYKIND.Temperature
                propfeature = testrig.iri
            case "temperature_tank":
                if "components/heat exchanger" not in h5testrig:
                    raise LookupError("tank temperature pipeline could not be matched with any actor")
                sensorlabel = "temperature sensor"
                propname = TRNS["temperature_tank"]
                proplabel = "temperature of hydraulic fluid at tank"
                propqkind = QUANTITYKIND.Temperature
                propfeature = testrig.iri
            case "valve_position":
                if "actors/electric_drive_ball_valve" not in h5testrig:  # valve should use this iri instead
                    raise LookupError("valve position pipeline could not be matched with any actor")
                sensorlabel = "position sensor"
                propname = TRNS["valve_position"]
                proplabel = "position of ball valve"
                propqkind = QUANTITYKIND.PERCENT
                propfeature = testrig.iri
            case "volume_flow":
                sensorlabel = "volume flow sensor"
                propname = TRNS["volume_flow"]
                proplabel = "volume flow in the hydraulic circuit"
                propqkind = QUANTITYKIND.VolumeFlowRate
                propfeature = testrig.iri

        unit = safeval(h5pipeline.attrs["units"])
        observedproperty = Quantity(data, isPropertyOf=propfeature, hasQuantityKind=propqkind, iri=propname, label=proplabel)
        sensor = Sensor(data, hasSensorCapability="Capability", iri=sensoriri, identifier=sensortype, label=sensorlabel, isHostedBy=testrig.iri,
                        owner="FST", manufacturer=manufacturer, serialNumber=serialnumber, location=testrig.label).observes(observedproperty.iri)

        # ./data/<datasetname> : datasetname > observationCollection
        # ./data/<datasetname> : dataset > observation, result

    rdfpath = filepath_source.removesuffix(".h5") + ".setup.ttl"
    data.g.serialize(destination=rdfpath, base=TRNS)
    print(str(len(set(data.g.subjects()))) + "nodes")
    print(str(len(data.g)) + "statements")

    # one collection for the measurement run, also one collection each for every operating point of the run
    run_collection = ObservationCollection(data, label=h5run.name)
    data.g.add((run_collection.iri, DCTERMS.description, Literal(
                safeval(h5run.attrs["msmt_type"]))))
    data.g.add((run_collection.iri, DCTERMS.created, Literal(
                safeval(h5run.attrs["timestamp_created"]), datatype=XSD.dateTime)))
    creator = safeval(h5run.attrs["author"])
    accountable = safeval(h5run.attrs["pmanager"])
    data.g.add((run_collection.iri, DCTERMS.creator, Literal(creator)))
    data.g.add((run_collection.iri, SDO.accountablePerson, Literal(accountable)))

    observations = [(sensoriri, data.g.compute_qname(prop)[2]) for (sensoriri, prop)
                    in data.g.subject_objects(predicate=SOSA.observes)]

    dsetnames = []
    timestamps = []
    for _, pipename in observations:
        dsets = h5run["pipelines/measured/" + pipename + "/scaled/data"]
        dsetnames.append([x for x in dsets.keys()])
        timestamps.append([safeval(x.attrs["timestamp"]) for x in dsets.values()])

    # make sure all lists have same number of elements here

    measurements = []
    for idx in range(len(timestamps[0])):
        label = set([dsetname[idx] for dsetname in dsetnames])
        if len(label) != 1:
            raise LookupError("datasets for operating points should have the same name for each pipeline")
        label = label.pop()
        timestamp = min([datetime.fromisoformat(measurement[idx]) for measurement in timestamps])
        measurement = ObservationCollection(data, label=label).isMemberOf(run_collection.iri)
        data.g.add((measurement.iri, DCTERMS.description, Literal("operating point")))
        data.g.add((measurement.iri, DCTERMS.created, Literal(timestamp, datatype=XSD.dateTime)))
        data.g.add((measurement.iri, DCTERMS.creator, Literal(creator)))
        data.g.add((measurement.iri, SDO.accountablePerson, Literal(accountable)))

        measurements.append(measurement)

    for measurement in measurements:
        for sensor, pipename in observations:
            dset = h5run["pipelines/measured/" + pipename + "/scaled/data/" + measurement.label[0]]
            result = Result(data, unit=UNIT.UNITLESS, h5path=dset.name, creator=creator)
            Observation(data, hasResult=result.iri, madeBySensor=sensoriri).isMemberOf(measurement.iri)  # member of run?

    rdfpath = filepath_source.removesuffix(".h5") + ".ttl"
    data.g.serialize(destination=rdfpath, base=TRNS)
    print(str(len(set(data.g.subjects()))) + "nodes")
    print(str(len(data.g)) + "statements")

sourcefile.close()
