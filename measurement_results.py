import h5py
from rdflib import Graph
from rdflib.namespace import RDF, DCTERMS, SOSA
from modules.kraken import (
    H5PATH_RDF_METADATA,
    UNIT,
    Kraken,
    ObservationCollection,
    Observation,
    Result,
)

# declare used filepaths
filepath_source = "./2022-11-15-testlauf.h5"
filepath = "./usecase_data_rdf_embedded.h5"

# get measurement data from file for now, students get this from their data acquisition routine
with h5py.File(filepath_source) as f:
    results = {}

    for idx in range(3):
        h5dset = f["/raw/Sensor" + str(idx + 1)]
        results[h5dset.attrs["Sensorname"]] = {"numericValues": h5dset[1, :],
                                               "phenomenonTimes": h5dset[0, :]}

    # since phenomenontimes for observations of other Sensors is not logged
    # we assume them to be equal to earliest and latest time of sensors 1-3
    t_min = min([min(results[key]["phenomenonTimes"]) for key in results.keys()])
    t_max = max([max(results[key]["phenomenonTimes"]) for key in results.keys()])

    h5attrs = f["/raw"].attrs
    results[h5attrs["Sensorname Probentemperatur"]] = {"numericValues": h5attrs["Probentemperatur"],
                                                       "phenomenonTimes": t_min}
    results[h5attrs["Sensorname Umgebungstemperatur"]] = {"numericValues": [h5attrs["Umgebungstemperatur_Start"],
                                                                            h5attrs["Umgebungstemperatur_Ende"]],
                                                          "phenomenonTimes": [t_min, t_max]}

# build metadata graph for observations and results
data = Kraken()

# import prepared graph of measurement setup
data.g += Graph().parse("./usecase_setup_rdf.ttl")

# make collection for new measurement
oc = ObservationCollection(data, None, "Measurement")

with h5py.File(filepath, "w") as f:
    # find sensors in metadata graph and iterate
    for sensor_iri in data.g.subjects(RDF.type, SOSA.Sensor):
        sensor_ID = str(data.g.value(subject=sensor_iri, predicate=DCTERMS.identifier))

        h5path = "/" + oc.name + "/" + sensor_ID + "/"
        values = Result(data, None, None, "Nils Preuß", UNIT.DEG_C, h5path, results[sensor_ID]["numericValues"])
        times = Result(data, None, None, "Nils Preuß", UNIT.SEC, h5path, results[sensor_ID]["phenomenonTimes"])
        Observation(data, None, None, sensor_iri, [values.iri, times.iri]).isMemberOf(oc.iri)

        f.create_dataset(values.h5path, data=values.data)
        f.create_dataset(times.h5path, data=times.data)

    # write metadata graph and datasets to h5 file
    f.create_dataset(H5PATH_RDF_METADATA, data=data.g.serialize())

# export metadata graph to ttl for pretty syntax highlighting / visualization
data.g.serialize(destination="./usecase_rdf.ttl", format="longturtle")
