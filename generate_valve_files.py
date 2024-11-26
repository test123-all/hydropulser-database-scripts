from importlib import import_module
from pathlib import Path
import warnings

from hardcoded_generate_scripts.gitlab_db_valve_sensor_combination import generate_valve_files
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
    valves_excel_table = 'valves_table.xlsx'
    # The name of the WiMi you want to create the files for. This is the same information
    # you have inserted into the sensor table.
    responsible_WiMi = 'Logan'
    # -------------------------------------------------------------------------------------

    path_to_valves_excel_table = Path(f"{file_directory}/{valves_excel_table}")
    # script_functions.generate_pump_files(path_for_generated_files= path_for_generated_labels,
    #                                      path_to_sensor_excel_sheet= path_to_pump_excel_table,
    #                                      responsible_WiMi= responsible_WiMi)

    print('Start of the generation of the sensor files.')
    generate_valve_files_from_the_table(valve_table_path=path_to_valves_excel_table, generated_files_directory_path=path_for_generated_PID_files)
    print('Generation of the sensor files successfully finished!')

    print('Start of the generation of the README.md files of the sensor directories.')
    generate_sensor_md_s_from_directory(sensors_directory_search_path= path_for_generated_PID_files.resolve())

    ## Generate the labels for the valves.
    # First create the table that is used to create the labels.
    FST_namespace_URL = 'https://w3id.org/fst/resource/'
    ID_list = []
    heading_list = []
    df_valves = pd.read_excel(path_to_valves_excel_table, sheet_name='Valves', skiprows=[1])
    for idx in df_valves.index:
        df_valves_row = df_valves.iloc[idx]
        df_valves_row = df_valves_row.replace({np.nan: None})

        ID_entry = f"{FST_namespace_URL}{df_valves_row['uuid']}"

        if (isinstance(df_valves_row['K_vs Wert'], str)
                and df_valves_row['K_vs Wert'].lower() == 'unknown'):
            k_vs_string = 'UNKNOWN'
        else:
            k_vs_string = f"{np.round(df_valves_row['K_vs Wert'] * 3600, 1)} m^3/h"

        if len(df_valves_row['Bezeichnung']) >= 8:
            bezeichnung_string = f"{df_valves_row['Bezeichnung'][:8]} ... "
        else:
            bezeichnung_string = df_valves_row['Bezeichnung']

        heading_entry = (f"{df_valves_row['Hersteller']} {bezeichnung_string}<br/>"
                         f"K_vs: {k_vs_string}<br/>" # FIXME: TODO: hardcoded!
                         f"p_max: {np.round(df_valves_row['maximaler Druck Wert'] / 100000, 1)} bar")  # FIXME: TODO: hardcoded!

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
        label_start_position_number=15)


def generate_valve_files_from_the_table(valve_table_path: [Path, str], generated_files_directory_path: [Path, str]):
    SUPPORTED_TABLE_SHEET_NAMES = ["Valves"]

    # Get the path of the direcotry of this file
    directory_path = Path(__file__).parent.resolve()

    dfs = pd.read_excel(valve_table_path, sheet_name=None, skiprows=[1])

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
                generate_valve_files(valve_files_dir=f"{generated_files_directory_path}/", df_row=row)
            except ValueError as e:
                warnings.warn(
                    f'There is a value error in one of the inputs in the {row["Ident-Nummer"]} line.\nSkipping Line..',
                    category=Warning, stacklevel=1)
                pass

if __name__ == '__main__':
    main()
