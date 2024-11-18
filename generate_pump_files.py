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
