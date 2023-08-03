# Load modules
from inferelator import (
    inferelator_workflow,
    inferelator_verbose_level,
    MPControl
)

from inferelator.benchmarking.scenic import (
    SCENICWorkflow,
    SCENICRegression
)

# Set verbosity level to "Talky"
inferelator_verbose_level(1)

DATA_DIR = '/mnt/ceph/users/cjackson/inferelator/data/bsubtilis'
YEAST_DATA_DIR = '/mnt/ceph/users/cjackson/inferelator/data/yeast'
OUTPUT_DIR = '/mnt/ceph/users/cjackson/supirfactor_genome_bio'

PRIORS_FILE_NAME = 'gold_standard.tsv.gz'
GOLD_STANDARD_FILE_NAME = 'gold_standard.tsv.gz'
TF_LIST_FILE_NAME = 'tf_names.tsv'

YEAST_TF_LIST_FILE_NAME = 'tf_names_yeastract.txt'
YEAST_GOLD_STANDARD = 'YEASTGENOME_PRIOR_YEASTRACT_MASK_20230711.tsv.gz'
YEAST_PRIOR = 'YEASTRACT_20190713_BOTH.tsv.gz'

AT_TF = "AT_TFs.tsv"
AT_GENES = "AT_GENES.tsv"

if __name__ == '__main__':
    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.use_default_configuration("rusty_rome", n_jobs=1)
    MPControl.client.add_worker_conda(
        "source ~/.local/anaconda3/bin/activate inferelator"
    )

    # Define the general run parameters
    def set_up_workflow(wkf, yeast=False, at=False):

        if at:
            wkf.set_file_paths(
                input_dir=YEAST_DATA_DIR,
                output_dir=OUTPUT_DIR,
                tf_names_file=AT_TF,
                priors_file=YEAST_PRIOR,
                gold_standard_file=YEAST_GOLD_STANDARD,
                gene_names_file=AT_GENES
            )

        elif yeast:
            wkf.set_file_paths(
                input_dir=YEAST_DATA_DIR,
                output_dir=OUTPUT_DIR,
                tf_names_file=YEAST_TF_LIST_FILE_NAME,
                priors_file=YEAST_PRIOR,
                gold_standard_file=YEAST_GOLD_STANDARD
            )

        else:
            wkf.set_file_paths(
                input_dir=DATA_DIR,
                output_dir=OUTPUT_DIR,
                tf_names_file=TF_LIST_FILE_NAME,
                priors_file=PRIORS_FILE_NAME,
                gold_standard_file=GOLD_STANDARD_FILE_NAME
            )
            wkf.set_file_properties(expression_matrix_columns_are_genes=False)

        wkf.set_output_file_names(curve_data_file_name="metric_curve.tsv.gz")
        return wkf

    # YEAST SINGLE CELL #
    worker = inferelator_workflow(
        regression='stars',
        workflow='single_cell'
    )
    worker = set_up_workflow(worker, yeast=True, at=True)
    worker.set_expression_file(
        h5ad="AT_YEAST_SINGLE_CELL.h5ad",
        h5_layer='robustminscaler'
    )
    worker.set_output_file_names(curve_data_file_name="metric_curve.tsv.gz")
    worker.append_to_path("output_dir", "yeast_single_cell_inferelator")
    worker.run()

    # BSUBTILIS #
    worker = inferelator_workflow(
        regression='stars',
        workflow='single_cell'
    )
    worker = set_up_workflow(worker)
    worker.set_file_paths(meta_data_file="meta_data.tsv")
    worker.set_expression_file(tsv="expression.tsv.gz")

    worker.append_to_path("output_dir", "bsub_set1_inferelator")
    worker.run()

    worker = inferelator_workflow(
        regression='stars',
        workflow='single_cell'
    )
    worker = set_up_workflow(worker)
    worker.set_file_paths(meta_data_file="GSE67023_meta_data.tsv")
    worker.set_expression_file(tsv="GSE67023_expression.tsv.gz")

    worker.append_to_path("output_dir", "bsub_set2_inferelator")
    worker.run()

    # YEAST #
    worker = inferelator_workflow(
        regression='stars',
        workflow='single_cell'
    )
    worker = set_up_workflow(worker, yeast=True)
    worker.set_expression_file(tsv="calico_expression_matrix_log2.tsv.gz")
    worker.set_file_properties(
        extract_metadata_from_expression_matrix=True,
        expression_matrix_metadata=['TF', 'strain', 'date', 'restriction', 'mechanism', 'time'],
        metadata_handler="nonbranching"
    )
    worker.append_to_path("output_dir", "yeast_set1_inferelator")
    worker.run()

    worker = inferelator_workflow(
        regression='stars',
        workflow='single_cell'
    )
    worker = set_up_workflow(worker, yeast=True)
    worker.set_expression_file(tsv="kostya_microarray_yeast.tsv.gz")
    worker.set_file_properties(
        extract_metadata_from_expression_matrix=True,
        expression_matrix_metadata=['isTs', 'is1stLast', 'prevCol', 'del.t', 'condName'],
        metadata_handler="branching"
    )
    worker.append_to_path("output_dir", "yeast_set2_inferelator")
    worker.run()
