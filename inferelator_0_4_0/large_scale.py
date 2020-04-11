from inferelator import utils
from inferelator import workflow
from inferelator.distributed.inferelator_mp import MPControl
from inferelator.preprocessing import single_cell
from inferelator.crossvalidation_workflow import CrossValidationManager

N_CORES = 100
INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/e18_10x'
OUTPUT_DIR = '/mnt/ceph/users/cjackson/e18_10x/'
CONDA_ACTIVATE_PATH = '~/.local/anaconda3/bin/activate'
TF_NAMES = "Mouse_TF.txt"
EXPRESSION_DATA = "1M_neurons_filtered_gene_bc_matrices_h5.h5ad"
PRIORS_FILE = "SRR695628X_prior.tsv"

utils.Debug.set_verbose_level(1)


if __name__ == '__main__':
    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.use_default_configuration("rusty_ccb", n_jobs=5)
    MPControl.client.add_worker_conda("source ~/.local/anaconda3/bin/activate inferelator")
    MPControl.connect()

    worker = workflow.inferelator_workflow(regression="bbsr", workflow="single-cell")
    worker.set_file_paths(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR, tf_names_file=TF_NAMES,
                          priors_file=PRIORS_FILE, gold_standard_file=PRIORS_FILE)
    worker.set_expression_file(h5ad=EXPRESSION_DATA)
    worker.set_file_properties(expression_matrix_columns_are_genes=True)
    worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True, cv_split_ratio=0.2)
    worker.set_run_parameters(num_bootstraps=5)
    worker.set_count_minimum(0.05)
    worker.add_preprocess_step(single_cell.log2_data)
    worker.append_to_path('output_dir', "bbsr")
    worker.run()

    # Create a crossvalidation wrapper
    cv_wrap = CrossValidationManager(worker)

    cv_wrap.add_gridsearch_parameter('random_seed', list(range(42, 52)))

    # Run
    cv_wrap.run()
