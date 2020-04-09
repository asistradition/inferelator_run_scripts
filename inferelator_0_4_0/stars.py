from inferelator import utils
from inferelator import workflow
from inferelator.distributed.inferelator_mp import MPControl
from inferelator.preprocessing import single_cell
from inferelator.regression.bbsr_multitask import BBSRByTaskRegressionWorkflow

N_CORES = 100
INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/yeast'
OUTPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/v040/'
CONDA_ACTIVATE_PATH = '~/.local/anaconda3/bin/activate'
YEASTRACT_PRIOR = "YEASTRACT_20190713_BOTH.tsv"
TF_NAMES = "tf_names_gold_standard.txt"
YEASTRACT_TF_NAMES = "tf_names_yeastract.txt"


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
    MPControl.connect()


if __name__ == '__main__':
    start_mpcontrol_dask(60)

    for seed in range(42, 52):
        worker = workflow.inferelator_workflow(regression="stars", workflow="single-cell")
        worker.set_file_paths(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR, gold_standard_file="gold_standard.tsv",
                              gene_metadata_file="orfs.tsv", priors_file=YEASTRACT_PRIOR,
                              tf_names_file=YEASTRACT_TF_NAMES)
        worker.set_expression_file(tsv="103118_SS_Data.tsv.gz")
        worker.set_file_properties(gene_list_index="SystematicName", extract_metadata_from_expression_matrix=True,
                                   expression_matrix_metadata=['Genotype', 'Genotype_Group', 'Replicate', 'Condition', 'tenXBarcode'])
        worker.set_run_parameters(num_bootstraps=5, random_seed=seed)
        worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True, cv_split_ratio=0.2)

        worker.append_to_path('output_dir', "stars_lasso_" + str(seed))
        worker.set_count_minimum(0.05)
        worker.add_preprocess_step(single_cell.log2_data)

        worker.run()
        del worker