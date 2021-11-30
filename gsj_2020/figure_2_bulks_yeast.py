# Load modules
from inferelator import inferelator_workflow, inferelator_verbose_level, MPControl, crossvalidation_workflow
from inferelator.benchmarking.scenic import SCENICWorkflow, SCENICRegression
from inferelator.distributed.inferelator_mp import MPControl

# Set verbosity level to "Talky"
inferelator_verbose_level(1)

# Set the location of the input data and the desired location of the output files

DATA_DIR = '~/repos/inferelator/data/yeast'
OUTPUT_DIR = '/scratch/cj59/yeast_inference'

PRIORS_FILE_NAME = 'YEASTRACT_20190713_BOTH.tsv'
GOLD_STANDARD_FILE_NAME = 'gold_standard.tsv.gz'
TF_LIST_FILE_NAME = 'tf_names.tsv'

# Multiprocessing needs to be protected with the if __name__ == 'main' pragma
if __name__ == '__main__':
    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.use_default_configuration("greene", n_jobs=2)
    MPControl.client.add_worker_conda("source /scratch/cgsb/gresham/no_backup/Chris/.conda/bin/activate scenic")
    MPControl.connect()


# Define the general run parameters
def set_up_workflow(wkf):
    wkf.set_file_paths(input_dir=DATA_DIR,
                       output_dir=OUTPUT_DIR,
                       tf_names_file=TF_LIST_FILE_NAME,
                       priors_file=PRIORS_FILE_NAME,
                       gold_standard_file=GOLD_STANDARD_FILE_NAME)
    
    wkf.set_output_file_names(curve_data_file_name="metric_curve.tsv.gz")
    return wkf

def set_up_cv_seeds(wkf):
    cv = crossvalidation_workflow.CrossValidationManager(wkf)
    cv.add_gridsearch_parameter('random_seed', list(range(42, 52)))
    return cv

# Data Set 1

if __name__ == '__main__':

    # Create a worker
    worker = inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
    worker = set_up_workflow(worker)
    worker.set_expression_file(tsv="calico_expression_matrix_raw_microarray.tsv.gz")
    worker.set_file_properties(extract_metadata_from_expression_matrix=True,
                            expression_matrix_metadata=['TF', 'strain', 'date', 'restriction', 'mechanism', 'time'],
                            metadata_handler="nonbranching")
    worker.adjacency_method = "grnboost2"
    worker.set_output_file_names(curve_data_file_name="metric_curve.tsv.gz")
    worker._do_preprocessing = False
    worker.do_scenic = False
    worker.append_to_path("output_dir", "set1_raw_grnboost")
    worker.run()

    # BBSR
    worker = inferelator_workflow(regression="bbsr", workflow="tfa")
    worker = set_up_workflow(worker)
    worker.set_expression_file(tsv="calico_expression_matrix_raw_microarray.tsv.gz")
    worker.set_file_properties(extract_metadata_from_expression_matrix=True,
                            expression_matrix_metadata=['TF', 'strain', 'date', 'restriction', 'mechanism', 'time'],
                            metadata_handler="nonbranching")
    worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True,
                                        cv_split_ratio=0.2)
    worker.set_run_parameters(num_bootstraps=5)
    worker.append_to_path("output_dir", "set1_raw_bbsr")
    worker.set_output_file_names(curve_data_file_name="metric_curve.tsv.gz")

    cv_wrap = set_up_cv_seeds(worker)
    cv_wrap.run()

    del cv_wrap
    del worker

    # STARS-LASSO
    worker = inferelator_workflow(regression="stars", workflow="tfa")
    worker = set_up_workflow(worker)
    worker.set_expression_file(tsv="calico_expression_matrix_raw_microarray.tsv.gz")
    worker.set_file_properties(extract_metadata_from_expression_matrix=True,
                            expression_matrix_metadata=['TF', 'strain', 'date', 'restriction', 'mechanism', 'time'],
                            metadata_handler="nonbranching")
    worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True,
                                        cv_split_ratio=0.2)
    worker.set_run_parameters(num_bootstraps=5)
    worker.append_to_path("output_dir", "set1_raw_stars")
    worker.set_output_file_names(curve_data_file_name="metric_curve.tsv.gz")

    cv_wrap = set_up_cv_seeds(worker)
    cv_wrap.run()

    del cv_wrap
    del worker

    # BBSR-BY-TASK
    worker = inferelator_workflow(regression="bbsr", workflow="multitask")
    worker = set_up_workflow(worker)

    # Calico data task
    task1 = worker.create_task(task_name="Calico_2019",
                                expression_matrix_file="calico_expression_matrix_raw.tsv.gz",
                                expression_matrix_columns_are_genes=True,
                                extract_metadata_from_expression_matrix=True,
                                expression_matrix_metadata=['TF', 'strain', 'date', 'restriction', 'mechanism',
                                                            'time'],
                                workflow_type="tfa",
                                metadata_handler="nonbranching")

    # Kostya data task
    task2 = worker.create_task(task_name="Kostya_2019",
                                expression_matrix_file="kostya_microarray_yeast.tsv.gz",
                                expression_matrix_columns_are_genes=True,
                                extract_metadata_from_expression_matrix=True,
                                expression_matrix_metadata=['isTs', 'is1stLast', 'prevCol', 'del.t', 'condName'],
                                workflow_type="tfa",
                                metadata_handler="branching")

    worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True,
                                        cv_split_ratio=0.2)
    worker.set_run_parameters(num_bootstraps=5)

    worker.append_to_path("output_dir", "set1_raw_joint_bbsr")
    cv_wrap = set_up_cv_seeds(worker)
    cv_wrap.run()

    del cv_wrap
    del worker

    # STARS-BY-TASK
    worker = inferelator_workflow(regression="stars", workflow="multitask")
    worker = set_up_workflow(worker)

    # Calico data task
    task1 = worker.create_task(task_name="Calico_2019",
                                expression_matrix_file="calico_expression_matrix_raw.tsv.gz",
                                expression_matrix_columns_are_genes=True,
                                extract_metadata_from_expression_matrix=True,
                                expression_matrix_metadata=['TF', 'strain', 'date', 'restriction', 'mechanism',
                                                            'time'],
                                workflow_type="tfa",
                                metadata_handler="nonbranching")

    # Kostya data task
    task2 = worker.create_task(task_name="Kostya_2019",
                                expression_matrix_file="kostya_microarray_yeast.tsv.gz",
                                expression_matrix_columns_are_genes=True,
                                extract_metadata_from_expression_matrix=True,
                                expression_matrix_metadata=['isTs', 'is1stLast', 'prevCol', 'del.t', 'condName'],
                                workflow_type="tfa",
                                metadata_handler="branching")
    
    worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True,
                                        cv_split_ratio=0.2)
    worker.set_run_parameters(num_bootstraps=5)

    worker.append_to_path("output_dir", "set1_raw_joint_stars")
    cv_wrap = set_up_cv_seeds(worker)
    cv_wrap.run()

    del cv_wrap
    del worker

    # AMUSR
    worker = inferelator_workflow(regression="amusr", workflow="multitask")
    worker = set_up_workflow(worker)

    # Calico data task
    task1 = worker.create_task(task_name="Calico_2019",
                                expression_matrix_file="calico_expression_matrix_raw.tsv.gz",
                                extract_metadata_from_expression_matrix=True,
                                expression_matrix_metadata=['TF', 'strain', 'date', 'restriction', 'mechanism',
                                                            'time'],
                                workflow_type="tfa",
                                metadata_handler="nonbranching")

    # Kostya data task
    task2 = worker.create_task(task_name="Kostya_2019",
                                expression_matrix_file="kostya_microarray_yeast.tsv.gz",
                                extract_metadata_from_expression_matrix=True,
                                expression_matrix_metadata=['isTs', 'is1stLast', 'prevCol', 'del.t', 'condName'],
                                workflow_type="tfa",
                                metadata_handler="branching")

    worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True,
                                        cv_split_ratio=0.2)
    worker.set_run_parameters(num_bootstraps=5, use_numba=True)

    worker.append_to_path("output_dir", "set1_raw_joint_amusr")
    cv_wrap = set_up_cv_seeds(worker)
    cv_wrap.run()

    del cv_wrap
    del worker

    """
    # Create a worker
    worker = inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
    worker = set_up_workflow(worker)
    worker.set_expression_file(tsv="calico_expression_matrix_raw_microarray.tsv.gz")
    worker.set_file_properties(extract_metadata_from_expression_matrix=True,
                            expression_matrix_metadata=['TF', 'strain', 'date', 'restriction', 'mechanism', 'time'],
                            metadata_handler="nonbranching")
    worker.adjacency_method = "genie3"

    worker.append_to_path("output_dir", "set1_genie3")
    worker.run()

    # Data Set 2

    # Create a worker
    worker = inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
    worker = set_up_workflow(worker)
    worker.set_expression_file(tsv="kostya_microarray_yeast.tsv.gz")
    worker.set_file_properties(extract_metadata_from_expression_matrix=True,
                            expression_matrix_metadata=['isTs', 'is1stLast', 'prevCol', 'del.t', 'condName'],
                            metadata_handler="branching")
    worker.adjacency_method = "grnboost2"

    worker.append_to_path("output_dir", "set2_grnboost")
    worker.run()

    # Create a worker
    worker = inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
    worker = set_up_workflow(worker)
    worker.set_expression_file(tsv="kostya_microarray_yeast.tsv.gz")
    worker.set_file_properties(extract_metadata_from_expression_matrix=True,
                            expression_matrix_metadata=['isTs', 'is1stLast', 'prevCol', 'del.t', 'condName'],
                            metadata_handler="branching")
    worker.adjacency_method = "genie3"

    worker.append_to_path("output_dir", "set2_genie3")
    worker.run()
    """
