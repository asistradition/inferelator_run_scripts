from inferelator import workflow
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

    # Figure 6: Final Network
    worker = ws.set_up_workflow(workflow.inferelator_workflow(regression=BBSRByTaskRegressionWorkflow, workflow="amusr"))
    worker.append_to_path('output_dir', 'support_bbsr_fig6')
    worker.priors_file = "YEASTRACT_Both_20181118.tsv"
    worker.gold_standard_file = "YEASTRACT_Both_20181118.tsv"
    worker.split_gold_standard_for_crossvalidation = False
    worker.split_priors_for_gold_standard = False
    worker.cv_split_ratio = None
    worker.num_bootstraps = 50
    worker.random_seed = 100
    worker.run()
