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
    worker.set_file_paths(output_dir='/mnt/ceph/users/cjackson/inferelator_srr')
    worker.append_to_path('output_dir', 'gold_standard')
    worker.set_regression_parameters(ordinary_least_squares_only=True)

    set_up_fig5a(worker).run()

    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.set_file_paths(tf_names_file="Scer_cisbp_TFs.txt", priors_file="Scer_ATAC_binary_prior.tsv",
                          output_dir='/mnt/ceph/users/cjackson/inferelator_srr')
    worker.append_to_path('output_dir', 'srrtomato')
    worker.set_regression_parameters(ordinary_least_squares_only=True)

    set_up_fig5a(worker).run()

    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.set_file_paths(tf_names_file="Scer_cisbp_TFs.txt", priors_file="Scer_ATAC_binary_prior.tsv",
                          output_dir='/mnt/ceph/users/cjackson/inferelator_srr')
    worker.set_shuffle_parameters(shuffle_prior_axis=0)
    worker.append_to_path('output_dir', 'shuffle')
    worker.set_regression_parameters(ordinary_least_squares_only=True)

    set_up_fig5a(worker).run()

    # Figure 5A: Random Data
    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.set_file_paths(expression_matrix_file='110518_SS_NEG_Data.tsv.gz',
                          output_dir='/mnt/ceph/users/cjackson/inferelator_srr')
    worker.append_to_path('output_dir', 'noise')
    worker.set_regression_parameters(ordinary_least_squares_only=True)

    set_up_fig5a(worker).run()
