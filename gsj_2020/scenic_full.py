from inferelator import utils
from inferelator import workflow
from inferelator import crossvalidation_workflow
from inferelator.benchmarking.scenic import SCENICWorkflow, SCENICRegression
from inferelator.distributed.inferelator_mp import MPControl

YEASTRACT_PRIOR = "YEASTRACT_20190713_BOTH.tsv"
YEASTRACT_TF_NAMES = "tf_names_yeastract.txt"

INPUT_DIR = '/home/cj59/Documents/scenic'
OUTPUT_PATH = '/scratch/cj59/gsj_2020_scenic'

utils.Debug.set_verbose_level(1)

def set_up_workflow(wkf):
    wkf.set_file_paths(input_dir=INPUT_DIR,
                       output_dir=OUTPUT_PATH,
                       priors_file=YEASTRACT_PRIOR,
                       tf_names_file=YEASTRACT_TF_NAMES,
                       gold_standard_file='gold_standard.tsv')
    wkf.set_expression_file(h5ad='GSE144820_GSE125162.h5ad')
    wkf.dask_temp_path = '/scratch/cj59/'


if __name__ == '__main__':

    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.use_default_configuration("greene", n_jobs=2)
    MPControl.client.add_worker_conda("source /scratch/cgsb/gresham/no_backup/Chris/.conda/bin/activate scenic")
    MPControl.connect()

    worker = workflow.inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'scenic_full')
    worker.run()

    del worker

    worker = workflow.inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'scenic_full_shuffle')
    worker.set_shuffle_parameters(shuffle_prior_axis=0)
    worker.run()

    del worker

    worker = workflow.inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'scenic_full_noise')
    worker.set_shuffle_parameters(make_data_noise=True)
    worker.run()

    del worker

    worker = workflow.inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'grnboost_full')
    worker.do_scenic = False
    worker.run()

    del worker

    worker = workflow.inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'grnboost_shuffle')
    worker.set_shuffle_parameters(shuffle_prior_axis=0)
    worker.do_scenic = False
    worker.run()

    del worker

    worker = workflow.inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'grnboost_noise')
    worker.set_shuffle_parameters(make_data_noise=True)
    worker.do_scenic = False
    worker.run()

    del worker

    worker = workflow.inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'genie_full')
    worker.do_scenic = False
    worker.adjacency_method = 'genie3'
    worker.run()

    del worker

    worker = workflow.inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'genie_shuffle')
    worker.set_shuffle_parameters(shuffle_prior_axis=0)
    worker.do_scenic = False
    worker.adjacency_method = 'genie3'
    worker.run()

    del worker

    worker = workflow.inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
    set_up_workflow(worker)
    worker.append_to_path('output_dir', 'genie_noise')
    worker.adjacency_method = 'genie3'
    worker.set_shuffle_parameters(make_data_noise=True)
    worker.do_scenic = False
    worker.run()

    del worker