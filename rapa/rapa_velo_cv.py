from inferelator import (CrossValidationManager,
                         inferelator_workflow,
                         inferelator_verbose_level,
                         MPControl)

from inferelator.workflows.velocity_workflow import VelocityWorkflow

import gc

YEASTRACT_PRIOR = "YEASTRACT_20190713_BOTH.tsv.gz"
YEASTRACT_TF_NAMES = "tf_names_yeastract.txt"

EXPRESSION_FILE = "2021_RAPA_INFERELATOR.h5ad"

INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/RAPA'
OUTPUT_PATH = '/mnt/ceph/users/cjackson/rapa_2022_networks'

inferelator_verbose_level(1)

def set_up_workflow(wkf):
    wkf.set_file_paths(
        input_dir=INPUT_DIR,
        output_dir=OUTPUT_PATH,
        priors_file=YEASTRACT_PRIOR,
        tf_names_file=YEASTRACT_TF_NAMES,
        gold_standard_file='gold_standard.tsv.gz'
    )

    wkf.set_crossvalidation_parameters(
        split_gold_standard_for_crossvalidation=True,
        cv_split_ratio=0.2
    )

    wkf.set_run_parameters(
        num_bootstraps=5
    )

    return wkf

def set_up_cv(wkf):
    cv = CrossValidationManager(wkf)
    cv.add_gridsearch_parameter(
        'random_seed',
        list(range(42, 52))
    )

    return cv

if __name__ == "__main__":

    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.use_default_configuration("rusty_ccb", n_jobs=2)
    MPControl.client.add_worker_conda("source ~/.local/anaconda3/bin/activate inferelator")
    MPControl.client.add_slurm_command_line("--constraint=broadwell")
    MPControl.connect()

    ### Expresssion Only ###

    worker = inferelator_workflow(regression="stars", workflow="single-cell")
    worker.set_expression_file(h5ad=EXPRESSION_FILE)
    worker.set_count_minimum(0.05)
    worker.add_preprocess_step("log2")
    worker.append_to_path('output_dir', 'expression_stars')

    cv = set_up_cv(worker)
    cv.run()

    del cv
    del worker

    gc.collect()

    worker = inferelator_workflow(regression="stars", workflow="single-cell")
    worker.set_expression_file(h5ad=EXPRESSION_FILE, h5_layer='denoised')
    worker.add_preprocess_step("log2")
    worker.append_to_path('output_dir', 'denoised_stars')

    cv = set_up_cv(worker)
    cv.run()

    del cv
    del worker

    gc.collect()

    worker = inferelator_workflow(regression="stars", workflow=VelocityWorkflow)
    worker.set_expression_file(h5ad=EXPRESSION_FILE, h5_layer='denoised')
    worker.set_velocity_parameters(
        velocity_file_name=EXPRESSION_FILE,
        velocity_file_type="h5ad",
        velocity_file_layer='velocity'
    )
    worker.add_preprocess_step("log2")
    worker.append_to_path('output_dir', 'velocity_stars')

    cv = set_up_cv(worker)
    cv.run()

    del cv
    del worker

    gc.collect()

    worker = inferelator_workflow(regression="stars", workflow=VelocityWorkflow)
    worker.set_expression_file(h5ad=EXPRESSION_FILE, h5_layer='denoised')
    worker.set_velocity_parameters(
        velocity_file_name=EXPRESSION_FILE,
        velocity_file_type="h5ad",
        velocity_file_layer='velocity'
    )
    worker.set_decay_parameters(
        global_decay_constant=.0150515
    )
    worker.add_preprocess_step("log2")
    worker.append_to_path('output_dir', 'decay_20min_stars')

    cv = set_up_cv(worker)
    cv.run()

    del cv
    del worker

    gc.collect()

    worker = inferelator_workflow(regression="stars", workflow=VelocityWorkflow)
    worker.set_expression_file(h5ad=EXPRESSION_FILE, h5_layer='denoised')
    worker.set_velocity_parameters(
        velocity_file_name=EXPRESSION_FILE,
        velocity_file_type="h5ad",
        velocity_file_layer='velocity'
    )
    worker.set_decay_parameters(
        decay_constant_file=EXPRESSION_FILE,
        decay_constant_file_type="h5ad",
        decay_constant_file_layer='decay_constants'
    )
    worker.add_preprocess_step("log2")
    worker.append_to_path('output_dir', 'decay_latent_inferred_stars')

    cv = set_up_cv(worker)
    cv.run()

    del cv
    del worker

    gc.collect()
