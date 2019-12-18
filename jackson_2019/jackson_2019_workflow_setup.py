from inferelator import crossvalidation_workflow
from inferelator import utils
from inferelator.distributed.inferelator_mp import MPControl
from inferelator.preprocessing import single_cell

N_CORES = 60

CONDA_ACTIVATE_PATH = '~/.local/anaconda3/bin/activate'
EXPRESSION_MATRIX_METADATA = ['Genotype', 'Genotype_Group', 'Replicate', 'Condition', 'tenXBarcode']

YEASTRACT_PRIOR = "YEASTRACT_20190713_BOTH.tsv"

TF_NAMES = "tf_names_gold_standard.txt"
YEASTRACT_TF_NAMES = "tf_names_yeastract.txt"

INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/yeast'
OUTPUT_PATH = '/mnt/ceph/users/cjackson/jackson_2019_inferelator_v032'


def yeastract(wkf):
    wkf.set_file_paths(tf_names_file=YEASTRACT_TF_NAMES, priors_file=YEASTRACT_PRIOR)


def set_up_workflow(wkf):

    wkf.set_file_paths(input_dir=INPUT_DIR,
                       output_dir=OUTPUT_PATH,
                       expression_matrix_file='103118_SS_Data.tsv.gz',
                       gene_metadata_file='orfs.tsv',
                       gold_standard_file='gold_standard.tsv',
                       priors_file='gold_standard.tsv',
                       tf_names_file=TF_NAMES)
    wkf.set_file_properties(extract_metadata_from_expression_matrix=True,
                            expression_matrix_metadata=EXPRESSION_MATRIX_METADATA,
                            expression_matrix_columns_are_genes=True,
                            gene_list_index="SystematicName")
    wkf.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True,
                                       cv_split_ratio=0.5)
    wkf.set_run_parameters(num_bootstraps=5)
    wkf.set_count_minimum(0.05)
    wkf.add_preprocess_step(single_cell.log2_data)
    return wkf


def set_up_fig5a(wkf):
    cv_wrap = crossvalidation_workflow.CrossValidationManager(wkf)
    cv_wrap.add_gridsearch_parameter('random_seed', list(range(42, 52)))
    return cv_wrap


def set_up_fig5b(wkf):
    cv_wrap = crossvalidation_workflow.CrossValidationManager(wkf)
    cv_wrap.add_gridsearch_parameter('random_seed', list(range(42, 52)))
    cv_wrap.add_size_subsampling([0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 0.75, 1], seed=86)
    return cv_wrap


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
