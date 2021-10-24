# Load modules
from inferelator import inferelator_workflow, inferelator_verbose_level, MPControl
from inferelator.benchmarking.scenic import SCENICWorkflow, SCENICRegression
from inferelator.distributed.inferelator_mp import MPControl

# Set verbosity level to "Talky"
inferelator_verbose_level(1)

# Set the location of the input data and the desired location of the output files

DATA_DIR = '~/repos/inferelator/data/yeast'
OUTPUT_DIR = '/scratch/cj59/yeast_inference'

PRIORS_FILE_NAME = 'gold_standard.tsv.gz'
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
    wkf._do_preprocessing = False
    wkf.do_scenic = False
    wkf.set_output_file_names(curve_data_file_name="metric_curve.tsv.gz")
    return wkf


# Data Set 1

# Create a worker
worker = inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
worker = set_up_workflow(worker)
worker.set_expression_file(tsv="calico_expression_matrix_log2.tsv.gz")
worker.set_file_properties(extract_metadata_from_expression_matrix=True,
                           expression_matrix_metadata=['TF', 'strain', 'date', 'restriction', 'mechanism', 'time'],
                           metadata_handler="nonbranching")
worker.adjacency_method = "grnboost2"

worker.append_to_path("output_dir", "set1_grnboost")
worker.run()

# Create a worker
worker = inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
worker = set_up_workflow(worker)
worker.set_expression_file(tsv="calico_expression_matrix_log2.tsv.gz")
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

