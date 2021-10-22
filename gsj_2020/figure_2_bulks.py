# Load modules
from inferelator import inferelator_workflow, inferelator_verbose_level, MPControl
from inferelator.benchmarking.scenic import SCENICWorkflow, SCENICRegression
from inferelator.distributed.inferelator_mp import MPControl

# Set verbosity level to "Talky"
inferelator_verbose_level(1)

# Set the location of the input data and the desired location of the output files

DATA_DIR = '~/repos/inferelator/data/bsubtilis'
OUTPUT_DIR = '/scratch/cj59/bsub_inference'

PRIORS_FILE_NAME = 'gold_standard.tsv.gz'
GOLD_STANDARD_FILE_NAME = 'gold_standard.tsv.gz'
TF_LIST_FILE_NAME = 'tf_names.tsv'

CV_SEEDS = list(range(42, 52))

# Multiprocessing uses the pathos implementation of multiprocessing (with dill instead of cPickle)
# This is suited for a single computer but will not work on a distributed cluster

n_cores_local = 10
local_engine = True

# Multiprocessing needs to be protected with the if __name__ == 'main' pragma
if __name__ == '__main__' and local_engine:
    MPControl.set_multiprocess_engine("multiprocessing")
    MPControl.client.set_processes(n_cores_local)
    MPControl.connect()


# Define the general run parameters
def set_up_workflow(wkf):
    wkf.set_file_paths(input_dir=DATA_DIR,
                       output_dir=OUTPUT_DIR,
                       tf_names_file=TF_LIST_FILE_NAME,
                       priors_file=PRIORS_FILE_NAME,
                       gold_standard_file=GOLD_STANDARD_FILE_NAME)
    wkf.set_file_properties(expression_matrix_columns_are_genes=False)
    wkf._do_preprocessing = False
    wkf.do_scenic = False
    wkf.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True, cv_split_ratio=0.2)
    return wkf


# Data Set 1

# Create a worker
worker = inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
worker = set_up_workflow(worker)
worker.set_file_paths(meta_data_file="meta_data.tsv")
worker.set_expression_file(tsv="expression.tsv.gz")
worker.adjacency_method = "grnboost2"

worker.append_to_path("output_dir", "set1_grnboost")
worker.run()

# Create a worker
worker = inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
worker = set_up_workflow(worker)
worker.set_file_paths(meta_data_file="meta_data.tsv")
worker.set_expression_file(tsv="expression.tsv.gz")
worker.adjacency_method = "genie3"

worker.append_to_path("output_dir", "set1_genie3")
worker.run()

# Data Set 2

# Create a worker
worker = inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
worker = set_up_workflow(worker)
worker.set_file_paths(meta_data_file="GSE67023_meta_data.tsv")
worker.set_expression_file(tsv="GSE67023_expression.tsv.gz")
worker.adjacency_method = "grnboost2"

worker.append_to_path("output_dir", "set2_grnboost")
worker.run()

# Create a worker
worker = inferelator_workflow(regression=SCENICRegression, workflow=SCENICWorkflow)
worker = set_up_workflow(worker)
worker.set_file_paths(meta_data_file="GSE67023_meta_data.tsv")
worker.set_expression_file(tsv="GSE67023_expression.tsv.gz")
worker.adjacency_method = "genie3"

worker.append_to_path("output_dir", "set2_genie3")
worker.run()