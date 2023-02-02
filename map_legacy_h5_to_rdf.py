from os import walk
from itertools import chain
from datetime import datetime
from urllib.parse import quote
from rdflib import Literal, Namespace
from rdflib.compare import to_isomorphic, graph_diff
from rdflib.namespace import RDF, XSD, DCTERMS, SOSA
from pyKRAKEN.kraken import (FST, SDO, QUANTITYKIND, UNIT, Kraken, PhysicalObject, ObservationCollection,
                             Observation, Quantity, Sensor, Result)
import h5py


def lookup_actor(item_slug):
    match item_slug:  # make this a dictionary in the meantime?
        case "ball_valve":
            actorname = "BallValve"
            actorlabel = "electric ball valve"
            propname = TRNS["BallValve/FlowCoefficient"]
            proplabel = "flow coefficient of ball valve"
            propqkind = QUANTITYKIND.VolumeFlowRate
            propfeature = None
        case "e-motor":
            actorname = "ElectricMotor"
            actorlabel = "electric motor for the pump shaft"
            propname = TRNS["rotational_speed"]
            proplabel = "rotational speed of pump shaft"
            propqkind = QUANTITYKIND["REV-PER-MIN"]
            propfeature = None
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
            propfeature = None
        case "heat exchanger" | "heat_exchanger":
            actorname = "HeatExchanger"
            actorlabel = "heat exchanger"
            propname = TRNS["temperature_tank"]  # <HydraulicFluid/>Temperature
            proplabel = "temperature of hydraulic fluid at tank"
            propqkind = QUANTITYKIND.Temperature
            propfeature = None  # <HydraulicFluid/>Temperature
        case "oil_filter":
            actorname = "OilFilter"
            actorlabel = "oil filter"
            propname = TRNS["ParticleNumberDensity"]  # <HydraulicFluid/>ParticleNumberDensity
            proplabel = "number density of contamination particles in hydraulic fluid"
            propqkind = QUANTITYKIND.ParticleNumberDensity
            propfeature = None  # <HydraulicFluid/>ParticleNumberDensity
        case _:
            raise LookupError(f"unrecognized component or actor name {item_slug}")

    return {"actorname": actorname,
            "actorlabel": actorlabel,
            "propname": propname,
            "proplabel": proplabel,
            "propqkind": propqkind,
            "propfeature": propfeature}


def lookup_sensor(item_slug, h5testrig):
    match item_slug:
        case "pressure_1":
            sensorlabel = "pressure sensor"
            propname = TRNS["pressure_1"]
            proplabel = "pressure at measurement location 1"
            propqkind = QUANTITYKIND.Pressure
            propfeature = None
        case "pressure_2":
            sensorlabel = "pressure sensor"
            propname = TRNS["pressure_2"]
            proplabel = "pressure at measurement location 2"
            propqkind = QUANTITYKIND.Pressure
            propfeature = None
        case "pressure_3":
            sensorlabel = "pressure sensor"
            propname = TRNS["pressure_3"]
            proplabel = "pressure at measurement location 3"
            propqkind = QUANTITYKIND.Pressure
            propfeature = None
        case "rotational_speed":
            sensorlabel = "rotational speed sensor"
            propname = TRNS["rotational_speed"]
            proplabel = "rotational speed of pump shaft"
            propqkind = QUANTITYKIND["REV-PER-MIN"]
            propfeature = None
        case "torque":
            sensorlabel = "torque sensor"
            propname = TRNS["torque"]
            proplabel = "torque of pump shaft"
            propqkind = QUANTITYKIND.Torque
            propfeature = None
        case "temperature_1":
            sensorlabel = "temperature sensor"
            propname = TRNS["temperature_1"]
            proplabel = "temperature of hydraulic fluid at measurement location 1"
            propqkind = QUANTITYKIND.Temperature
            propfeature = None
        case "temperature_2":
            sensorlabel = "temperature sensor"
            propname = TRNS["temperature_2"]
            proplabel = "temperature of hydraulic fluid at measurement location 2"
            propqkind = QUANTITYKIND.Temperature
            propfeature = None
        case "temperature_tank":
            if "components/heat exchanger" not in h5testrig and "components/heat_exchanger" not in h5testrig:
                raise LookupError("tank temperature pipeline could not be matched with any actor")
            sensorlabel = "temperature sensor"
            propname = TRNS["temperature_tank"]
            proplabel = "temperature of hydraulic fluid at tank"
            propqkind = QUANTITYKIND.Temperature
            propfeature = None
        case "valve_position":
            if "actors/electric_drive_ball_valve" not in h5testrig:  # valve should use this iri instead
                raise LookupError("valve position pipeline could not be matched with any actor")
            sensorlabel = "position sensor"
            propname = TRNS["valve_position"]
            proplabel = "position of ball valve"
            propqkind = QUANTITYKIND.PERCENT
            propfeature = None
        case "volume_flow":
            sensorlabel = "volume flow sensor"
            propname = TRNS["volume_flow"]
            proplabel = "volume flow in the hydraulic circuit"
            propqkind = QUANTITYKIND.VolumeFlowRate
            propfeature = None
        case _:
            raise LookupError(f"unrecognized pipeline or sensor name {item_slug}")

    return {"sensorlabel": sensorlabel,
            "propname": propname,
            "proplabel": proplabel,
            "propqkind": propqkind,
            "propfeature": propfeature}


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


def map_testrig(kraken, h5run):
    testrig_slug = safeval(h5run.attrs["testrig_name"])
    match testrig_slug:
        case "hydraulic_small":
            testrig_slug = "HydraulicSmall"
            comment = "small test rig for displacement pumps"
        case "hydraulic_large":
            testrig_slug = "HydraulicLarge"
            comment = "large test rig for displacement pumps"
        case _:
            raise LookupError(f"unrecognized testrig name {testrig_slug}")

    testrig_iri = FST["testrig/" + testrig_slug]

    return PhysicalObject(kraken, iri=testrig_iri, comment=comment,
                          name=testrig_slug, owner="FST", manufacturer="FST")


def map_uut(kraken, testrig, h5run):
    # h5pump = h5run["unit_under_test"]
    # ./geometry > property @FoI Pump

    pumpname = safeval(h5run.attrs["pump_type"])  # pumps should be items in lookup service, match by this
    manufacturer = safeval(h5run.attrs["pump_manufacturer"])
    return PhysicalObject(kraken, iri=FST["equipment/" + quote(pumpname, safe='')], identifier=pumpname, name=pumpname,
                          isHostedBy=testrig.iri, owner="FST", manufacturer=manufacturer)


def map_actor(kraken, equip, testrig, h5actor):
    actorname = h5actor.name.rsplit("/")[-1]
    manufacturer = safeval(h5actor.attrs["manufacturer"])
    identifier = safeval(h5actor.attrs["type"])  # should be actual identifier

    actor_props = lookup_actor(actorname)  # make this lookup for uuid
    if actor_props["propfeature"] is None:
        actor_props["propfeature"] = testrig.iri

    actoriri = FST["actor/" + quote(identifier, safe='')]

    tmp = Kraken()
    # only use identifying info here, not mapped info!
    actor = PhysicalObject(tmp, iri=actoriri,
                           identifier=identifier,
                           name=actor_props["actorlabel"],
                           comment=actor_props["actorlabel"],
                           owner="FST",
                           manufacturer=manufacturer,
                           serialNumber=identifier)

    # maybe validate vs shacl profile = essential info for ident?
    ident = equip.g.value(predicate=SDO.serialNumber, object=Literal(identifier), any=False)
    # maybe we need to catch the error from any=False, if we want to handle it, or it is too cryptic

    diffs = 0
    if ident is not None:
        # we already know that -one- item that fits identification criteria is there
        # we only need to check for properties from h5 that is there, but different
        # i.e. diff of tmp ("from h5") versus equip ("in database")
        _, in_first, _ = graph_diff(to_isomorphic(tmp.g), to_isomorphic(equip.g))
        for s, p, o in in_first:
            diffs += 1
            print(f"inconsistent configuration of equipment with serialnumber \"{identifier}\" found")
            print(f"{s} {p} {o}")

    if (ident is None) or (diffs != 0):
        print(f"equipment with {str(SDO.serialNumber)} = \"{identifier}\" not found, adding it")
        equip.g += tmp.g
        ident = actor.iri
        # flag for review via bibo.status "REVIEW"

    for p, o in equip.g.predicate_objects(subject=ident):
        kraken.g.add((ident, p, o))

    actor.g = kraken.g
    actor.isHostedBy = testrig.iri
    actuatedproperty = Quantity(kraken,
                                hasQuantityKind=actor_props["propqkind"],
                                isPropertyOf=actor_props["propfeature"],
                                iri=actor_props["propname"],
                                name=actor_props["proplabel"])
    kraken.g.add((actor.iri, RDF.type, SOSA.Actuator))
    kraken.g.add((actor.iri, SOSA.actsOnProperty, actuatedproperty.iri))


def map_sensor(kraken, testrig, h5pipeline, h5testrig):
    pipename = h5pipeline.name.rsplit("/")[-2]  # second to last part, last will be "scaled"
    if not confirmattr(h5pipeline, expectedkey="kkn_CLASS", expectedval="PIPELINE"):
        raise LookupError("this should be a pipeline")

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
    sensoriri = FST["sensor/" + quote(serialnumber, safe='')]

    sensor_props = lookup_sensor(pipename, h5testrig)
    if sensor_props["propfeature"] is None:
        sensor_props["propfeature"] = testrig.iri

    # unit = safeval(h5pipeline.attrs["units"])
    observedproperty = Quantity(kraken,
                                isPropertyOf=sensor_props["propfeature"],
                                hasQuantityKind=sensor_props["propqkind"],
                                iri=sensor_props["propname"],
                                name=sensor_props["proplabel"])
    sensor = Sensor(kraken,
                    hasSensorCapability="Capability",
                    iri=sensoriri,
                    identifier=sensortype,
                    name=sensor_props["sensorlabel"],
                    isHostedBy=testrig.iri,
                    owner="FST",
                    manufacturer=manufacturer,
                    serialNumber=serialnumber,
                    location=testrig.name[0]).observes(observedproperty.iri)


filepath_source = "data/KF_80_2900.h5"
# filepath = filepath_source.removesuffix(".h5") + "_rdf_embedded.h5"

data = Kraken()
equip = Kraken()
equip.g.parse("data/equipment.ttl")
num_runs = 0

# dirpath = "D:/Daten/Download/fst/data/schaenzle/data_final_appended_meta/"
dirpath = "data/"
for root, _, filenames in walk(dirpath):
    for filename in filenames:
        if filename.endswith(".h5"):
            filepath = "/".join([root, filename])
            with h5py.File(filepath, "r") as sourcefile:
                for h5run in sourcefile.values():
                    try:
                        testrig = map_testrig(data, h5run)
                        if testrig.name[0] != "HydraulicSmall":
                            continue

                        num_runs += 1
                        TRNS = Namespace(testrig.iri + "/")

                        h5testrig = h5run["test_rig"]

                        for h5actor in chain(h5testrig["actors"].values(), h5testrig["components"].values()):
                            map_actor(data, equip, testrig, h5actor)

                        # ./operation/nom_rot_speed > actuatedProperty @FoI = Pump, actor = e motor, FU
                        # ./operation/nom_temp > actuatedProperty @FoI = oil, actor = heat ex
                        # the above can be results of actuations?
                        # ./operation/hydraulic_oil > property
                        uut = map_uut(data, testrig, h5run)

                        for obj in h5run["pipelines/measured"].values():
                            h5pipeline = obj["scaled"]
                            map_sensor(data, testrig, h5pipeline, h5testrig)

                        # ./data/<datasetname> : datasetname > observationCollection
                        # ./data/<datasetname> : dataset > observation, result
                    except LookupError as err:
                        raise LookupError(f"something went wrong in file {filepath}: {err}")

rdfpath = filepath_source.removesuffix(".h5") + ".setup.ttl"
data.g.serialize(destination=rdfpath, base=FST)
print(f"{len(set(data.g.subjects()))} nodes")
print(f"{len(data.g)} statements")
print(f"{num_runs} runs")
equip.g.serialize(destination="data/equipment.ttl", base=FST)

if False:
    # one collection for the measurement run, also one collection each for every operating point of the run
    run_collection = ObservationCollection(data, name=h5run.name)
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
        name = set([dsetname[idx] for dsetname in dsetnames])
        if len(name) != 1:
            raise LookupError("datasets for operating points should have the same name for each pipeline")
        name = name.pop()
        timestamp = min([datetime.fromisoformat(measurement[idx]) for measurement in timestamps])
        measurement = ObservationCollection(data, name=name).isMemberOf(run_collection.iri)
        data.g.add((measurement.iri, DCTERMS.description, Literal("operating point")))
        data.g.add((measurement.iri, DCTERMS.created, Literal(timestamp, datatype=XSD.dateTime)))
        data.g.add((measurement.iri, DCTERMS.creator, Literal(creator)))
        data.g.add((measurement.iri, SDO.accountablePerson, Literal(accountable)))

        measurements.append(measurement)

    for measurement in measurements:
        for sensor, pipename in observations:
            dset = h5run["pipelines/measured/" + pipename + "/scaled/data/" + measurement.name[0]]
            result = Result(data, unit=UNIT.UNITLESS, h5path=dset.name, creator=creator)
            Observation(data, hasResult=result.iri, madeBySensor=sensor.iri).isMemberOf(measurement.iri)
            # member of run?

    rdfpath = filepath_source.removesuffix(".h5") + ".ttl"
    data.g.serialize(destination=rdfpath, base=TRNS)
    print(str(len(set(data.g.subjects()))) + "nodes")
    print(str(len(data.g)) + "statements")
