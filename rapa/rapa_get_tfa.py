from inferelator import (inferelator_workflow,
                         inferelator_verbose_level,
                         MPControl)

from inferelator.workflows.velocity_workflow import VelocityWorkflow
from inferelator.preprocessing.single_cell import normalize_expression_to_median

import gc
import argparse

inferelator_verbose_level(1)

ap = argparse.ArgumentParser()

ap.add_argument(
    "--expression",
    dest="expression",
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

REGRESSION = 'bbsr'

def set_up_workflow(wkf):

    wkf.set_file_paths(
        input_dir=INPUT_DIR,
        output_dir=OUTPUT_PATH,
        priors_file=YEASTRACT_PRIOR,
        tf_names_file=YEASTRACT_TF_NAMES,
        gold_standard_file='gold_standard.tsv.gz'
    )

    return wkf


if __name__ == "__main__":

    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.use_default_configuration("rusty_rome", n_jobs=0)
    MPControl.client.add_worker_conda("source ~/.local/anaconda3/bin/activate inferelator")

    if args.expression:
        worker = set_up_workflow(
            inferelator_workflow(regression=REGRESSION, workflow="single-cell")
        )
        worker.set_expression_file(h5ad=EXPRESSION_FILE)
        worker.set_count_minimum(0.05)
        worker.add_preprocess_step(normalize_expression_to_median)

        worker.set_tfa(
            tfa_output_file="2021_RAPA_TFA_EXPRESSION.tsv.gz"
        )

        worker.startup()

        del worker


    gc.collect()

    if args.denoised:
        worker = set_up_workflow(
            inferelator_workflow(regression=REGRESSION, workflow="single-cell")
        )
        worker.set_expression_file(h5ad=EXPRESSION_FILE, h5_layer='denoised')
        worker.set_tfa(
            tfa_output_file="2021_RAPA_TFA_DENOISED.tsv.gz"
        )

        worker.startup()

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
        worker.set_tfa(
            tfa_output_file="2021_RAPA_TFA_VELOCITY.tsv.gz"
        )

        worker.startup()

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
        worker.set_tfa(
            tfa_output_file="2021_RAPA_TFA_DECAY_20MIN.tsv.gz"
        )

        worker.startup()

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
        worker.set_tfa(
            tfa_output_file="2021_RAPA_TFA_DECAY_LATENT.tsv.gz"
        )

        worker.startup()

        del worker
