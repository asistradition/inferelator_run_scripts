from inferelator import (CrossValidationManager,
                         inferelator_workflow,
                         inferelator_verbose_level,
                         MPControl)

from inferelator.workflows.velocity_workflow import VelocityWorkflow
from inferelator.preprocessing.single_cell import normalize_expression_to_median

import gc
import argparse

ap = argparse.ArgumentParser()

ap.add_argument(
    "--expression",
    dest="expression",
    action='store_const',
    const=True,
    default=False
)

ap.add_argument(
    "--stars",
    dest="stars",
    action='store_const',
    const=True,
    default=False
)

ap.add_argument(
    "--shuffle",
    dest="shuffle",
    action='store_const',
    const=True,
    default=False
)

ap.add_argument(
    "--denoised",
    dest="denoised",
    action='store_const',
    const=True,
    default=False
)

ap.add_argument(
    "--velocity",
    dest="velocity",
    action='store_const',
    const=True,
    default=False
)

ap.add_argument(
    "--decay_constant",
    dest="decay_constant",
    action='store_const',
    const=True,
    default=False
)

ap.add_argument(
    "--decay_variable",
    dest="decay_variable",
    action='store_const',
    const=True,
    default=False
)

args = ap.parse_args()

YEASTRACT_PRIOR = "YEASTRACT_20190713_BOTH.tsv.gz"
YEASTRACT_TF_NAMES = "tf_names_yeastract.txt"

EXPRESSION_FILE = "2021_RAPA_INFERELATOR.h5ad"

INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/RAPA/'
OUTPUT_PATH = '/mnt/ceph/users/cjackson/rapa_2022_networks'

if args.stars:
    REGRESSION = "stars"
else:
    REGRESSION = "bbsr"

if args.shuffle:
    SHUFFLE = True
else:
    SHUFFLE = False


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

    if SHUFFLE:
        wkf.set_shuffle_parameters(shuffle_prior_axis=0)

    if REGRESSION == "bbsr":
        wkf.set_regression_parameters(clr_only=True)
    elif REGRESSION == "stars":
        wkf.set_regression_parameters(max_iter=500)

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
    MPControl.client.use_default_configuration("rusty_rome", n_jobs=1)
    MPControl.client.add_worker_conda("source ~/.local/anaconda3/bin/activate inferelator")
    MPControl.client._await_all_workers = True

    if REGRESSION == "stars":
        MPControl.client.set_task_parameters(batch_size=1)
    elif REGRESSION == "bbsr":
        MPControl.client.set_task_parameters(batch_size=20)

    MPControl.connect()

    ### Expresssion Only ###

    if args.expression:
        worker = set_up_workflow(
            inferelator_workflow(regression=REGRESSION, workflow="single-cell")
        )
        worker.set_expression_file(h5ad=EXPRESSION_FILE)
        worker.set_count_minimum(0.05)
        worker.add_preprocess_step(normalize_expression_to_median)
        worker.append_to_path('output_dir', f'expression_{REGRESSION}')

        cv = set_up_cv(worker)
        cv.run()

        del cv
        del worker

    gc.collect()

    if args.denoised:
        worker = set_up_workflow(
            inferelator_workflow(regression=REGRESSION, workflow="single-cell")
        )
        worker.set_expression_file(h5ad=EXPRESSION_FILE, h5_layer='denoised')
        worker.append_to_path('output_dir', f'denoised_{REGRESSION}')

        cv = set_up_cv(worker)
        cv.run()

        del cv
        del worker

    gc.collect()

    if args.velocity:
        worker = set_up_workflow(
            inferelator_workflow(regression=REGRESSION, workflow=VelocityWorkflow)
        )
        worker.set_expression_file(h5ad=EXPRESSION_FILE, h5_layer='denoised')
        worker.set_velocity_parameters(
            velocity_file_name=EXPRESSION_FILE,
            velocity_file_type="h5ad",
            velocity_file_layer='velocity'
        )
        worker.append_to_path('output_dir', f'velocity_{REGRESSION}')

        cv = set_up_cv(worker)
        cv.run()

        del cv
        del worker

    gc.collect()

    if args.decay_constant:
        worker = set_up_workflow(
            inferelator_workflow(regression=REGRESSION, workflow=VelocityWorkflow)
        )
        worker.set_expression_file(h5ad=EXPRESSION_FILE, h5_layer='denoised')
        worker.set_velocity_parameters(
            velocity_file_name=EXPRESSION_FILE,
            velocity_file_type="h5ad",
            velocity_file_layer='velocity'
        )
        worker.set_decay_parameters(
            global_decay_constant=.0150515
        )
        worker.append_to_path('output_dir', f'decay_20min_{REGRESSION}')

        cv = set_up_cv(worker)
        cv.run()

        del cv
        del worker

    gc.collect()

    if args.decay_variable:
        worker = set_up_workflow(
            inferelator_workflow(regression=REGRESSION, workflow=VelocityWorkflow)
        )
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
        worker.append_to_path('output_dir', f'decay_latent_inferred_{REGRESSION}')

        cv = set_up_cv(worker)
        cv.run()

        del cv
        del worker

    gc.collect()
