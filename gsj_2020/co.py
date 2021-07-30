from inferelator import utils
from inferelator import workflow
from inferelator import crossvalidation_workflow
from inferelator.regression.base_regression import BaseRegression
from inferelator.benchmarking.celloracle import CellOracleWorkflow
from inferelator.distributed.inferelator_mp import MPControl


CONDA_ACTIVATE_PATH = '~/.local/anaconda3/bin/activate'
EXPRESSION_MATRIX_METADATA = ['Genotype', 'Genotype_Group', 'Replicate', 'Condition', 'tenXBarcode']

YEASTRACT_PRIOR = "YEASTRACT_20190713_BOTH.tsv"

TF_NAMES = "tf_names_gold_standard.txt"
YEASTRACT_TF_NAMES = "tf_names_yeastract.txt"

INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/yeast'
OUTPUT_PATH = '/mnt/ceph/users/cjackson/gsj_2020_celloracle'

utils.Debug.set_verbose_level(1)


def set_up_workflow(wkf):
    wkf.set_file_paths(input_dir=INPUT_DIR,
                       output_dir=OUTPUT_PATH,
                       priors_file=YEASTRACT_PRIOR,
                       tf_names_file=YEASTRACT_TF_NAMES,
                       gold_standard_file='gold_standard.tsv')
    wkf.set_expression_file(h5ad='GSE144820_GSE125162.h5ad')

    wkf.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True,
                                       cv_split_ratio=0.2)


def set_up_cv_seeds(wkf):
    cv = crossvalidation_workflow.CrossValidationManager(wkf)
    cv.add_gridsearch_parameter('random_seed', list(range(42, 52)))
    return cv


if __name__ == '__main__':

    worker = workflow.inferelator_workflow(regression=BaseRegression, workflow=CellOracleWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'experimental')

    cv_wrap = set_up_cv_seeds(worker)
    cv_wrap.run()

    del cv_wrap
    del worker

    worker = workflow.inferelator_workflow(regression=BaseRegression, workflow=CellOracleWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'shuffle')
    worker.set_shuffle_parameters(shuffle_prior_axis=0)

    cv_wrap = set_up_cv_seeds(worker)
    cv_wrap.run()

    del cv_wrap
    del worker

    worker = workflow.inferelator_workflow(regression=BaseRegression, workflow=CellOracleWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'noise')
    worker.set_shuffle_parameters(make_data_noise=True)

    cv_wrap = set_up_cv_seeds(worker)
    cv_wrap.run()

    del cv_wrap
    del worker