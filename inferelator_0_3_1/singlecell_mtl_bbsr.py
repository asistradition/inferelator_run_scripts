from inferelator import utils
from inferelator import workflow
from inferelator.distributed.inferelator_mp import MPControl
from inferelator.preprocessing import single_cell
from inferelator.regression.bbsr_multitask import BBSRByTaskRegressionWorkflow

N_CORES = 100
INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/yeast'
OUTPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/v031/'
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
    start_mpcontrol_dask(100)

    for seed in range(42, 52):
        worker = workflow.inferelator_workflow(regression=BBSRByTaskRegressionWorkflow, workflow="amusr")
        worker.input_dir = '/mnt/ceph/users/cjackson/inferelator/data/yeast'
        worker.append_to_path('output_dir', "fig5d_mtl_bbsr_seed_" + str(seed))
        worker.target_expression_filter = "union"
        worker.regulator_expression_filter = "intersection"
        worker.num_bootstraps = 5
        worker.random_seed = seed
        worker.split_gold_standard_for_crossvalidation = True
        worker.cv_split_ratio = 0.2
        worker.gold_standard_file = "gold_standard.tsv"
        worker.gene_metadata_file = "orfs.tsv"
        worker.gene_list_index = "SystematicName"
        worker.priors_file = YEASTRACT_PRIOR
        worker.tf_names_file = YEASTRACT_TF_NAMES

        # Jackson single cell task
        task = worker.create_task(task_name="Jackson_2019",
                                  expression_matrix_file="103118_SS_Data.tsv.gz",
                                  expression_matrix_columns_are_genes=True,
                                  extract_metadata_from_expression_matrix=True,
                                  expression_matrix_metadata=['Genotype', 'Genotype_Group', 'Replicate', 'Condition', 'tenXBarcode'],
                                  workflow_type="single-cell",
                                  count_minimum=0.05,
                                  tasks_from_metadata=True,
                                  meta_data_task_column="Condition")
        task.add_preprocess_step(single_cell.log2_data)

        worker.run()
        del worker
