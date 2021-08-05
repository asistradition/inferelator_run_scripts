from inferelator import utils
from inferelator import workflow
from inferelator import crossvalidation_workflow
from inferelator.benchmarking.celloracle import CellOracleWorkflow ,CellOracleRegression
from inferelator.distributed.inferelator_mp import MPControl

YEASTRACT_PRIOR = "YEASTRACT_20190713_BOTH.tsv"
YEASTRACT_TF_NAMES = "tf_names_yeastract.txt"

INPUT_DIR = '/home/cj59/Documents/celloracle'
OUTPUT_PATH = '/scratch/cj59/gsj_2020_celloracle'

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


if __name__ == '__main__':

    worker = workflow.inferelator_workflow(regression=CellOracleRegression, workflow=CellOracleWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'full_build')
    worker.run()

    del worker

    worker = workflow.inferelator_workflow(regression=CellOracleRegression, workflow=CellOracleWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'full_build_shuffle')
    worker.set_shuffle_parameters(shuffle_prior_axis=0)
    worker.run()

    del worker

    worker = workflow.inferelator_workflow(regression=CellOracleRegression, workflow=CellOracleWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'full_build_noise')
    worker.set_shuffle_parameters(make_data_noise=True)
    worker.run()

    del worker