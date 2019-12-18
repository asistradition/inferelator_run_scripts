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
yeastract = ws.yeastract

if __name__ == '__main__':
    ws.start_mpcontrol_dask(200)

    # Figure 6: Final Network

    worker = set_up_workflow(workflow.inferelator_workflow(regression="amusr", workflow="multitask"))
    yeastract(worker)
    worker.set_file_paths(gold_standard_file="YEASTRACT_Both_20181118.tsv")
    worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=False, cv_split_ratio=None)
    worker.set_run_parameters(num_bootstraps=50, random_seed=100)
    worker.append_to_path('output_dir', 'figure_6_final')

    final_network = worker.run()
    del worker
