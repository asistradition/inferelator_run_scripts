from inferelator import utils
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
set_up_fig5a = ws.set_up_fig5a


if __name__ == '__main__':
    ws.start_mpcontrol_dask(60)

    utils.Debug.vprint("Generating Fig 5A", level=0)

    # Figure 5A: No Imputation
    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.append_to_path('output_dir', 'figure_5a_no_impute')

    set_up_fig5a(worker).run()

    # Figure 5A: Shuffled Priors
    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.set_shuffle_parameters(shuffle_prior_axis=0)
    worker.append_to_path('output_dir', 'figure_5a_shuffled')

    set_up_fig5a(worker).run()

    # Figure 5A: Random Data
    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.set_file_paths(expression_matrix_file='110518_SS_NEG_Data.tsv.gz')
    worker.append_to_path('output_dir', 'figure_5a_neg_data')

    set_up_fig5a(worker).run()

    # Figure 5A: MAGIC
    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.set_file_paths(expression_matrix_file='MAGIC_DATA.tsv.gz')
    worker.preprocessing_workflow = list()
    worker.append_to_path('output_dir', 'figure_5a_magic')

    set_up_fig5a(worker).run()

    # Figure 5A: scImpute
    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.set_file_paths(expression_matrix_file='SCIMPUTE_DATA.tsv.gz')
    worker.append_to_path('output_dir', 'figure_5a_scImpute')

    set_up_fig5a(worker).run()

    # Figure 5A: VIPER
    worker = set_up_workflow(workflow.inferelator_workflow(regression="bbsr", workflow="single-cell"))
    worker.set_file_paths(expression_matrix_file='VIPER_DATA.tsv.gz')
    worker.append_to_path('output_dir', 'figure_5a_VIPER')

    set_up_fig5a(worker).run()
