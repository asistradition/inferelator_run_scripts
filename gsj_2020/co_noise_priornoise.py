from inferelator import utils
from inferelator import workflow
from inferelator import crossvalidation_workflow
from inferelator.benchmarking.celloracle import CellOracleWorkflow ,CellOracleRegression
from inferelator.distributed.inferelator_mp import MPControl

YEASTRACT_PRIOR = "YEASTRACT_20190713_BOTH.tsv"
YEASTRACT_TF_NAMES = "tf_names_yeastract.txt"

INPUT_DIR = '/home/cj59/Documents/celloracle'
OUTPUT_PATH = '/scratch/cj59/gsj_2020_celloracle/prior_noise'

utils.Debug.set_verbose_level(1)

MPControl.set_multiprocess_engine("local")
MPControl.connect()

def set_up_workflow(wkf):
    wkf.set_file_paths(input_dir=INPUT_DIR,
                       output_dir=OUTPUT_PATH,
                       priors_file=YEASTRACT_PRIOR,
                       tf_names_file=YEASTRACT_TF_NAMES,
                       gold_standard_file='gold_standard.tsv')
    wkf.set_expression_file(h5ad='GSE144820_GSE125162.h5ad')
    wkf.append_to_path('output_dir', 'noise')
    wkf.set_shuffle_parameters(make_data_noise=True)

def set_up_cv_seeds(wkf):
    cv = crossvalidation_workflow.CrossValidationManager(wkf)
    cv.add_gridsearch_parameter('random_seed', list(range(42, 52)))
    return cv


if __name__ == '__main__':

    for prior_noise in [0.01, 0.025, 0.05, 0.1]:
        worker = workflow.inferelator_workflow(regression=CellOracleRegression, workflow=CellOracleWorkflow)
        set_up_workflow(worker)
        worker.append_to_path('output_dir', 'noise_' + str(prior_noise))
        worker.set_shuffle_parameters(add_prior_noise=prior_noise)

        cv_wrap = set_up_cv_seeds(worker)
        cv_wrap.run()

        del cv_wrap
        del worker

