<!-- heading declaration and main RDFa data declaration in HTML-->
<div xmlns:schema="https://schema.org/" typeof="schema:SoftwareSourceCode" id="software-1">
   <h1 property="schema:name">hydropulser database scripts</h1>
   <meta property="schema:codeRepository" content="https://github.com/test123-all/hydropulser-database-scripts">
   <meta property="schema:codeSampleType" content="full solution">
   <meta property="schema:license" content="https://interoperable-europe.ec.europa.eu/licence/european-union-public-licence-version-12-eupl">
   <meta property="schema:programmingLanguage" content="Python">
   <h2>Introduction:</h2>
   <p property="schema:description">
      This is the repository of the hydropulser database scripts, which build upon the scripts from the AIMS project 
      (<a href="https://www.aims-projekt.de/impressum-und-haftungsauschluss/" target="_blank">https://www.aims-projekt.de/impressum-und-haftungsauschluss/</a>) and the pyKRAKEN software 
      (<a href="https://git.rwth-aachen.de/aims/public/pyKRAKEN" target="_blank">https://git.rwth-aachen.de/aims/public/pyKRAKEN</a>) by 
      Nils Preuß (<a href="https://orcid.org/0000-0002-6793-8533" target="_blank">https://orcid.org/0000-0002-6793-8533</a>).<br>
      <br>
      This repository contains enhanced and automated versions of these scripts as functions, along with a wrapper script 
      that integrates these functions. The wrapper script also utilizes the FST Label Creator 
      (<a href="https://github.com/test123-all/fst-label-creator" target="_blank">https://github.com/test123-all/fst-label-creator</a>)
      to generate the corresponding sensor labels.<br>
      <br>
      These scripts generate RDF files for sensors, substances, and components, which are hosted on a GitLab repository
      structure behind a p_ID (persistent identifier) namespace, such as 
      <a href="https://w3id.org/fst/resource/" target="_blank">https://w3id.org/fst/resource/</a>, with a two-step
      redirect.<br>
      <br>
      The scripts inside this repository aim to provide a easy-to-use 'interface' for the user where data can be put
      into special Excel tables and create the RDF files with the data from these Excel files together with the scripts. 
      This approach attempts to lower the barriers to reuse the software toolchain by inexperienced users.  
      For example, creating RDF files for sensors requires only two scripts <code>generate_UUID7s.py</code> and 
      <code>generate_sensor_db_files.py</code> and one Excel table <code>sensor_table.xlsx</code>.<br>
      <br>
      Currently, no SHACL profiles are included, but implementing them is one of the logical next steps. <br>
      <br>
      As a first use case the primary repository, which includes all sub-repositories as submodules and maintains versioned files, is the
      'metadata hub repository' of the Chair of Fluid Systems (FST). 
      The metadata hub repository can currently be accessed at 
      <a href="https://git.rwth-aachen.de/fst-tuda/projects/rdm/metadata_hub" target="_blank">https://git.rwth-aachen.de/fst-tuda/projects/rdm/metadata_hub</a> 
      [as of January 2025].<br>
      Access is restricted to scientific staff (WiMis) and maintainers, as it contains repositories with sensitive data.<br>
      <br>
      For more information about the RDF data repository structure, the p_ID redirecting service infrastructure, and
      how these scripts are used in conjunction with them, please refer to the following paper:
      <ol>
          <li>
              <div>
                  <strong>
                      <span property="schema:name">How to Make Bespoke Experiments FAIR: Modular Dynamic Semantic Digital Twin and Open Source Information Infrastructure</span>
                      <span>(</span>
                      <a property="schema:relatedLink" href="https://preprints.inggrid.org/repository/view/40/" typeof="schema:Article"> 
                          <span>https://preprints.inggrid.org/repository/view/40/</span>
                      </a>
                      <span>)</span>
                  </strong>
                  <span>(January 2025, currently only available as a preprint.)</span>
              </div>
        </li>
      </ol>
   </p>
</div>


<b>DISCLAIMER:</b> <br>
This software in its current version is in an early proof of concept phase and used in the 
https://preprints.inggrid.org/repository/view/40/ paper and contributed to the results mentioned in the paper.<br>
<br>
Since this software is in an early proof of concept phase it is not commented out comprehensively yet,
the functional segregation isn't good and in conclusion the function and variable names might be subject to 
significant change in the future. Therefore, the backwards compatibility of the API won't be granted for now. <br>
<br>
Please note that we are no longer able to provide an exact time span for the refactoring work at this time, as the 
German government has recently reduced funding for scientific purposes overall, leaving the future of all sciences 
somewhat uncertain. Thank you very much for your understanding. <br>
<br>
Moreover it is currently discussed if this framework will be used in a broader field at the Chair of Fluid Systems
(Institut für Fluidsystemtechnik). If this should come true this repository will get archived after refactoring and
will be succeded by a broader more orderly and partly private repository.<br>
Also it is currently discussed if the approach to generate the data files should be replaced by a more efficient one in
the future. This would also result in the archiving of this repository and at least one succeeding repository.


## Installation:
### Installation on Windows with venv:
0. Please make sure, you have python3 (>3.10 https://www.python.org/) and inkscape (https://inkscape.org/) installed
1. Clone or download this hydropulser database scripts git-repository
2. Please navigate with your command line program inside the folder where this README.md is located (for example with `cd C:\Users\Neumeier\Desktop\hydropulser-database-scripts`)
3. Inside this folder run with the Windows command line "cmd" the command `py -m venv env`. (This will create a virtual environment, that won't mess up your system python installation)
4. Next run the command `.\env\Scripts\activate` to activate that environment
5. After setting up the virtual environment you are ready to install the neccessary packages with the command `py -m pip install qrcode reportlab svglib pandas openpyxl rdflib numpy uuid6`
6. Next you are able to run the script with for example `python .\generate_UUID7s.py` or `python .\generate_sensor_db_files.py` 

7. At the end please deactivate the virtual environment with `.\env\Scripts\deactivate`

### Installation on Linux or every other OS:
Please use poetry (https://python-poetry.org/) the python package manager or venv with the corresponding shell scripts 
(shell scripts have the '.sh' suffix).


## Getting started:
### How to create UUIDs for my objects?:
Just run the `generate_UUID7s.py` script located inside the root directory of this repository with `python ./generate_UUID7s.py` .
For installation instructions please have a look at the 'Installation'-section of this README.md file.
The script creates a directory called `_generated_UUIDs` with a .csv file inside with the name `saved_UUID7s.csv` that contains 
10 UUID7s. If you run the script multiple times the data will be overwritten, and you will get 10 new UUID7s.
If you want to change the quantity of generated UUID7s please open the `generate_UUID7s.py` script and change the `10`
inside the `def main(quanitity_of_UUID7s :int = 10):` line to a natural number of the amount of UUID7s you rather like 
to generate (for example `20`).  


### How can I create rdf files for a data repository?:
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
3. Run the file with `python ./generate_sensor_db_files.py` that will generate sensor directories inside a generated
`./hardcoded_generate_scripts/_generated` directory that are named after the single UUID7s of the sensors and 
contain the corresponding rdf files and the generated README.md
4. Copy the generated sensor directories from this repository to your cloned data repository.
5. Commit them to the data repository.
6. Push the commit[s].
7. And make sure all overlying data repositories, that contain the mentioned data repository as a submodule, are updated
to the newest version of the underlying data repositories. This makes sure that the CI/CD pipeline of the data hub repository gets initiated and
is able to generate the redirect files.


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
  
  
## Possible Improvements:
The following list includes possible improvements that have been identified up to this version:
- The scripts of the AIMS project are mainly hardcoded especially 
  - for the components (`gitlab_db_component.py`) and the substances (`gitlab_db_substance.py`).
  - the `gitlab_db_mdgen.py` to the sensors and doesn't work with components and substances.
- Enhance the rdf sensor files by different uncertainties and the possibility of declaring these uncertainties inside
the `sensor_table.xlsx`.


## Current To Do List:
- How to automatically add images to the sensor README.md files?
- Since there is a README.md file present for the one example component of the FST. Is there a script for it or is it created 
by hand? 


## Dependencies:
This repository uses the following third party python packages and software as dependency:

- FST Label Creator _ GNU Lesser General Public License v3 (LGPLv3) (https://github.com/test123-all/fst-label-creator [Last Access at 14th January 2025])

**The scripts from the AIMS project by Nils Preuß _ licensed under the EUROPEAN UNION PUBLIC LICENCE v. 1.2 ** <br>
- rdflib _ BSD License (BSD-3-Clause) (https://rdflib.dev/ [Last Access at 14th January 2025])
- uuid6 _ MIT License (MIT) (https://github.com/oittaa/uuid6-python [Last Access at 14th January 2025]) 
- pandas + openpyxl _ BSD License (BSD 3-Clause License) + MIT License (MIT) (to load the data of the excel sheets) (https://pandas.pydata.org/ [Last Access at 14th January 2025]) (https://pypi.org/project/openpyxl/ [Last Access at 14th January 2025])
- numpy _ BSD License(https://numpy.org/ [Last Access at 14th January 2025])

Since this scripts directly build upon the scripts from the AIMS project, the current license choice is also the
EUROPEAN UNION PUBLIC LICENCE v. 1.2 .

<!-- maintainer- and creator- RDFa data declaration in HTML-->
<div xmlns:schema="https://schema.org/" about="#software-1">
    <h2>Current Maintainer[s]:</h2>
    <div typeof="schema:Person">
        <strong property="schema:givenName">Sebastian</strong>
        <strong property="schema:familyName">Neumeier</strong>
        <strong>(<a href="https://orcid.org/0000-0001-9533-9004" property="schema:identifier">https://orcid.org/0000-0001-9533-9004</a>)</strong>
        <span property="schema:email">sebastian.neumeieratstud.tu-darmstadt.de</span>
    </div>
    <h2>Authors:</h2>
    <p xmlns:dcterms="http://purl.org/dc/terms/">The first scripts in this repository used to generate usable datasets 
        were originally created in
        <span property="dcterms:date" content="2023-10-01">October 2023</span>,
        <span property="dcterms:date" content="2023-10-01">November 2023</span>
        and
        <span property="dcterms:date" content="2023-10-01">December 2023</span>
        by:
    </p>
    <div typeof="schema:Person">
        <strong property="schema:givenName">Sebastian</strong>
        <strong property="schema:familyName">Neumeier</strong>
        <strong>(<a href="https://orcid.org/0000-0001-9533-9004" property="schema:identifier">https://orcid.org/0000-0001-9533-9004</a>)</strong>
        , <span property="schema:affiliation">
            Chair of Fluid Systems at Technical University of Darmstadt 
            (<a href="https://ror.org/05n911h24">https://ror.org/05n911h24</a>)
        </span>
        : <span property="schema:role">Conceptualization, Implementation, Documentation</span>.
    </div>
    <div typeof="schema:Person">
        <strong property="schema:givenName">Manuel</strong>
        <strong property="schema:familyName">Rexer</strong>
        <strong>(<a href="https://orcid.org/0000-0003-0559-1156" property="schema:identifier">https://orcid.org/0000-0003-0559-1156</a>)</strong>
        , <span property="schema:affiliation">
            Chair of Fluid Systems at Technical University of Darmstadt 
            (<a href="https://ror.org/05n911h24">https://ror.org/05n911h24</a>)
        </span>
        : <span property="schema:role">Project Manager, Provider of the Use Cases, Supervision</span>.
    </div>
    <div typeof="schema:Person">
        <strong property="schema:givenName">Nils</strong>
        <strong property="schema:familyName">Preuß</strong>
        <strong>(<a href="https://orcid.org/0000-0002-6793-8533" property="schema:identifier">https://orcid.org/0000-0002-6793-8533</a>)</strong>
        , <span property="schema:affiliation">
            Chair of Fluid Systems at Technical University of Darmstadt 
            (<a href="https://ror.org/05n911h24">https://ror.org/05n911h24</a>)
        </span>
        : <span property="schema:role">Help with better understanding the code and software stack of the AIMS project, Feedback</span>.
    </div>
</div>

## Additional Ressources:
This software is somehow connected to the following paper[s] or contributed to the results of the following papers:
<ol>
   <li>
       <div>
           <strong>
               <span property="schema:name">How to Make Bespoke Experiments FAIR: Modular Dynamic Semantic Digital Twin and Open Source Information Infrastructure</span>
               <span>(</span>
               <a property="schema:relatedLink" href="https://preprints.inggrid.org/repository/view/40/" typeof="schema:Article"> 
                   <span>https://preprints.inggrid.org/repository/view/40/</span>
               </a>
               <span>)</span>
           </strong>
           <span>(January 2025, currently only available as a preprint.)</span>
       </div>
   </li>
</ol>