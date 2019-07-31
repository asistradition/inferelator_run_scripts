from inferelator import utils
from inferelator.postprocessing.results_processor_mtl import ResultsProcessorMultiTask
from inferelator.regression.bbsr_multitask import BBSRByTaskRegressionWorkflow
from inferelator.regression.elasticnet_multitask import ElasticNetByTaskRegressionWorkflow

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

    utils.Debug.vprint("Generating Fig 5D", level=0)
    # Figure 5D: STL
    worker = ws.set_up_fig5a()
    worker.append_to_path('output_dir', 'figure_5d_stl')
    worker.priors_file = ws.YEASTRACT_PRIOR
    worker.seeds = list(range(52, 62))
    worker.run()
    del worker

    # Figure 5D: MTL
    worker = ws.set_up_fig5a()
    worker.append_to_path('output_dir', 'figure_5d_amusr_mtl')
    worker.priors_file = ws.YEASTRACT_PRIOR
    worker.cv_workflow_type = "amusr"
    worker.cv_regression_type = "amusr"
    worker.cv_result_processor_type = ResultsProcessorMultiTask
    worker.seeds = list(range(52, 62))
    worker.task_expression_filter = "intersection"
    worker.run()
    del worker

    # Figure 5D: MTL-BBSR
    # worker = ws.set_up_fig5a()
    # worker.append_to_path('output_dir', 'figure_5d_bbsr_mtl')
    # worker.priors_file = ws.YEASTRACT_PRIOR
    # worker.cv_workflow_type = "amusr"
    # worker.cv_regression_type = BBSRByTaskRegressionWorkflow
    # worker.cv_result_processor_type = ResultsProcessorMultiTask
    # worker.seeds = list(range(52, 62))
    # worker.task_expression_filter = "intersection"
    # worker.run()
    # del worker
