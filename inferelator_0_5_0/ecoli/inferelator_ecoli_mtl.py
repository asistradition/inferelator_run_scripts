from inferelator import inferelator_verbose_level, workflow, MPControl, CrossValidationManager
import gc


##############################################################
## CHANGE THESE PARAMETERS                                  ##

## NUMBER OF PARALLEL PROCESSES TO RUN ##
N_PROCESSES = 8

## FILE NAMES ##
OUTPUT_PATH = "~/this_is_where_files_go"
DATA_FILE_PATH = "~/this_is_where_files_are"

TREATMENT_EXPRESSION_FILE = "TREATMENT_FILENAME.tsv"
CONTROL_EXPRESSION_FILE = "CONTROL_FILENAME.tsv"
PRIOR_KNOWLEDGE_NETWORK_FILE = "PRIOR_KNOWLEDGE.tsv"

# Set to None if you just want to use all the TFs in the
# Prior knowledge matrix
TF_NAMES_FILE = "TF_NAMES.tsv"

## RANDOM SEEDS FOR CROSSVALIDATION ##
RANDOM_SEEDS = list(range(16, 26))

##############################################################

## SET MULTIPROCESSING SETTINGS ##
MPControl.set_multiprocess_engine('multiprocessing')
MPControl.set_processes(N_PROCESSES)
MPControl.connect()

inferelator_verbose_level(1)

def create_job_workflow():

    ## SET PARAMETERS ##
    worker = workflow.inferelator_workflow(
        regression="amusr",
        workflow="multitask"
    )
    worker.set_file_paths(
        input_dir=DATA_FILE_PATH,
        output_dir=OUTPUT_PATH,
        tf_names_file=TF_NAMES_FILE,
        gold_standard_file=PRIOR_KNOWLEDGE_NETWORK_FILE
    )

    worker.set_run_parameters(
        num_bootstraps=10,
        use_numba=True
    )

    ## CREATE SEPARATE LEARNING TASKS FOR CONTROL AND TREATMENT ##
    control_task = worker.create_task(
        task_name="control",
        workflow_type="single-cell",
        count_minimum=0.05,
        expression_matrix_file=CONTROL_EXPRESSION_FILE,
        priors_file=PRIOR_KNOWLEDGE_NETWORK_FILE
    )

    treatment_task = worker.create_task(
        task_name="treatment",
        workflow_type="single-cell",
        count_minimum=0.05,
        expression_matrix_file=TREATMENT_EXPRESSION_FILE,
        priors_file=PRIOR_KNOWLEDGE_NETWORK_FILE
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
