from inferelator import workflow
from inferelator.regression.elasticnet_multitask import ElasticNetByTaskRegressionWorkflow
from inferelator.preprocessing import single_cell

# Ugly hack for relative import from __main__ because fucking python, am I right?
import os

try:
    from . import jackson_2019_workflow_setup as ws
except ValueError:
    # Py2
    import imp

    (f, p, d) = imp.find_module("jackson_2019_workflow_setup",
                                [os.path.join(os.path.dirname(os.path.realpath(__file__)))])
    ws = imp.load_module("ws", f, p, d)
except ImportError:
    # Py3
    import importlib.machinery

    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "jackson_2019_workflow_setup.py")
    ws = importlib.machinery.SourceFileLoader("ws", filename).load_module()


def set_up_mtl_workflow(wkf):
    # Jackson single cell task
    task = wkf.create_task(task_name="Jackson_2019",
                           expression_matrix_file="103118_SS_Data.tsv.gz",
                           expression_matrix_columns_are_genes=True,
                           extract_metadata_from_expression_matrix=True,
                           expression_matrix_metadata=['Genotype', 'Genotype_Group', 'Replicate', 'Condition',
                                                       'tenXBarcode'],
                           workflow_type="single-cell",
                           count_minimum=0.05,
                           tasks_from_metadata=True,
                           meta_data_task_column="Condition")
    task.add_preprocess_step(single_cell.log2_data)
    return wkf


if __name__ == '__main__':
    ws.start_mpcontrol_dask(120)

    # Figure 6: Final Network
    worker = ws.set_up_workflow(workflow.inferelator_workflow(regression=ElasticNetByTaskRegressionWorkflow,
                                                              workflow="amusr"))
    worker = ws.yeastract(worker)
    worker = set_up_mtl_workflow(worker)
    worker.append_to_path('output_dir', 'figure_6_final')
    worker.gold_standard_file = ws.YEASTRACT_PRIOR
    worker.split_gold_standard_for_crossvalidation = False
    worker.split_priors_for_gold_standard = False
    worker.cv_split_ratio = None
    worker.num_bootstraps = 50
    worker.random_seed = 100
    worker.target_expression_filter = "union"
    worker.regulator_expression_filter = "intersection"
    worker.run()