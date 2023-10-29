# hydropulser database scripts
## Introduction
This is the repository of the hydropulser database scripts, that are based on the scripts from the AIMS project 
(https://www.aims-projekt.de/impressum-und-haftungsauschluss/ and https://git.rwth-aachen.de/aims/public/pyKRAKEN) by 
Nils Preuß (https://orcid.org/0000-0002-6793-8533). <br>
These scripts generate the rdf files of sensors that are hosted on a gitlab instance behind a PID namespace like 
(https://w3id.org/fst/resource/) with a two step redirect. The genrated rdf and .md files are comittet and pushed to a
data repository that is a submodule of the metadata hub repository of the FST. The metadata hub repository of the FST
can be currently found at https://git.rwth-aachen.de/fst-tuda/projects/rdm/metadata_hub [State of end of october 2023]. <br> 
It is only visible to scientific staff (WiMis) and maintainer. 

This repository contains further enhanced and automated versions of these scripts as functions and also a wrapper script
that ties these functions together. The wrapper script also calls the FST Label Creator to generate the corresponding
sensor labels. 

Therefore, only two scripts, `generate_UUID7s.py` and `generate_sensor_db_files.py` and one
excel table `sensor_table.xlsx` file, that contains the data, are provided to the user as a small easy to use 'interface'.


## Installation
### Installation on Windows with venv:
0. Please make sure, you have python3 (>3.10 https://www.python.org/) and inkscape (https://inkscape.org/) installed
1. Clone or download this hydropulser database scripts git-repository
2. Please navigate with your command line program inside the folder where this README.md is located (for example with `cd C:\Users\Neumeier\Desktop\hydropulser-database-scripts`)
3. Inside this folder run with the Windows command line "cmd" the command `py -m venv env`. (This will create a virtual environment, that won't mess up your system python installation)
4. Next run the command `.\env\Scripts\activate` to activate that environment
5. After setting up the virtual environment you are ready to install the neccessary packages with the command `py -m pip install qrcode reportlab svglib pandas openpyxl rdflib numpy uuid6`
6. Next you are able to run the script with for example `python .\generate_UUID7s.py` or `python .\generate_sensor_db_files.py` 

7. At the end please deactivate the virtual environment with `.\env\Scripts\deactivate`

### Installation on Linux or every other OS
Please use poetry (https://python-poetry.org/) the python package manager or venv with the corresponding shell scripts 
(shell scripts have the '.sh' suffix).



## Getting started
### How to create UUIDs for my objects?
Just run the `generate_UUID7s.py` script located inside the root directory of this repository with `python .\generate_UUID7s.py`.
For installation isntructions please have a look at the 'Installation'-section of this README.md file.
The script creates a directory called '_generated_UUIDs' with a .csv file inside with the name 'saved_UUID7s.csv' that contains 
10 UUID7s. If you run the script multiple times the data will be overwritten, and you will get 10 new UUID7s.
If you want to change the quantity of generated UUID7s please open the `generate_UUID7s.py` script and change the `10`
inside the `def main(quanitity_ofUUID7s :int = 10):` line to a natural number of the amount of UUID7s you rather like 
to generate.  



### How can I create rdf files for a data repository and labels with a QR-code?
1. Fill in your data into the `sensor_table.xlsx` file. A example table with already filled in data is given by the
`sensor_table_EXAMPLE.xlsx` file. You should try to fill out all possible fields.
2. Change the following variables inside the `generate_sensor_db_files.py`. The code block is right in the middle of
the file and largely separated from the rest. You should therefore be able to find it quite easily.
```python
  # These are the variables you need to adjust ------------------------------------------
  sensor_excel_sheet_name = 'sensor_table.xlsx'
  # The name of the WiMi you want to create the files for. This is the same information
  # you have inserted into the sensor table.
  responsible_WiMi = 'Rexer'
  # -------------------------------------------------------------------------------------
```
3. Run the file with `python ./generate_sensor_db_files.py` that generates directories inside a 
`./hardcoded_generate_scripts/_generated that are named` that are named after the single UUIds of the sensors and 
contain the corresponding rdf files and the generated README.md
4. Copy the generated sensor directories inside of your cloned data repository.
5. Commit them.
6. Push the commit[s].
7. And make sure all overlying data repositories, that contain the mentioned data repository as a submodule, are updated
to the newest version of the underlying data repositories, to make sure that the CI/CD pipeline of the data hub repository gets initiated and
is able to generate the redirect files.
8. 

**Disclaimer:** <br>
Currently the fst label creator doesn't resolve the path of incscape on windows machines (since windows doesn't
resolve CLI tool names to the corresponding file, therefore an explicit standard path needs to be given, that isn't
implemented yet).

### Restrictions placed on the sensor table:
- Currently only sensors of the following type are supported (others might follow):
  - "Druck" (pressure), 
  - "Temperatur" (temperature),
  - "Kraft" (force),
  - "Weg" (displacement) <br>

- Currently only the following units for the sensors are supported inside the sensor table:
  - bar (bar)
  - mbar (milli bar)
  - psi (pound per square inch)
  - kPa (kilo pascal)
  - MPa (Mega pascal)
  - °C (degree centigrade)
  - K (kelvin)
  - N (newton)
  - kN (kilo newton)
  - mm (milli metre)
  - cm (centi metre)
  
  
## Improvement Suggestions
- The scripts of the AIMS project are mainly hardcoded especially 
  - for the components (`gitlab_db_component.py`) and the substances (`gitlab_db_substance.py`)
  - The `gitlab_db_mdgen.py` is hardcoded to the sensors
- Enhance the rdf sensor files by different uncertainties and the possibility of declaring these uncertainties inside
the sensor_table.xlsx 



## Current To Do List
- How to add images to the sensor README.md files?
- Since there is a README.md file present for the one example component of the FST. Is there a script for it or is it created 
by hand? 



## Dependencies:
This repository uses the following third party python packages and software as dependency:

**FST Label Creator:** <br>
- qrcode (https://pypi.org/project/qrcode/ [Last Access at 03th October 2023])
- reportlab open source version (https://pypi.org/project/reportlab/ [Last Access at 03th October 2023], https://docs.reportlab.com/reportlab/userguide/ch1_intro/ [Last Access at 03th October 2023])
- svglib (https://pypi.org/project/svglib/ [Last Access at 03th October 2023])
- pandas + openpyxl (to load the data of the excel sheets) (https://pandas.pydata.org/ [Last Access at 29th October 2023]) (https://pypi.org/project/openpyxl/ [Last Access at 29th October 2023])
- Inkscape (https://inkscape.org/ [Last Access at 03th October 2023])

**The scripts from the AIMS project by Nils Preuß** <br>
- rdflib (https://rdflib.dev/ [Last Access at 29th October 2023])
- uuid6 (https://github.com/oittaa/uuid6-python [Last Access at 29th October 2023]) 
- pandas + openpyxl (to load the data of the excel sheets) (https://pandas.pydata.org/ [Last Access at 29th October 2023]) (https://pypi.org/project/openpyxl/ [Last Access at 29th October 2023])
- numpy (https://numpy.org/ [Last Access at 29th October 2023])



## Current Maintainers:
sebastian.neumeier[at]stud.tu-darmstadt.de <br>
manuel.rexer[at]fst.tu-darmstadt.de <br>