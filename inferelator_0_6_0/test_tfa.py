from inferelator import (CrossValidationManager,
                         inferelator_workflow,
                         inferelator_verbose_level,
                         MPControl)

from inferelator.preprocessing.single_cell import normalize_expression_to_median

from inferelator.tfa import (
    RidgeTFA,
    ActivityOnlyPinvTFA
)

import gc

YEASTRACT_PRIOR = "YEASTRACT_20190713_BOTH.tsv.gz"
YEASTRACT_TF_NAMES = "tf_names_yeastract.txt"

EXPRESSION_FILE = "2021_RAPA_INFERELATOR.h5ad"

INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/RAPA/'
OUTPUT_PATH = '/mnt/ceph/users/cjackson/rapa_tfa_test'

REGRESSION = "stars"
RESULTS_DIR = "{method}_" + f"{REGRESSION}"

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
    MPControl.client.use_default_configuration("rusty_rome", n_jobs=0)
    MPControl.client.add_worker_conda("source ~/.local/anaconda3/bin/activate inferelator")

    MPControl.connect()

    ### Expresssion Only ###

    worker = set_up_workflow(
        inferelator_workflow(regression=REGRESSION, workflow="single-cell")
    )
    worker.set_expression_file(h5ad=EXPRESSION_FILE)
    worker.set_count_minimum(0.05)
    worker.add_preprocess_step(normalize_expression_to_median)

    worker.append_to_path('output_dir', RESULTS_DIR.format(method='pinv'))

    worker.set_tfa(tfa_driver=ActivityOnlyPinvTFA)

    cv = set_up_cv(worker)
    cv.run()

    del cv
    del worker

    gc.collect()

    worker = set_up_workflow(
        inferelator_workflow(regression=REGRESSION, workflow="single-cell")
    )
    worker.set_expression_file(h5ad=EXPRESSION_FILE)
    worker.set_count_minimum(0.05)
    worker.add_preprocess_step(normalize_expression_to_median)

    worker.append_to_path('output_dir', RESULTS_DIR.format(method='ridge'))

    worker.set_tfa(tfa_driver=RidgeTFA)

    cv = set_up_cv(worker)
    cv.run()

    del cv
    del worker

    gc.collect()
