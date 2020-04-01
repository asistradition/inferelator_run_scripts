from inferelator import utils
from inferelator import workflow

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
    ws.start_mpcontrol_dask(60)

    utils.Debug.vprint("Generating Fig 5A", level=0)

    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.set_file_paths(output_dir='/mnt/ceph/users/cjackson/inferelator_dewax')
    worker.set_expression_file(h5ad="Jackson2019_pipeline_computed_all_distance_euclidean.h5ad")
    worker.append_to_path('output_dir', 'dewaxed')
    worker.preprocessing_workflow = list()
    worker.set_regression_parameters(ordinary_least_squares_only=True)

    set_up_fig5a(worker).run()

    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.set_file_paths(output_dir='/mnt/ceph/users/cjackson/inferelator_dewax')
    worker.append_to_path('output_dir', 'no_impute')
    worker.set_regression_parameters(ordinary_least_squares_only=True)

    set_up_fig5a(worker).run()

    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.set_file_paths(output_dir='/mnt/ceph/users/cjackson/inferelator_dewax')
    worker.set_expression_file(h5ad="Jackson2019_pipeline_computed_all_distance_euclidean.h5ad")
    worker.append_to_path('output_dir', 'dewaxed_yeastract')
    worker.preprocessing_workflow = list()
    worker.set_regression_parameters(ordinary_least_squares_only=True)
    yeastract(worker)

    set_up_fig5a(worker).run()

    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.set_file_paths(output_dir='/mnt/ceph/users/cjackson/inferelator_dewax')
    worker.set_expression_file(h5ad="Jackson2019_pipeline_computed_all_distance_euclidean.h5ad")
    worker.set_shuffle_parameters(shuffle_prior_axis=0)
    worker.preprocessing_workflow = list()
    worker.append_to_path('output_dir', 'shuffle')
    worker.set_regression_parameters(ordinary_least_squares_only=True)

    set_up_fig5a(worker).run()

