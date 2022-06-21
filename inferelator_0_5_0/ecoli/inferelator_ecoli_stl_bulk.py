from inferelator import inferelator_verbose_level, workflow, MPControl, CrossValidationManager
import gc
import os

##############################################################
## CHANGE THESE PARAMETERS                                  ##

## NUMBER OF PARALLEL PROCESSES TO RUN ##
N_PROCESSES = 8

## FILE NAMES ##
OUTPUT_PATH = "/home/chris/Documents/network_inference"
DATA_FILE_PATH = "~/PycharmProjects/inferelator/data/DREAM5"

EXPRESSION_FILE = "DREAM5_ecoli_expression.tsv"
METADATA_FILE = "DREAM5_ecoli_meta_data.tsv"
PRIOR_KNOWLEDGE_NETWORK_FILE = "DREAM5_ecoli_gold_standard.tsv"
GOLD_STANDARD_FILE = "DREAM5_ecoli_gold_standard.tsv"

# Set to None if you just want to use all the TFs in the
# Prior knowledge matrix
TF_NAMES_FILE = "DREAM5_ecoli_tf_names.tsv"

## RANDOM SEEDS FOR CROSSVALIDATION ##
RANDOM_SEEDS = list(range(52, 62))

##############################################################

## SET MULTIPROCESSING SETTINGS ##
MPControl.set_multiprocess_engine('multiprocessing')
MPControl.set_processes(N_PROCESSES)

inferelator_verbose_level(1)

def create_job_workflow():

    ## SET PARAMETERS ##
    worker = workflow.inferelator_workflow(
        regression="bbsr",
        workflow="tfa"
    )
    worker.set_file_paths(
        input_dir=DATA_FILE_PATH,
        output_dir=OUTPUT_PATH,
        tf_names_file=TF_NAMES_FILE,
        expression_matrix_file=EXPRESSION_FILE,
        priors_file=PRIOR_KNOWLEDGE_NETWORK_FILE,
        gold_standard_file=PRIOR_KNOWLEDGE_NETWORK_FILE
    )

    worker.set_run_parameters(
        num_bootstraps=5,
        use_numba=True
    )

    worker.set_file_properties(
        metadata_handler='nonbranching'
    )

    return worker


## MP PROTECTION FOR WEIRD OSES ##
if __name__ == '__main__':

    ## SET UP A CROSS VALIDATION TO EVALUATE MODEL PERFORMANCE ##
    wkf = create_job_workflow()
    wkf.append_to_path('output_dir', 'crossvalidation')
    wkf.set_crossvalidation_parameters(
        split_gold_standard_for_crossvalidation=True,
        cv_split_ratio=0.2
    )

    cv_wrap = CrossValidationManager(wkf)
    cv_wrap.add_gridsearch_parameter('random_seed', RANDOM_SEEDS)
    cv_wrap.run()

    del wkf
    del cv_wrap

    gc.collect()

    ## BUILD A FINAL FULL NETWORK ##
    wkf = create_job_workflow()
    wkf.append_to_path('output_dir', 'final')
    wkf.set_run_parameters(
        num_bootstraps=50,
        random_seed=999
    )
    wkf.run()
