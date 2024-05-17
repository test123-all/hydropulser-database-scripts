from pathlib import Path

import rdflib
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import DCAT, DCMITYPE, DCTERMS, RDF, RDFS, XSD, SSN, SDO, FOAF, SOSA
from scipy.io import loadmat

QUANTITYKIND = Namespace("https://qudt.org/vocab/quantitykind/")
UNIT = Namespace("https://qudt.org/vocab/unit/")
QUDT = Namespace("https://qudt.org/schema/qudt/")

SSN_SYSTEM = Namespace('https://www.w3.org/ns/ssn/systems/')

PROV = Namespace('http://www.w3.org/ns/prov#')
METADAT4ING = Namespace('http://w3id.org/nfdi4ing/metadata4ing#')

def parse_measurement_mat_file_to_RDF(mat_file_path: Path | str):
    mat_dict = loadmat(file_name=str(mat_file_path))
    measurement_data_struct = mat_dict['measurement_data_struct'][0, 0]

    fields = ['METADATA', 'model_PARAMETERS']

    METADATA_struct = measurement_data_struct[fields[0]][0, 0]
    model_PARAMETERS_struct = measurement_data_struct[fields[1]][0, 0]

    g = Graph()
    #FST_RESOURCE = Namespace('https://w3id.org/fst/resource/')
    FST_MEASUREMENT = Namespace('https://w3id.org/fst/measurement/')
    g.bind("qudt", QUDT)
    g.bind("quantitykind", QUANTITYKIND)
    g.bind("unit", UNIT)
    #g.bind("fst_resource", FST_RESOURCE)
    g.bind("fst_measurement", FST_MEASUREMENT)
    g.bind("metdat4ing", METADAT4ING)

    # Add the measurement with its id
    measurement_UUID = METADATA_struct['measurement_UUID'][0]
    # TODO: FIXME: WARN: die id muss in einem eigenen namespace definiert werden

    measurement_node = URIRef(f'{FST_MEASUREMENT}{measurement_UUID}')
    # TODO: FIXME: Das passt hier noch nicht. Eigentlich müsste das keinen Typ haben, wäre es ein Dokument funktioniert die
    #  andere Logik drum rum mit den Termen nicht mehr
    #g.add((measurement_node, RDF.type, FOAF.Document))
    # g.add((measurement_node, RDF.type, SDO.Event))
    g.add((measurement_node, SDO.comment, Literal('This is a measurement', lang='en')))
    # TODO: Start Zeit usw. fehlt noch
    g.add((measurement_node, SDO.startDate, Literal(METADATA_struct['measurement_start_date'][0])))
    g.add((measurement_node, SDO.endDate, Literal(METADATA_struct['measurement_end_date'][0])))
    # TODO: Convert in different format
    g.add((measurement_node, SDO.duration, Literal(f"{METADATA_struct['measuring_period'][0, 0]['value'][0, 0]} {METADATA_struct['measuring_period'][0, 0]['unit'][0]}")))


    # Add the experimenter
    experimenter_struct = METADATA_struct['measurement_executor'][0, 0]
    experimenter_node = URIRef(experimenter_struct['ORCID'][0])
    g.add((measurement_node, DCTERMS.creator, experimenter_node))
    g.add((experimenter_node, RDF.type, FOAF.Person))
    g.add((experimenter_node, RDF.type, PROV.Person))
    g.add((experimenter_node, FOAF.givenName, Literal(experimenter_struct['given_name'][0])))
    g.add((experimenter_node, FOAF.surname, Literal(experimenter_struct['sur_name'][0])))
    g.add((experimenter_node, PROV.hadRole, METADAT4ING.DataCollector))
    # TODO: FIXME: Hardcoded organization
    # TODO: FIXME: fst has no RDF yet therefore more infos are added
    g.add((experimenter_node, SDO.memberOf, URIRef('https://w3id.org/fst')))
    g.add((URIRef('https://w3id.org/fst'), SDO.memberOf, URIRef('https://ror.org/05n911h24')))
    g.add((URIRef('https://w3id.org/fst'), RDF.type, SDO.Organization))
    g.add((URIRef('https://ror.org/05n911h24'), SDO.name, Literal('Technical University of Darmstadt', lang='en')))
    g.add((URIRef('https://ror.org/05n911h24'), SDO.name,
           Literal('Technische Universität Darmstadt', lang='de')))
    g.add((URIRef('https://ror.org/05n911h24'), RDF.type, SDO.Organization))

    g.add((URIRef('https://w3id.org/fst'), SDO.name, Literal('Chair of Fluid Systems', lang='en')))
    g.add((URIRef('https://w3id.org/fst'), SDO.name, Literal('Institut für Fluidsystemtechnik', lang='de')))

    # If the experimenter should'nt have a supervisor the experimenter always will be project manager and researcher
    try:
        supervisor_struct = METADATA_struct['supervisor'][0, 0]
    except ValueError:
        target_node = experimenter_node
    else:
        supervisor_node = URIRef(supervisor_struct['ORCID'][0])
        g.add((measurement_node, DCTERMS.contributor, supervisor_node))
        g.add((supervisor_node, RDF.type, FOAF.Person))
        g.add((supervisor_node, RDF.type, PROV.Person))
        g.add((supervisor_node, FOAF.givenName, Literal(supervisor_struct['given_name'][0])))
        g.add((supervisor_node, FOAF.surName, Literal(supervisor_struct['sur_name'][0])))
        # TODO: FIXME: Hardcoded organization
        # TODO: FIXME: fst has no RDF yet
        g.add((supervisor_node, SDO.memberOf, URIRef('https://w3id.org/fst')))

        target_node = supervisor_node

    g.add((target_node, PROV.hadRole, METADAT4ING.ProjectManager))
    g.add((target_node, PROV.hadRole, METADAT4ING.Researcher))


    # Add the required hardware
    hardware_metadata_struct = METADATA_struct['hardware'][0, 0]
    hardware_metadata_struct_fieldnames = hardware_metadata_struct.dtype.names
    # TODO: software should probably be described in the future
    AWAITED_HARDWARE_FIELDNAMES = ['p_ID', 'name', 'type', 'manufacturer', 'software', 'serial_number']
    def recursively_add_sub_components(current_hardware_struct, graph: Graph, measurement_node) -> Graph:
        current_hardware_node = URIRef(current_hardware_struct['p_ID'][0])
        current_hardware_fieldnames = current_hardware_struct.dtype.names

        for sub_fieldname in current_hardware_fieldnames:
            if sub_fieldname in AWAITED_HARDWARE_FIELDNAMES:
                continue

            # Add the sub component node
            current_sub_component_struct = current_hardware_struct[sub_fieldname][0, 0]
            current_sub_component_node = URIRef(current_sub_component_struct['p_ID'][0])

            graph.add((current_sub_component_node, RDF.type, DCMITYPE.PhysicalObject))
            graph.add((current_sub_component_node, SDO.name, Literal(current_sub_component_struct['name'][0])))
            # TODO: Das automatische resolven könnt eman auch über das nachladen der Datensätze und nachschauen erledigen
            if current_sub_component_struct['type'][0] == 'Substance':
                # TODO: FIXME: WARN: Das mit dem ispart is von ssn evtl. nicht vorgesehen
                graph.add((current_sub_component_node, RDF.type, SDO.Substance))
                graph.add((current_hardware_node, DCTERMS.hasPart, current_sub_component_node))
                graph.add((current_sub_component_node, DCTERMS.isPartOf, current_hardware_node))
            else:
                graph.add((current_hardware_node, RDF.type, SSN.System))
                graph.add((current_hardware_node, SSN.hasSubSystem, current_sub_component_node))

                # Add the feature of interest
                if current_sub_component_struct['type'][0] == 'TestObject':
                    graph.add((current_hardware_node, SOSA.isFeatureOfInterestOf, measurement_node))
                    graph.add((measurement_node, SOSA.hasFeatureOfInterest, current_hardware_node))


                # Recursively add the sub-component to the graph
                recursively_add_sub_components(current_sub_component_struct, graph)

        return graph

    for hardware_fieldname in hardware_metadata_struct_fieldnames:
        # Add the different hardware components
        current_hardware_struct = hardware_metadata_struct[hardware_fieldname][0, 0]
        current_hardware_node = URIRef(current_hardware_struct['p_ID'][0])
        g.add((measurement_node, DCTERMS.requires, current_hardware_node))
        g.add((current_hardware_node, DCTERMS.isRequiredBy, measurement_node))
        g.add((current_hardware_node, RDF.type, DCMITYPE.PhysicalObject))
        g.add((current_hardware_node, RDF.type, SSN.System))
        g.add((current_hardware_node, SDO.name, Literal(current_hardware_struct['name'][0])))
        g.add((current_hardware_node, SDO.comment, Literal(f"This component is of type \'{current_hardware_struct['type'][0]}\'",lang='en')))

        # If the object is a Testobject it is the feature of interest of the measurement
        if current_hardware_struct['type'][0] == 'TestObject':
            g.add((current_hardware_node, SOSA.isFeatureOfInterestOf, measurement_node))
            g.add((measurement_node, SOSA.hasFeatureOfInterest, current_hardware_node))

        # Recurse through the sub-components
        g = recursively_add_sub_components(current_hardware_struct=current_hardware_struct,
                                           graph=g,
                                           measurement_node=measurement_node)
    # Add the simulink model
    software_struct = METADATA_struct['software'][0, 0]
    simulink_model_struct = software_struct['simulink_model'][0, 0]
    simulink_model_node = URIRef(f"https://w3id.org/fst/resource/{simulink_model_struct['name'][0]}")
    g.add((simulink_model_node, DCTERMS.isRequiredBy, measurement_node))
    g.add((measurement_node, DCTERMS.requires, simulink_model_node))
    g.add((simulink_model_node, SDO.name, Literal(simulink_model_struct['name'][0])))
    g.add((simulink_model_node, SDO.codeRepository, URIRef(simulink_model_struct['repository_url'][0].replace('\n', ''))))
    g.add((simulink_model_node, DCTERMS.hasVersion, Literal(simulink_model_struct['commit_hash'][0].replace('\n', ''))))
    g.add((simulink_model_node, SDO.location, Literal(simulink_model_struct['relative_repository_file_path'][0])))
    g.add((simulink_model_node, SDO.comment, Literal('This is the simulink model use don the simulation '
                                                     'plattform. It is located inside the repository defined by '
                                                     '\'SDO.codeRepository\' at the path specified by \'SDO.location\' with '
                                                     'the version commit-hash specified by \'DCTERMS.hasVersion\'.', lang='en')))


    # Add the timeseries
    quantitykind_dict = {"Pressure": QUANTITYKIND.Pressure,
                         "Force": QUANTITYKIND.Force,
                         "Temperature": QUANTITYKIND.Temperature,
                         "Deflection": QUANTITYKIND.Displacement,
                         "Time": QUANTITYKIND.Time}

    unit_dict = {"bar": UNIT.BAR,
                 "mbar": UNIT.MilliBAR,
                 "psi": UNIT.PSI,
                 "kPa": UNIT.KiloPA,
                 "MPa": UNIT.MegaPA,
                 "°C": UNIT.DEG_C,
                 "K": UNIT.K,
                 "N": UNIT.N,
                 "kN": UNIT.KiloN,
                 "mm": UNIT.MilliM,
                 "cm": UNIT.CentiM,
                 "V": UNIT.V,
                 "mV": UNIT.MilliV,
                 "µV": UNIT.MicroV,
                 "s": UNIT.SEC}
    # Get the field names of the timeseries
    measurement_data_struct_fieldnames = measurement_data_struct.dtype.names
    for current_fieldname in measurement_data_struct_fieldnames:
        if current_fieldname in fields:
            continue

        # Else timeseries is found
        current_timeseries_struct = measurement_data_struct[current_fieldname][0, 0]
        current_timeseries_struct_name = current_fieldname
        current_timeseries_struct_node = URIRef(f'{str(measurement_node)}/{current_fieldname}')

        g.add((measurement_node, SDO.hasPart, current_timeseries_struct_node))
        g.add((current_timeseries_struct_node, RDF.type, SOSA.Observation))
        g.add((current_timeseries_struct_node, QUDT.hasQuantityKind, quantitykind_dict[current_timeseries_struct['physical_quantity_name'][0]]))
        g.add((current_timeseries_struct_node, QUDT.unit, unit_dict[current_timeseries_struct['unit'][0]]))

        g.add((current_timeseries_struct_node, SDO.name, Literal(current_timeseries_struct_name)))

        SIGNAL_TYPE_PARAMETER_OPTIONS = ['measured', 'simulated/calculated']
        if current_timeseries_struct_name == 'measurement_TIME_VECTOR':
            g.add((current_timeseries_struct_node, SDO.comment, Literal('This vector is the x-axis of all of the contained measured and simulated/calculated timeseries signals.', lang='en')))
            continue
        elif current_timeseries_struct['signal_type_parameter'][0] == SIGNAL_TYPE_PARAMETER_OPTIONS[0]:
            current_sensor_struct = current_timeseries_struct['sensor_data'][0, 0]
            current_sensor_node = URIRef(current_sensor_struct['p_ID'][0, 0]['URI'][0])
            g.add((current_timeseries_struct_node, SOSA.isObservedBy, current_sensor_node))
            g.add((current_timeseries_struct_node, SDO.comment, Literal('This is a measured timeseries.', lang='en')))
        elif current_timeseries_struct['signal_type_parameter'][0] == SIGNAL_TYPE_PARAMETER_OPTIONS[1]:
            g.add((current_timeseries_struct_node, SDO.comment, Literal('This is a simulated/calculated timeseries.', lang='en')))
        else:
            # TODO: Find better fitting error class and a more suiting error message
            raise Exception(f"Supported: {SIGNAL_TYPE_PARAMETER_OPTIONS} \n"
                            f"Got: \'{current_timeseries_struct['signal_type_parameter'][0]}\'")


    current_python_file_dir_path = Path(__file__).parent.resolve()
    dir_path = Path(f"{current_python_file_dir_path}/test")

    try:
        dir_path.mkdir()
    except FileExistsError:
        pass

    file_path = f"{dir_path}/rdf"
    print(g.serialize(destination=f"{file_path}.json", format="json-ld", auto_compact=True))
    print(g.serialize(destination=f"{file_path}.ttl", base=FST_MEASUREMENT, format="longturtle", encoding="utf-8"))
    print(g.serialize(destination=f"{file_path}.xml", base=FST_MEASUREMENT, format="xml"))

    def recursively_add_sub_components(current_hardware_struct, graph: Graph, measurement_node) -> Graph:
        current_hardware_node = URIRef(current_hardware_struct['p_ID'][0])
        current_hardware_fieldnames = current_hardware_struct.dtype.names

        for sub_fieldname in current_hardware_fieldnames:
            if sub_fieldname in AWAITED_HARDWARE_FIELDNAMES:
                continue

            # Add the sub component node
            current_sub_component_struct = current_hardware_struct[sub_fieldname][0, 0]
            current_sub_component_node = URIRef(current_sub_component_struct['p_ID'][0])

            graph.add((current_sub_component_node, RDF.type, DCMITYPE.PhysicalObject))
            # TODO: Das automatische resolven könnt eman auch über das nachladen der Datensätze und nachschauen erledigen
            if current_sub_component_struct['type'][0] == 'Substance':
                # TODO: FIXME: WARN: Das mit dem ispart is von ssn evtl. nicht vorgesehen
                graph.add((current_hardware_node, DCTERMS.hasPart, current_sub_component_node))
                graph.add((current_sub_component_node, DCTERMS.isPartOf, current_hardware_node))
            else:
                graph.add((current_hardware_node, RDF.type, SSN.System))
                graph.add((current_hardware_node, SSN.hasSubSystem, current_sub_component_node))

                # Add the feature of interest
                if current_sub_component_struct['type'][0] == 'TestObject':
                    graph.add((current_hardware_node, SOSA.isFeatureOfInterestOf, measurement_node))
                    graph.add((measurement_node, SOSA.hasFeatureOfInterest, current_hardware_node))


                # Recursively add the sub-component to the graph
                recursively_add_sub_components(current_sub_component_struct, graph)

        return graph








