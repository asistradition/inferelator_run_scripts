from inferelator import utils

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
    ws.start_mpcontrol_dask(60)

    utils.Debug.vprint("Generating Fig 5D", level=0)
    # Figure 5D: STL
    worker = ws.set_up_fig5a()
    worker = ws.yeastract(worker)
    worker.cv_regression_type = "elasticnet"
    worker.append_to_path('output_dir', 'figure_5d_stl')
    worker.seeds = list(range(52, 62))
    worker.run()
    del worker