from inferelator import utils
from inferelator import workflow
from inferelator.distributed.inferelator_mp import MPControl
from inferelator.preprocessing import single_cell
from inferelator.regression.bbsr_multitask import BBSRByTaskRegressionWorkflow

N_CORES = 200
INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/yeast'
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

    for seed in range(42,52):
        worker = workflow.inferelator_workflow(regression=BBSRByTaskRegressionWorkflow, workflow="amusr")
        worker.input_dir = '/mnt/ceph/users/cjackson/inferelator/data/yeast'
        worker.append_to_path('output_dir', "mtl_seed_" + str(seed))
        worker.target_expression_filter = "union"
        worker.regulator_expression_filter = "intersection"
        worker.num_bootstraps = 5
        worker.random_seed = seed
        worker.split_gold_standard_for_crossvalidation = True
        worker.cv_split_ratio = 0.2

        # Jackson single cell task
        worker.create_task(task_name="Jackson_2019",
                           expression_matrix_file="103118_SS_Data.tsv.gz",
                           tf_names_file=TF_NAMES,
                           gene_metadata_file="orfs.tsv",
                           expression_matrix_columns_are_genes=True,
                           extract_metadata_from_expression_matrix=True,
                           expression_matrix_metadata=['Genotype', 'Genotype_Group', 'Replicate', 'Condition', 'tenXBarcode'],
                           priors_file=YEASTRACT_PRIOR,
                           workflow_type="single-cell",
                           preprocessing_workflow=[(single_cell.log2_data, {})],
                           count_minimum=0.05)

        # Calico data task
        worker.create_task(task_name="Calico_2019",
                           expression_matrix_file="calico_expression_matrix_log2.tsv.gz",
                           tf_names_file=TF_NAMES,
                           gene_metadata_file="orfs.tsv",
                           expression_matrix_columns_are_genes=True,
                           extract_metadata_from_expression_matrix=True,
                           expression_matrix_metadata=['TF', 'strain', 'date', 'restriction', 'mechanism', 'time'],
                           priors_file=YEASTRACT_PRIOR,
                           workflow_type="tfa",
                           metadata_handler="nonbranching")

        # Kostya data task
        worker.create_task(task_name="Kostya_2019",
                           expression_matrix_file="kostya_microarray_yeast.tsv.gz",
                           tf_names_file=TF_NAMES,
                           gene_metadata_file="orfs.tsv",
                           expression_matrix_columns_are_genes=True,
                           extract_metadata_from_expression_matrix=True,
                           expression_matrix_metadata=['isTs', 'is1stLast', 'prevCol', 'del.t', 'condName'],
                           priors_file=YEASTRACT_PRIOR,
                           workflow_type="tfa",
                           metadata_handler="branching")

        worker.run()
        del worker
