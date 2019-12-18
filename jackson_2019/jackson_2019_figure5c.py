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

if __name__ == '__main__':
    ws.start_mpcontrol_dask(40)

    # Figure 5C: Condition Specific

    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.append_to_path('output_dir', 'figure_5c_conditions')

    cv_wrap = crossvalidation_workflow.CrossValidationManager(worker)
    cv_wrap.add_gridsearch_parameter('random_seed', list(range(42, 52)))
    cv_wrap.add_grouping_dropin("Condition", group_size=500)

    cv_wrap.run()
    del cv_wrap
