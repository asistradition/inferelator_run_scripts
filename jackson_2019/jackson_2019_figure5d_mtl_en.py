from inferelator.postprocessing.results_processor_mtl import ResultsProcessorMultiTask
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
    ws.start_mpcontrol_dask(60)

    # Figure 5D: MTL
    worker = ws.set_up_fig5a()
    worker = ws.yeastract(worker)
    worker = set_up_mtl_workflow(worker)
    worker.append_to_path('output_dir', 'figure_5d_mtl_bbsr')
    worker.cv_workflow_type = "amusr"
    worker.cv_regression_type = ElasticNetByTaskRegressionWorkflow
    worker.cv_result_processor_type = ResultsProcessorMultiTask
    worker.seeds = list(range(52, 62))
    worker.target_expression_filter = "union"
    worker.regulator_expression_filter = "intersection"
    worker.run()
    del worker
