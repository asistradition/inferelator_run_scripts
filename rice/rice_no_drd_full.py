from inferelator import utils
from inferelator import workflow
from inferelator import crossvalidation_workflow
from inferelator.preprocessing import single_cell
from inferelator.distributed.inferelator_mp import MPControl


CONDA_ACTIVATE_PATH = '~/.local/anaconda3/bin/activate'

EXPRESSION_FILE = "Oryza_expression_data_MZ82_2021.h5ad"
MOTIF_PRIOR = "EGRIN_PRIOR_MOTIF.tsv"
NETWORK_PRIOR = "EGRIN_PRIOR_INFERRED.tsv"

INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/rice'
OUTPUT_PATH = '/mnt/ceph/users/cjackson/mz82_rice'

utils.Debug.set_verbose_level(1)


def set_up_workflow(wkf, prior_file = MOTIF_PRIOR):
    wkf.set_file_paths(input_dir=INPUT_DIR,
                       output_dir=OUTPUT_PATH)

    wkf.set_file_paths(priors_file=prior_file, gold_standard_file=prior_file)
    wkf.set_expression_file(h5ad=EXPRESSION_FILE)
    wkf.set_run_parameters(num_bootstraps=100, random_seed=420)

def set_up_dask(n_jobs=2):
    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.use_default_configuration("rusty_ccb", n_jobs=n_jobs)
    MPControl.client.add_worker_conda("source ~/.local/anaconda3/bin/activate inferelator")
    MPControl.client.add_slurm_command_line("--constraint=broadwell")
    MPControl.connect()

def set_up_multithreading():
    MPControl.set_multiprocess_engine("multiprocessing")
    MPControl.client.set_processes(38)
    MPControl.connect()


if __name__ == '__main__':
    set_up_multithreading()

    utils.Debug.vprint("Full build", level=0)

    worker = workflow.inferelator_workflow(regression="bbsr", workflow="tfa")
    worker.drd_driver = None

    set_up_workflow(worker, prior_file=NETWORK_PRIOR)
    worker.append_to_path('output_dir', 'full_network_prior_bbsr')
    worker.run()

    worker = workflow.inferelator_workflow(regression="stars", workflow="tfa")
    worker.drd_driver = None

    set_up_workflow(worker, prior_file=NETWORK_PRIOR)
    worker.append_to_path('output_dir', 'full_network_prior_stars')
    worker.run()
