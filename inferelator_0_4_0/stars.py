from inferelator import utils
from inferelator import workflow
from inferelator.distributed.inferelator_mp import MPControl
from inferelator.preprocessing import single_cell
from inferelator.crossvalidation_workflow import CrossValidationManager

N_CORES = 100
INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/yeast'
OUTPUT_DIR = '/mnt/ceph/users/cjackson/stars_lasso'
CONDA_ACTIVATE_PATH = '~/.local/anaconda3/bin/activate'
YEASTRACT_PRIOR = "YEASTRACT_20190713_BOTH.tsv"
TF_NAMES = "tf_names_gold_standard.txt"
YEASTRACT_TF_NAMES = "tf_names_yeastract.txt"

utils.Debug.set_verbose_level(1)

if __name__ == '__main__':
    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.use_default_configuration("rusty_ccb", n_jobs=3)
    MPControl.client.add_worker_conda("source ~/.local/anaconda3/bin/activate inferelator")
    MPControl.connect()

    worker = workflow.inferelator_workflow(regression="stars", workflow="single-cell")
    worker.set_file_paths(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR, gold_standard_file="gold_standard.tsv",
                          gene_metadata_file="orfs.tsv", priors_file=YEASTRACT_PRIOR,
                          tf_names_file=YEASTRACT_TF_NAMES)
    worker.set_expression_file(tsv="103118_SS_Data.tsv.gz")
    worker.set_file_properties(gene_list_index="SystematicName", extract_metadata_from_expression_matrix=True,
                               expression_matrix_metadata=['Genotype', 'Genotype_Group', 'Replicate', 'Condition', 'tenXBarcode'])
    worker.set_run_parameters(num_bootstraps=5)
    worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True, cv_split_ratio=0.2)

    worker.append_to_path('output_dir', "single-cell")
    worker.set_count_minimum(0.05)
    worker.add_preprocess_step(single_cell.log2_data)

    # Create a crossvalidation wrapper
    cv_wrap = CrossValidationManager(worker)

    # Assign variables for grid search
    cv_wrap.add_gridsearch_parameter('random_seed', list(range(42, 52)))

    # Run
    cv_wrap.run()
    del worker
    del cv_wrap

    worker = workflow.inferelator_workflow(regression="stars", workflow="tfa")
    worker.set_file_paths(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR, gold_standard_file="gold_standard.tsv",
                          gene_metadata_file="orfs.tsv", priors_file=YEASTRACT_PRIOR,
                          tf_names_file=YEASTRACT_TF_NAMES)
    worker.set_expression_file(tsv="calico_expression_matrix_log2.tsv.gz")
    worker.set_file_properties(gene_list_index="SystematicName",
                               extract_metadata_from_expression_matrix=True,
                               expression_matrix_metadata=['TF', 'strain', 'date', 'restriction', 'mechanism', 'time'],
                               metadata_handler="nonbranching")
    worker.set_task_filters(target_expression_filter="union", regulator_expression_filter="intersection")
    worker.set_run_parameters(num_bootstraps=5)
    worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True, cv_split_ratio=0.2)

    worker.append_to_path('output_dir', "yeast_calico")

    # Create a crossvalidation wrapper
    cv_wrap = CrossValidationManager(worker)

    # Assign variables for grid search
    cv_wrap.add_gridsearch_parameter('random_seed', list(range(42, 52)))

    # Run
    cv_wrap.run()
    del worker
    del cv_wrap

