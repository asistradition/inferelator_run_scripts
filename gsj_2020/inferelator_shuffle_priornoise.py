from inferelator import utils
from inferelator import workflow
from inferelator import crossvalidation_workflow
from inferelator.preprocessing import single_cell
from inferelator.distributed.inferelator_mp import MPControl

YEASTRACT_PRIOR = "YEASTRACT_20190713_BOTH.tsv"
YEASTRACT_TF_NAMES = "tf_names_yeastract.txt"

INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/yeast'
OUTPUT_PATH = '/mnt/ceph/users/cjackson/gsj_2021_inferelator_priornoise'

utils.Debug.set_verbose_level(1)


def set_up_workflow(wkf):
    wkf.set_file_paths(input_dir=INPUT_DIR,
                       output_dir=OUTPUT_PATH,
                       priors_file=YEASTRACT_PRIOR,
                       tf_names_file=YEASTRACT_TF_NAMES,
                       gold_standard_file='gold_standard.tsv')
    wkf.append_to_path('output_dir', "noise")

    task = worker.create_task(task_name="Jackson_2019",
                              workflow_type="single-cell",
                              count_minimum=0.05,
                              tasks_from_metadata=True,
                              meta_data_task_column="Condition")
    task.set_expression_file(h5ad='GSE144820_GSE125162.h5ad')

    wkf.set_run_parameters(num_bootstraps=5)
    wkf.set_count_minimum(0.05)
    wkf.set_shuffle_parameters(shuffle_prior_axis=0)


def set_up_cv_seeds(wkf, seeds=list(range(42, 52))):
    cv = crossvalidation_workflow.CrossValidationManager(wkf)
    cv.add_gridsearch_parameter('random_seed', seeds)
    return cv


if __name__ == '__main__':

    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.use_default_configuration("rusty_ccb", n_jobs=3)
    MPControl.client.add_worker_conda("source ~/.local/anaconda3/bin/activate inferelator")
    MPControl.client.add_slurm_command_line("--constraint=broadwell")
    MPControl.connect()

    for prior_noise in [0, 0.01, 0.025, 0.05, 0.1]:

        worker = workflow.inferelator_workflow(regression="amusr", workflow="multitask")
        set_up_workflow(worker)
        worker.append_to_path('output_dir', 'noise_' + str(prior_noise))
        worker.set_shuffle_parameters(add_prior_noise=prior_noise) if prior_noise > 0 else None
        worker.add_preprocess_step("ftt")

        cv_wrap = set_up_cv_seeds(worker)
        cv_wrap.run()

        del cv_wrap
        del worker
