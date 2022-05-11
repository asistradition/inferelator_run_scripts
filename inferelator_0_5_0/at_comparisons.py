from inferelator import utils
from inferelator import workflow
from inferelator import crossvalidation_workflow
from inferelator.preprocessing import single_cell
from inferelator.distributed.inferelator_mp import MPControl

import os
import csv

CONDA_ACTIVATE_PATH = '~/.local/anaconda3/bin/activate'
EXPRESSION_MATRIX_METADATA = ['Genotype', 'Genotype_Group', 'Replicate', 'Condition', 'tenXBarcode']

YEASTRACT_PRIOR = "YEASTRACT_20190713_BOTH.tsv"

TF_NAMES = "tf_names_gold_standard.txt"
YEASTRACT_TF_NAMES = "tf_names_yeastract.txt"

GOLD_STANDARD = 'gold_standard.tsv'

INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/yeast'
OUTPUT_PATH = '/mnt/ceph/users/cjackson/at_comps_named'

utils.Debug.set_verbose_level(1)


def set_up_workflow(wkf, priors, tfs):
    wkf.set_file_paths(input_dir=INPUT_DIR,
                       output_dir=OUTPUT_PATH,
                       priors_file=priors,
                       tf_names_file=tfs,
                       gold_standard_file=GOLD_STANDARD)

    task = worker.create_task(task_name="Jackson_2019",
                              workflow_type="single-cell",
                              count_minimum=0.05,
                              tasks_from_metadata=True,
                              meta_data_task_column="Condition")
    task.set_expression_file(h5ad='GSE144820_GSE125162.h5ad')

    wkf.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True,
                                       cv_split_ratio=0.2)
    wkf.set_run_parameters(num_bootstraps=10, use_numba=True)
    wkf.set_count_minimum(0.05)


def set_up_cv_seeds(wkf, seeds=list(range(42, 52))):
    cv = crossvalidation_workflow.CrossValidationManager(wkf)
    cv.add_gridsearch_parameter('random_seed', seeds)
    return cv


def set_up_dask(n_jobs=2):
    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.use_default_configuration("rusty_ccb", n_jobs=n_jobs)
    MPControl.client.add_worker_conda("source ~/.local/anaconda3/bin/activate inferelator")
    MPControl.client.add_slurm_command_line("--constraint=broadwell")
    MPControl.connect()


def _scores(result):
    return [result.all_scores[n] for n in ["AUPR", "F1", "MCC"]]


if __name__ == '__main__':
    set_up_dask()

    for out_dir, gs, tf_file in [('gs_to_gs', GOLD_STANDARD, TF_NAMES),
                                 ('yt_to_gs', YEASTRACT_PRIOR, YEASTRACT_TF_NAMES)]:

        with open(os.path.join(OUTPUT_PATH, out_dir, "crossvalidation_task_performance.tsv"), "w") as out_fh:

            csv_handler = csv.writer(out_fh, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_NONE)
            csv_handler.writerow(["Task", "Seed", "AUPR", "F1", "MCC"])

            for seed in range(42,52):

                worker = workflow.inferelator_workflow(regression="amusr", workflow="multitask")
                set_up_workflow(worker, gs, tf_file)
                worker.add_preprocess_step(single_cell.normalize_expression_to_median)
                worker.add_preprocess_step("ln")
                worker.append_to_path('output_dir', out_dir)
                worker.append_to_path('output_dir', f'random_seed_{seed}')
                worker.set_run_parameters(random_seed=seed)

                results = worker.run()
                csv_handler.writerow(["rank_combined", seed] + _scores(results))

                for t_id, t_name in enumerate(worker._task_names):
                    csv_handler.writerow([t_name, seed] + _scores(results.tasks[t_id]))

                out_fh.flush()
