from inferelator import utils

# Ugly hack for relative import from __main__ because fucking python, am I right?
import os

try:
    from inferelator_0_3_1 import jackson_2019_workflow_setup as ws
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
    ws.start_mpcontrol_dask(40)

    utils.Debug.vprint("Generating Fig 5A", level=0)
    # Figure 5A: Shuffled Priors
    worker = ws.set_up_fig5a(regression="elasticnet")
    worker.workflow.set_regression_parameters(l1_ratio=1, max_iter=2000, min_coef=0)
    worker.append_to_path('output_dir', 'figure_5a_shuffled')
    worker.workflow.set_shuffle_parameters(shuffle_prior_axis=0)
    worker.run()
    del worker

    # Figure 5A: Random Data
    worker = ws.set_up_fig5a(regression="elasticnet")
    worker.workflow.set_regression_parameters(l1_ratio=1, max_iter=2000, min_coef=0)
    worker.append_to_path('output_dir', 'figure_5a_neg_data')
    worker.workflow.wkf.set_file_paths(expression_matrix_file='110518_SS_NEG_Data.tsv.gz')
    worker.run()
    del worker

    # Figure 5A: No Imputation
    worker = ws.set_up_fig5a(regression="elasticnet")
    worker.workflow.set_regression_parameters(l1_ratio=1, max_iter=2000, min_coef=0)
    worker.append_to_path('output_dir', 'figure_5a_no_impute')
    worker.run()
    del worker

    # Figure 5A: MAGIC
    worker = ws.set_up_fig5a(regression="elasticnet")
    worker.workflow.set_regression_parameters(l1_ratio=1, max_iter=2000, min_coef=0)
    worker.append_to_path('output_dir', 'figure_5a_magic')
    worker.workflow.wkf.set_file_paths(expression_matrix_file='MAGIC_DATA.tsv.gz')
    worker.workflow.preprocessing_workflow = list()
    worker.workflow.count_minimum = None
    worker.run()
    del worker

    # Figure 5A: scImpute
    worker = ws.set_up_fig5a()
    worker.workflow.set_regression_parameters(l1_ratio=1, max_iter=2000, min_coef=0)
    worker.append_to_path('output_dir', 'figure_5a_scImpute')
    worker.workflow.wkf.set_file_paths(expression_matrix_file='SCIMPUTE_DATA.tsv.gz')
    worker.run()
    del worker

    # Figure 5A: VIPER
    worker = ws.set_up_fig5a(regression="elasticnet")
    worker.workflow.set_regression_parameters(l1_ratio=1, max_iter=2000, min_coef=0)
    worker.append_to_path('output_dir', 'figure_5a_VIPER')
    worker.workflow.wkf.set_file_paths(expression_matrix_file='VIPER_DATA.tsv.gz')
    worker.run()
    del worker
