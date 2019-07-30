from inferelator.postprocessing.results_processor_mtl import ResultsProcessorMultiTask
from inferelator.regression.bbsr_multitask import BBSRByTaskRegressionWorkflow

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

    # Figure 5D: MTL
    worker = ws.set_up_fig5a()
    worker.append_to_path('output_dir', 'figure_5d_multiple_stl')
    worker.priors_file = "YEASTRACT_Both_20181118.tsv"
    worker.cv_workflow_type = "amusr"
    worker.cv_regression_type = BBSRByTaskRegressionWorkflow
    worker.cv_result_processor_type = ResultsProcessorMultiTask
    worker.seeds = list(range(52, 62))
    worker.task_expression_filter = "intersection"
    worker.run()
    del worker
