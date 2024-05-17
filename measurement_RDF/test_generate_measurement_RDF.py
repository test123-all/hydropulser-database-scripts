import unittest
from pathlib import Path

from scipy.io import loadmat

from generate_measurement_RDF import parse_measurement_mat_file_to_RDF


class Testloadmat(unittest.TestCase):
    def test_loadmat(self):
        dir_path = Path(__file__).parent
        mat_file_path = Path(f'{dir_path}/515_231122_gaszylinder_10bar/018f3e2d-29a0-7e99-afe5-17eae266ef7f_gaszylinder_p0_10.15bar_p1_14bar_Ta_20C_harmonisch_02.00mm_02.50Hz.mat')
        mat_dict = loadmat(file_name=str(mat_file_path))

        parse_measurement_mat_file_to_RDF(mat_file_path=mat_file_path)

        # self.assertEqual(
        #     matlab_convert_to_hdf5_pywrapper.rexer_convert_mat_testdata_to_hdf5(
        #         project_directory_path=abs_path_to_the_testsdata_files.joinpath('/'),
        #         dst_directory_path=abs_path_to_the_testsdata_files.joinpath('/'),
        #         assignmenttable_filepath=abs_path_to_the_testsdata_files.joinpath('/note_200711_Bezeichung_messignale_Rexer.xlsx'),
        #         author_name='Sebastian Neumeier',
        #         project_manager_name='Manuel Rexer',
        #         experiment_name='Hydropulser',
        #         matlab_path=None))
