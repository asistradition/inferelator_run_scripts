from inferelator import utils
from inferelator import workflow
from inferelator.distributed.inferelator_mp import MPControl
from inferelator.preprocessing import single_cell
from inferelator.preprocessing import tfa

N_CORES = 100
INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/e18_10x'
OUTPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/v031/'
CONDA_ACTIVATE_PATH = '~/.local/anaconda3/bin/activate'
TF_NAMES = "Mouse_TF.txt"
EXPRESSION_DATA = "1M_neurons.tsv.gz"


def start_mpcontrol_dask(n_cores=N_CORES):
    utils.Debug.set_verbose_level(1)
    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.minimum_cores = n_cores
    MPControl.client.maximum_cores = n_cores
    MPControl.client.walltime = '48:00:00'
    MPControl.client.add_worker_env_line('module load slurm')
    MPControl.client.add_worker_env_line('module load gcc/8.3.0')
    MPControl.client.add_worker_env_line('source ' + CONDA_ACTIVATE_PATH)
    MPControl.client.cluster_controller_options.append("-p ccb")
    MPControl.client.memory = "500GB"
    MPControl.connect()


if __name__ == '__main__':
    start_mpcontrol_dask(100)

    for seed in range(42, 52):
        worker = workflow.inferelator_workflow(regression="bbsr", workflow="single-cell")
        worker.set_file_paths(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR, expression_matrix_file=EXPRESSION_DATA,
                              tf_names_file=TF_NAMES)
        worker.set_network_data_flags(use_no_prior=True, use_no_gold_standard=True)
        worker.set_run_parameters(num_bootstraps=5, random_seed=seed)
        worker.tfa_driver = tfa.NoTFA
        worker.append_to_path('output_dir', "1M_neuron_" + str(seed))
        worker.run()

        del worker
