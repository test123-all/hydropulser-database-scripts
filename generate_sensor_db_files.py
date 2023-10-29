from importlib import import_module
from pathlib import Path

from hardcoded_generate_scripts.gitlab_db_sensor import run_script as generate_gitlab_db_sensor_files
from hardcoded_generate_scripts.gitlab_db_mdgen import generate_sensor_md_s_from_directory

# The fst label creator needs a string import since the dash sign '-' isn't supported inside the normal import
# statement.
file_directory = Path(__file__).parent.resolve()
script_functions = import_module(f'{file_directory}/fst-label-creator/fstlabelcreator/script_functions')

def main():
    path_for_generated_files = Path(f"{file_directory}/_generated")
    path_for_generated_labels = Path(f"{path_for_generated_files}/labels")



    # These are the variables you need to adjust ------------------------------------------
    sensor_excel_sheet_name = 'sensor_table.xlsx'
    # The name of the WiMi you want to create the files for. This is the same information
    # you have inserted into the sensor table.
    responsible_WiMi = 'Rexer'
    # -------------------------------------------------------------------------------------



    path_to_sensor_excel_table = Path(f"{file_directory}/{sensor_excel_sheet_name}")
    script_functions.generate_sensor_pID_label_sites_from_excel_sheets(path_for_generated_files= path_for_generated_labels,
                                                                       path_to_sensor_excel_sheet= path_to_sensor_excel_table,
                                                                       responsible_WiMi= responsible_WiMi)

    generate_gitlab_db_sensor_files(sensor_table_path=path_to_sensor_excel_table)
    generate_sensor_md_s_from_directory(sensors_directory_path=path_for_generated_files)


if __name__ == '__main__':
    main()