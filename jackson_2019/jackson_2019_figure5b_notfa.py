from inferelator import workflow

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
set_up_fig5b = ws.set_up_fig5b

if __name__ == '__main__':
    ws.start_mpcontrol_dask(40)

    # Figure 5B: No Priors
    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.set_tfa(tfa_driver=False)
    worker.append_to_path('output_dir', 'figure_5b_no_priors')

    set_up_fig5b(worker).run()
