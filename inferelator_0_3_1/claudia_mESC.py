from inferelator import utils
from inferelator import workflow
from inferelator.distributed.inferelator_mp import MPControl

N_CORES = 100
CONDA_ACTIVATE_PATH = '~/.local/anaconda3/bin/activate'

utils.Debug.set_verbose_level(1)


def start_mpcontrol_dask(n_cores=N_CORES):
    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.minimum_cores = n_cores
    MPControl.client.maximum_cores = n_cores
    MPControl.client.walltime = '48:00:00'
    MPControl.client.add_worker_env_line('module load slurm')
    MPControl.client.add_worker_env_line('module load gcc/8.3.0')
    MPControl.client.add_worker_env_line('source ' + CONDA_ACTIVATE_PATH)
    MPControl.client.cluster_controller_options.append("-p ccb")
    MPControl.client.memory = "500GB"
    MPControl.client.job_mem = "500GB"
    MPControl.connect()


if __name__ == '__main__':
    start_mpcontrol_dask(100)

    for seed in range(42, 52):
        worker = workflow.inferelator_workflow(regression="bbsr", workflow="tfa")
        worker.set_file_paths(input_dir='~/fi-inferelator_sc/data/mESC_test_network',
                              output_dir='~/fi-inferelator_sc/data/mESC_test_network',
                              expression_matrix_file='srr_fpkm.tsv',
                              tf_names_file="TF_names.tsv",
                              gold_standard_file="mESC_ATAC_prior_matrix.tsv",
                              priors_file="mESC_ATAC_prior_matrix.tsv")
        worker.set_file_properties(expression_matrix_columns_are_genes=False)
        worker.set_run_parameters(num_bootstraps=5,
                                  random_seed=seed)
        worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True,
                                              cv_split_ratio=0.2)
        worker.set_shuffle_parameters(shuffle_prior_axis=0)
        worker.append_to_path('output_dir', "mESC_shuffled_complete_bbsr_" + str(seed))
        worker.run()

        del worker
