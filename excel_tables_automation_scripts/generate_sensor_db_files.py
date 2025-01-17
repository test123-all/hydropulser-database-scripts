from importlib import import_module
from pathlib import Path

from hardcoded_generate_scripts.gitlab_db_sensor import run_script as generate_gitlab_db_sensor_files
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
    sensor_excel_sheet_name = 'sensor_table_EXAMPLE.xlsx'
    # The name of the WiMi you want to create the files for. This is the same information
    # you have inserted into the sensor table.
    responsible_WiMi = 'Rexer'
    # -------------------------------------------------------------------------------------



    path_to_sensor_excel_table = Path(f"{file_directory}/../excel_tables/{sensor_excel_sheet_name}")
    script_functions.generate_sensor_pID_label_sites_from_excel_sheets(path_for_generated_files= path_for_generated_labels,
                                                                       path_to_sensor_excel_sheet= path_to_sensor_excel_table,
                                                                       responsible_WiMi= responsible_WiMi)

    print('Start of the generation of the sensor files.')
    generate_gitlab_db_sensor_files(sensor_table_path= path_to_sensor_excel_table.resolve(), generated_files_directory_path= path_for_generated_PID_files.resolve())
    print('Generation of the sensor files successfully finished!')

    print('Start of the generation of the README.md files of the sensor directories.')
    generate_sensor_md_s_from_directory(sensors_directory_search_path= path_for_generated_PID_files.resolve())

if __name__ == '__main__':
    main()