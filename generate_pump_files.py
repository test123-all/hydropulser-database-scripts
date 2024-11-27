from importlib import import_module
from pathlib import Path
import warnings

from hardcoded_generate_scripts.gitlab_db_component_pump import generate_pump_files
from hardcoded_generate_scripts.gitlab_db_mdgen import generate_sensor_md_s_from_directory

from fstlabelcreator import script_functions

import pandas as pd
import numpy as np

def main():
    file_directory = Path(__file__).parent.resolve()
    path_for_generated_files = Path(f"{file_directory}/_generated")
    path_for_generated_labels = Path(f"{path_for_generated_files}/pID_label_files")
    path_for_generated_PID_files = Path(f"{path_for_generated_files}/pID_directories")

    try:
        path_for_generated_files.mkdir()
    except FileExistsError:
        pass

    try:
        path_for_generated_labels.mkdir()
    except FileExistsError:
        pass

    try:
        path_for_generated_PID_files.mkdir()
    except FileExistsError:
        pass


    # These are the variables you need to adjust ------------------------------------------
    pump_excel_table = 'pumps_table.xlsx'
    # The name of the WiMi you want to create the files for. This is the same information
    # you have inserted into the sensor table.
    responsible_WiMi = 'Logan'
    # -------------------------------------------------------------------------------------

    path_to_pump_excel_table = Path(f"{file_directory}/{pump_excel_table}")
    # script_functions.generate_pump_files(path_for_generated_files= path_for_generated_labels,
    #                                      path_to_sensor_excel_sheet= path_to_pump_excel_table,
    #                                      responsible_WiMi= responsible_WiMi)

    print('Start of the generation of the sensor files.')
    generate_pump_files_for_the_table(pump_table_path=path_to_pump_excel_table, generated_files_directory_path=path_for_generated_PID_files)
    print('Generation of the sensor files successfully finished!')

    print('Start of the generation of the README.md files of the sensor directories.')
    generate_sensor_md_s_from_directory(sensors_directory_search_path= path_for_generated_PID_files.resolve())

    ## Generate the labels for the pumps.
    # First create the table that is used to create the labels.
    FST_namespace_URL = 'https://w3id.org/fst/resource/'
    ID_list = []
    heading_list = []
    df_pumps = pd.read_excel(path_to_pump_excel_table, sheet_name='Pumps', skiprows=[1])
    for idx in df_pumps.index:
        df_pumps_row = df_pumps.iloc[idx]
        df_pumps_row = df_pumps_row.replace({np.nan: None})

        ID_entry = f"{FST_namespace_URL}{df_pumps_row['uuid']}"
        heading_entry = (f"{df_pumps_row['Hersteller']} {df_pumps_row['Bezeichnung']}<br/>"
                        f"P_N: {df_pumps_row['Motornennleistung']} {df_pumps_row['Motornennleistung Einheit']}<br/>"
                        f"ω: {np.round(df_pumps_row['Actuator Input Range from'], 0)} - {np.round(df_pumps_row['Actuator Input Range to'], 0)} {df_pumps_row['Actuator Input Range unit']}")  # FIXME: TODO: hardcoded!

        ID_list.append(ID_entry)
        heading_list.append(heading_entry)

    data = {
        "ID": ID_list,
        "heading": heading_list
    }
    label_df = pd.DataFrame(data)
    # Write to an Excel file with a specific sheet name
    label_df.to_excel(f"{path_for_generated_files}/label_table.xlsx", sheet_name="Sheet1", index=False)

    # Set the paths
    path_for_generated_files_text_label_from_excel_sheet: Path = Path(
        f'{path_for_generated_files}/text_label_from_excel_sheet')
    path_to_text_excel_sheet: Path = Path(f'{path_for_generated_files}/label_table.xlsx')

    try:
        path_for_generated_files_text_label_from_excel_sheet.mkdir()
    except FileExistsError:
        pass

    script_functions.generate_label_sites_from_excel_sheets(
        path_for_generated_files=path_for_generated_files_text_label_from_excel_sheet,
        path_to_text_excel_sheet=path_to_text_excel_sheet,
        supported_template=script_functions.SUPPORTED_TEMPLATES['B7651'],
        label_start_position_number= 12)

    # ID	heading
    # https://w3id.org/fst/resource/018bfcec-5037-7cf8-81a1-1c3282ca03ae	PNr:  SBO330E-0,75E1/112U330AB<br/>SNr:  2418657<br/>
    # https://w3id.org/fst/resource/018bfcec-503c-77ce-832b-b7ab7d26d8da	PNr:  SBO330E-0,75E1/112U330AB<br/>SNr:  2418665<br/>
    # https://w3id.org/fst/resource/018bfcec-503d-7191-b393-3938e35d177a	PNr:  SBO330E-0,75E1/112U330AB030<br/>SNr:  2493736<br/>
    # https://w3id.org/fst/resource/018bfcec-503e-7bcb-a136-7edf30722bf6	PNr:  SBO330E-0,75E1/112U330AB030<br/>SNr:  2493732<br/>
    # https://w3id.org/fst/resource/018bfcec-503f-7890-8407-1c0589c7fc33	PNr:  SBO330E-0,75E1/112U330AB030<br/>SNr:  2493737<br/>
    # https://w3id.org/fst/resource/018bfcec-5040-793a-b28c-a4520e474d15	PNr:  SBO330E-0,75E1/112U330AB030<br/>SNr:  2493741<br/>
    # https://w3id.org/fst/resource/018bfcec-5042-7d5f-bfc1-dc31d16f0d6a	PNr:  SBO210-0,5E1/112U-250AK105<br/>SNr:  11793906<br/>
    # https://w3id.org/fst/resource/018bfcec-5043-7fc1-a371-a22da4baea9a	PNr:  SBO210-0,5E1/112U-250AK105<br/>SNr:  11793904<br/>
    # https://w3id.org/fst/resource/018bfcec-5044-7bdd-b4d5-c6b3f44eb7b3	PNr:  SBO210-0,5E1/112U-250AK105<br/>SNr:  11793911<br/>
    # https://w3id.org/fst/resource/018bfcec-5045-7f02-8149-205fd09d58eb	PNr:  SBO210-0,5E1/112U-250AK105<br/>SNr:  11793908<br/>
    # https://w3id.org/fst/resource/018bfcec-5046-7611-bf92-7c8e900d34bb	PNr:  SBO210-0,5E1/112U-250AK105<br/>SNr:  11793910<br/>
    # https://w3id.org/fst/resource/018bfcec-5048-78fe-a641-c44aa533b894	PNr:  SBO400-1,3A6/112U-400AK<br/>SNr:  3818191<br/>

    # With the table create the labels with the fst label creator.



def generate_pump_files_for_the_table(pump_table_path: [Path, str], generated_files_directory_path: [Path, str]):
    SUPPORTED_TABLE_SHEET_NAMES = ["Pumps"]

    # Get the path of the direcotry of this file
    directory_path = Path(__file__).parent.resolve()

    dfs = pd.read_excel(pump_table_path, sheet_name=None, skiprows=[1])
    # sensor_dir = "C:/Users/NP/Documents/AIMS/metadata_hub/data/fst_measurement_equipment/"
    try:
        generated_files_directory_path.mkdir()
    except FileExistsError:
        pass

    for sheet_name in SUPPORTED_TABLE_SHEET_NAMES:
        df = dfs[sheet_name]
        for idx in df.index:
            row = df.iloc[idx]
            row = row.replace({np.nan: None})

            # TODO: Add some control code that checks if the necessary minimal set of information is present
            try:
                generate_pump_files(pump_files_dir=f"{generated_files_directory_path}/", df_row=row)
            except ValueError as e:
                warnings.warn(
                    f'There is a value error in one of the inputs in the {row["Ident-Nummer"]} line.\nSkipping Line..',
                    category=Warning, stacklevel=1)
                pass

if __name__ == '__main__':
    main()
