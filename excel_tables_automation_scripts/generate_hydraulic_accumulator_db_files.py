from pathlib import Path
import numpy as np
import pandas as pd


from hardcoded_generate_scripts.gitlab_db_hydraulic_accumulator import generate_gitlab_hydraulic_accumulator_files
from hardcoded_generate_scripts.gitlab_db_mdgen import generate_sensor_md_s_from_directory

from fstlabelcreator import script_functions


def main():
    file_directory = Path(__file__).parent.resolve()
    path_for_generated_files = Path(f"{file_directory}/../_generated")
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
    sensor_excel_sheet_name = 'hydrospeicher_id_list.xlsx'
    # The name of the WiMi you want to create the files for. This is the same information
    # you have inserted into the sensor table.
    responsible_WiMi = 'Rexer'
    # -------------------------------------------------------------------------------------



    path_to_excel_table = Path(f"{file_directory}/../excel_tables/{sensor_excel_sheet_name}")

    print('Start of the generation of the sensor files.')
    dfs = pd.read_excel(path_to_excel_table, sheet_name=None,) #skiprows=[1])
    # sensor_dir = "C:/Users/NP/Documents/AIMS/metadata_hub/data/fst_measurement_equipment/"
    try:
        path_for_generated_files.mkdir()
    except FileExistsError:
        pass


    df = dfs['Sheet1']
    for idx in df.index:
        row = df.iloc[idx]
        row = row.replace({np.nan: None})

        if row['UUID'] is None:
            continue

        current_serial_number = str(row['Serial_number'])
        parsed_current_serial_number = current_serial_number.replace('“', '').replace('”', '')

        generate_gitlab_hydraulic_accumulator_files(save_to_dir=path_for_generated_PID_files,
                                                    hydraulic_accumulator_id=row['UUID'],
                                                    identifier=row['Product_number'],
                                                    manufacturer=row['Hersteller:'],
                                                    serial_number=parsed_current_serial_number,
                                                    hydraulic_accumulator_comment=row['Kommentar'],
                                                    hydraulic_accumulator_manufacturing_date=row['Herstellungsdatum'],
                                                    operating_pressure_value=row['PS'],
                                                    operating_pressure_unit=row['PS_UNIT'],
                                                    maximum_pressure_value=row['PT'],
                                                    maximum_pressure_unit=row['PT_UNIT'],
                                                    volume_value=row['Volumen'],
                                                    volume_unit=row['V_UNIT'],
                                                    volume_accuracy=row['Volumen_Unsicherheit'],
                                                    operating_temperature_range_minvalue=row['TS_min'],
                                                    operating_temperature_range_maxvalue=row['TS_max'],
                                                    operating_temperature_range_unit=row['TS_UNIT'])

    print('Generation of the files successfully finished!')

    print('Start of the generation of the README.md files of the directories.')
    generate_sensor_md_s_from_directory(sensors_directory_search_path=path_for_generated_PID_files.resolve())

if __name__ == '__main__':
    main()
