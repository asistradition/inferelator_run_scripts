from inferelator import utils
from inferelator import workflow
from inferelator.preprocessing import single_cell

# Ugly hack for relative import from __main__ because fucking python, am I right?
import os

try:
    from . import yeast_workflow_setup as ws
except ValueError:
    # Py2
    import imp

    (f, p, d) = imp.find_module("yeast_workflow_setup",
                                [os.path.join(os.path.dirname(os.path.realpath(__file__)))])
    ws = imp.load_module("ws", f, p, d)
except ImportError:
    # Py3
    import importlib.machinery

    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "yeast_workflow_setup.py")
    ws = importlib.machinery.SourceFileLoader("ws", filename).load_module()


set_up_workflow = ws.set_up_workflow
set_up_fig5a = ws.set_up_fig5a
yeastract = ws.yeastract

if __name__ == '__main__':
    ws.start_mpcontrol_dask(100)

    # Figure 6: Final Network

    worker = set_up_workflow(workflow.inferelator_workflow(regression="amusr", workflow="multitask"))
    yeastract(worker)
    worker.preprocessing_workflow = list()
    worker.set_file_paths(gold_standard_file="YEASTRACT_Both_20181118.tsv")
    worker.set_file_paths(output_dir='/mnt/ceph/users/cjackson/inferelator_full_build')
    worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=False, cv_split_ratio=None)
    worker.set_task_filters(target_expression_filter="union", regulator_expression_filter="intersection")
    worker.set_run_parameters(num_bootstraps=25, random_seed=100)
    worker.append_to_path('output_dir', 'dewakks')

    # Jackson single cell task
    task = worker.create_task(task_name="Jackson_2019",
                              workflow_type="single-cell",
                              count_minimum=0.05,
                              tasks_from_metadata=True,
                              meta_data_task_column="Condition")
    task.set_expression_file(h5ad="Jackson2019_pipeline_computed_all_distance_euclidean.h5ad")

    worker.run()
    del worker

    # Figure 6: Final Network

    worker = set_up_workflow(workflow.inferelator_workflow(regression="amusr", workflow="multitask"))
    yeastract(worker)
    worker.set_file_paths(gold_standard_file="YEASTRACT_Both_20181118.tsv")
    worker.set_file_paths(output_dir='/mnt/ceph/users/cjackson/inferelator_full_build')
    worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=False, cv_split_ratio=None)
    worker.set_task_filters(target_expression_filter="union", regulator_expression_filter="intersection")
    worker.set_run_parameters(num_bootstraps=25, random_seed=100)
    worker.append_to_path('output_dir', 'counts')

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
