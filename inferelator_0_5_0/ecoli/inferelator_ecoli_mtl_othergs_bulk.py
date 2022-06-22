from inferelator import inferelator_verbose_level, workflow, MPControl, CrossValidationManager
import gc


##############################################################
## CHANGE THESE PARAMETERS                                  ##

## NUMBER OF PARALLEL PROCESSES TO RUN ##
N_PROCESSES = 8

## FILE NAMES ##
OUTPUT_PATH = "/mnt/ceph/users/cjackson/ecoli"
DATA_FILE_PATH = "/mnt/ceph/users/cjackson/inferelator/data"

TASK1_EXPRESSION_FILE = "DREAM5/DREAM5_ecoli_expression.tsv"
TASK2_EXPRESSION_FILE = "GSE206047/GSE206047_ecoli_tpm.tsv.gz"

PRIOR_KNOWLEDGE_NETWORK_FILE = [
    ('regulondb', 'ecoli/regulondb_10_10.tsv.gz'),
    ('dream5', "DREAM5/DREAM5_ecoli_gold_standard.tsv")
    ('genetic_network', "ecoli/genetic_network.tsv.gz"),
    ('generegulation_tmp', "ecoli/generegulation_tmp.tsv.gz"),
]

# Set to None if you just want to use all the TFs in the
# Prior knowledge matrix
TF_NAMES_FILE = "DREAM5/DREAM5_ecoli_tf_names.tsv"

## RANDOM SEEDS FOR CROSSVALIDATION ##
RANDOM_SEEDS = list(range(16, 26))

##############################################################

inferelator_verbose_level(1)

def create_job_workflow(prior_file, regress='amusr'):

    ## SET PARAMETERS ##
    worker = workflow.inferelator_workflow(
        regress="amusr",
        workflow="multitask"
    )
    worker.set_file_paths(
        input_dir=DATA_FILE_PATH,
        output_dir=OUTPUT_PATH,
        tf_names_file=TF_NAMES_FILE,
        gold_standard_file=prior_file
    )

    worker.set_run_parameters(
        num_bootstraps=10,
        use_numba=True
    )

    ## CREATE SEPARATE LEARNING TASKS FOR CONTROL AND TREATMENT ##
    task1 = worker.create_task(
        task_name="DREAM5",
        workflow_type="tfa",
        expression_matrix_file=TASK1_EXPRESSION_FILE,
        priors_file=prior_file
    )

    task2 = worker.create_task(
        task_name="GSE206047",
        workflow_type="tfa",
        expression_matrix_file=TASK2_EXPRESSION_FILE,
        priors_file=prior_file
    )

    return worker

MPControl.set_multiprocess_engine("dask-cluster")
MPControl.client.use_default_configuration("rusty_ccb", n_jobs=0)
MPControl.client.add_worker_conda("source ~/.local/anaconda3/bin/activate inferelator")
MPControl.client.add_slurm_command_line("--constraint=broadwell")
MPControl.connect()

for r in ['amusr', 'bbsr', 'stars']:
    for name_str, path in PRIOR_KNOWLEDGE_NETWORK_FILE:
        ## SET UP A CROSS VALIDATION TO EVALUATE MODEL PERFORMANCE ##
        wkf = create_job_workflow(path, regress=r)
        wkf.append_to_path('output_dir', r)
        wkf.append_to_path('output_dir', name_str)
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
