from inferelator import utils
from inferelator import workflow
from inferelator import crossvalidation_workflow

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

set_up_workflow = ws.set_up_workflow
yeastract = ws.yeastract

if __name__ == '__main__':
    ws.start_mpcontrol_dask(60)

    utils.Debug.vprint("Generating Fig 5D_BBSR", level=0)

    # Figure 5D: BBSR By Task Learning

    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr-by-task", workflow="multitask"))
    yeastract(worker)
    worker.append_to_path('output_dir', 'figure_5d_mtl_bbsr')

    cv_wrap = crossvalidation_workflow.CrossValidationManager(worker)
    cv_wrap.add_gridsearch_parameter('random_seed', list(range(52, 62)))
    cv_wrap.run()

    del cv_wrap
