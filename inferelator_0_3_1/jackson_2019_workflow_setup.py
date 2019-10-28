from inferelator import single_cell_cv_workflow
from inferelator import utils
from inferelator.distributed.inferelator_mp import MPControl
from inferelator.preprocessing import single_cell

N_CORES = 200
INPUT_DIR = '~/PycharmProjects/inferelator/data/yeast'
CONDA_ACTIVATE_PATH = '~/.local/anaconda3/bin/activate'

YEASTRACT_PRIOR = "YEASTRACT_20190713_BOTH.tsv"

TF_NAMES = "tf_names_gold_standard.txt"
YEASTRACT_TF_NAMES = "tf_names_yeastract.txt"

OUTPUT_PATH = '~/jackson_2019_inferelator/'


def yeastract(wkf):
    wkf.tf_names_file = YEASTRACT_TF_NAMES
    wkf.priors_file = YEASTRACT_PRIOR
    return wkf


def set_up_workflow(wkf):
    wkf.input_dir = INPUT_DIR
    wkf.output_dir = OUTPUT_PATH
    wkf.expression_matrix_file = '103118_SS_Data.tsv.gz'
    wkf.gene_metadata_file = "orfs.tsv"
    wkf.gene_list_index = "SystematicName"
    wkf.gold_standard_file = "gold_standard.tsv"
    wkf.priors_file = "gold_standard.tsv"
    wkf.tf_names_file = TF_NAMES
    wkf.expression_matrix_columns_are_genes = True
    wkf.extract_metadata_from_expression_matrix = True
    wkf.expression_matrix_metadata = ['Genotype', 'Genotype_Group', 'Replicate', 'Condition', 'tenXBarcode']
    wkf.split_gold_standard_for_crossvalidation = True
    wkf.cv_regression_type = "elasticnet"
    wkf.cv_split_ratio = 0.5
    wkf.num_bootstraps = 5
    wkf.add_preprocess_step(single_cell.log2_data)
    wkf.count_minimum = 0.05
    return wkf


def set_up_fig5a():
    wkf = set_up_workflow(single_cell_cv_workflow.SingleCellSizeSampling())
    wkf.random_seed = 1
    wkf.seeds = list(range(42, 52))
    wkf.sizes = [1]
    wkf.sample_with_replacement = False
    return wkf


def set_up_fig5b():
    wkf = set_up_workflow(single_cell_cv_workflow.SingleCellSizeSampling())
    wkf.random_seed = 1
    wkf.seeds = list(range(42, 62))
    wkf.sizes = [0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 0.75, 1]
    wkf.sample_with_replacement = False
    return wkf


def start_mpcontrol_dask(n_cores=N_CORES):
    utils.Debug.set_verbose_level(1)
    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.minimum_cores = n_cores
    MPControl.client.maximum_cores = n_cores
    MPControl.client.walltime = '48:00:00'
    MPControl.client.add_worker_env_line('module load slurm')
    MPControl.client.add_worker_env_line('module load gcc/8.3.0')
    MPControl.client.add_worker_env_line('source ' + CONDA_ACTIVATE_PATH)
    MPControl.client.cluster_controller_options.append("-p ccb")
    MPControl.connect()
