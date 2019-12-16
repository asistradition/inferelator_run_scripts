from inferelator import utils
from inferelator import workflow, crossvalidation_workflow
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

if __name__ == '__main__':
    ws.start_mpcontrol_dask(100)

    utils.Debug.vprint("Generating Fig 5D_AMuSR", level=0)

    # Figure 5D: MTL

    worker = workflow.inferelator_workflow(regression="amusr", workflow="amusr")
    worker.set_file_paths(input_dir=ws.INPUT_DIR,
                          output_dir=ws.OUTPUT_PATH,
                          gold_standard_file="gold_standard.tsv",
                          gene_metadata_file="orfs.tsv",
                          priors_file=ws.YEASTRACT_PRIOR,
                          tf_names_file=ws.YEASTRACT_TF_NAMES)
    worker.set_file_properties(gene_list_index="SystematicName")
    worker.set_task_filters(target_expression_filter="union", regulator_expression_filter="intersection")
    worker.set_run_parameters(num_bootstraps=5)
    worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True, cv_split_ratio=0.2)

    worker.append_to_path('output_dir', "fig5d_mtl_amusr")

    # Jackson single cell task
    task = worker.create_task(task_name="Jackson_2019",
                              expression_matrix_file="103118_SS_Data.tsv.gz",
                              expression_matrix_columns_are_genes=True,
                              extract_metadata_from_expression_matrix=True,
                              expression_matrix_metadata= ws.EXPRESSION_MATRIX_METADATA,
                              workflow_type="single-cell",
                              count_minimum=0.05,
                              tasks_from_metadata=True,
                              meta_data_task_column="Condition")

    task.add_preprocess_step(single_cell.log2_data)
    cv_wrap = crossvalidation_workflow.CrossValidationManager(worker)
    cv_wrap.add_gridsearch_parameter('random_seed', list(range(52, 62)))
    cv_wrap.run()
