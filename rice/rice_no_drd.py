from inferelator import utils
from inferelator import workflow
from inferelator import crossvalidation_workflow
from inferelator.preprocessing import single_cell
from inferelator.distributed.inferelator_mp import MPControl


CONDA_ACTIVATE_PATH = '~/.local/anaconda3/bin/activate'
EXPRESSION_MATRIX_METADATA = ['Genotype', 'Genotype_Group', 'Replicate', 'Condition', 'tenXBarcode']

MOTIF_PRIOR = "EGRIN_PRIOR_MOTIF.tsv"
NETWORK_PRIOR = "EGRIN_PRIOR_INFERRED.tsv"

INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/rice'
OUTPUT_PATH = '/mnt/ceph/users/cjackson/mz82_rice'

utils.Debug.set_verbose_level(1)


def set_up_workflow(wkf):
    wkf.set_file_paths(input_dir=INPUT_DIR,
                       output_dir=OUTPUT_PATH,
                       gold_standard_file='gold_standard.tsv')


    wkf.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True,
                                       cv_split_ratio=0.2)
    wkf.set_run_parameters(num_bootstraps=5)
    wkf.set_count_minimum(0.05)


def set_up_cv_seeds(wkf):
    cv = crossvalidation_workflow.CrossValidationManager(wkf)
    cv.add_gridsearch_parameter('random_seed', list(range(42, 52)))
    return cv


def set_up_dask(n_jobs=2):
    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.use_default_configuration("rusty_ccb", n_jobs=n_jobs)
    MPControl.client.add_worker_conda("source ~/.local/anaconda3/bin/activate inferelator")
    MPControl.client.add_slurm_command_line("--constraint=broadwell")
    MPControl.connect()


if __name__ == '__main__':
    set_up_dask()

    utils.Debug.vprint("Testing network prior", level=0)

    worker = workflow.inferelator_workflow(regression="stars", workflow="tfa")
    worker.drd_driver = None

    set_up_workflow(worker)
    worker.set_file_paths(priors_file=NETWORK_PRIOR)

    worker.append_to_path('output_dir', 'network_prior_stars')
    cv_wrap = set_up_cv_seeds(worker)
    cv_wrap.run()

    del cv_wrap
    del worker

    utils.Debug.vprint("Testing motif prior", level=0)

    worker = workflow.inferelator_workflow(regression="stars", workflow="tfa")
    worker.drd_driver = None

    set_up_workflow(worker)
    worker.set_file_paths(priors_file=MOTIF_PRIOR)

    worker.append_to_path('output_dir', 'motif_prior_stars')
    cv_wrap = set_up_cv_seeds(worker)
    cv_wrap.run()

    del cv_wrap
    del worker

    utils.Debug.vprint("Testing network prior", level=0)

    worker = workflow.inferelator_workflow(regression="bbsr", workflow="tfa")
    worker.drd_driver = None

    set_up_workflow(worker)
    worker.set_file_paths(priors_file=NETWORK_PRIOR)

    worker.append_to_path('output_dir', 'network_prior_bbsr')
    cv_wrap = set_up_cv_seeds(worker)
    cv_wrap.run()

    del cv_wrap
    del worker

    utils.Debug.vprint("Testing motif prior", level=0)

    worker = workflow.inferelator_workflow(regression="bbsr", workflow="tfa")
    worker.drd_driver = None

    set_up_workflow(worker)
    worker.set_file_paths(priors_file=MOTIF_PRIOR)

    worker.append_to_path('output_dir', 'motif_prior_bbsr')
    cv_wrap = set_up_cv_seeds(worker)
    cv_wrap.run()

    del cv_wrap
    del worker