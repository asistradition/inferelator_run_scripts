from inferelator import single_cell_cv_workflow
from inferelator import utils
from inferelator import workflow
from inferelator.postprocessing.results_processor_mtl import ResultsProcessorMultiTask

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

FIG_5A = True
FIG_5B = True
FIG_5C = True
FIG_5D = True
FIG_6 = True

N_CORES = 200

if __name__ == '__main__':
    ws.start_mpcontrol_dask(N_CORES)

    if FIG_5A:
        utils.Debug.vprint("Generating Fig 5A", level=0)
        # Figure 5A: Shuffled Priors
        worker = ws.set_up_fig5a()
        worker.append_to_path('output_dir', 'figure_5a_shuffled')
        worker.shuffle_prior_axis = 0
        worker.run()
        del worker

    if FIG_5A:
        # Figure 5A: Random Data
        worker = ws.set_up_fig5a()
        worker.append_to_path('output_dir', 'figure_5a_neg_data')
        worker.expression_matrix_file = '110518_SS_NEG_Data.tsv.gz'
        worker.run()
        del worker

    if FIG_5A:
        # Figure 5A: No Imputation
        worker = ws.set_up_fig5a()
        worker.append_to_path('output_dir', 'figure_5a_no_impute')
        worker.run()
        del worker

    if FIG_5A:
        # Figure 5A: MAGIC
        worker = ws.set_up_fig5a()
        worker.append_to_path('output_dir', 'figure_5a_magic')
        worker.expression_matrix_file = 'MAGIC_DATA.tsv.gz'
        worker.preprocessing_workflow = list()
        worker.run()
        del worker

    if FIG_5A:
        # Figure 5A: scImpute
        worker = ws.set_up_fig5a()
        worker.append_to_path('output_dir', 'figure_5a_scImpute')
        worker.expression_matrix_file = 'SCIMPUTE_DATA.tsv.gz'
        worker.run()
        del worker

    if FIG_5A:
        # Figure 5A: VIPER
        worker = ws.set_up_fig5a()
        worker.append_to_path('output_dir', 'figure_5a_VIPER')
        worker.expression_matrix_file = 'VIPER_DATA.tsv.gz'
        worker.run()
        del worker

    if FIG_5B:
        utils.Debug.vprint("Generating Fig 5B", level=0)
        # Figure 5B: Gold Standard
        worker = ws.set_up_fig5b()
        worker.append_to_path('output_dir', 'figure_5b_gold_standard_cv')
        worker.run()
        del worker

    if FIG_5B:
        # Figure 5B: YEASTRACT
        worker = ws.set_up_fig5b()
        worker.append_to_path('output_dir', 'figure_5b_yeastract')
        worker.priors_file = "YEASTRACT_Both_20181118.tsv"
        worker.gold_standard_file = "gold_standard.tsv"
        worker.run()
        del worker

    if FIG_5B:
        # Figure 5B: ATAC-Seq
        worker = ws.set_up_fig5b()
        worker.append_to_path('output_dir', 'figure_5b_atac')
        worker.priors_file = "yeast-motif-prior.tsv"
        worker.gold_standard_file = "gold_standard.tsv"
        worker.run()
        del worker

    if FIG_5B:
        # Figure 5B: Bussemaker
        worker = ws.set_up_fig5b()
        worker.append_to_path('output_dir', 'figure_5b_bussemaker')
        worker.priors_file = "Bussemaker_pSAM_priors.tsv"
        worker.gold_standard_file = "gold_standard.tsv"
        worker.run()
        del worker

    if FIG_5B:
        # Figure 5B: No Priors
        worker = ws.set_up_fig5b()
        worker.append_to_path('output_dir', 'figure_5b_no_priors')
        from inferelator.preprocessing.tfa import NoTFA

        worker.tfa_driver = NoTFA
        worker.run()
        del worker

    if FIG_5C:
        utils.Debug.vprint("Generating Fig 5C", level=0)
        # Figure 5C: Condition Networks
        worker = ws.set_up_workflow(single_cell_cv_workflow.SingleCellDropoutConditionSampling())
        worker.append_to_path('output_dir', 'figure_5c_conditions')
        worker.sample_batches_to_size = 500
        worker.drop_column = "Condition"
        worker.model_dropouts = False
        worker.seeds = list(range(42, 52))
        worker.run()
        del worker

    if FIG_5D:
        utils.Debug.vprint("Generating Fig 5D", level=0)
        # Figure 5D: STL
        worker = ws.set_up_fig5a()
        worker.append_to_path('output_dir', 'figure_5d_stl')
        worker.priors_file = "YEASTRACT_Both_20181118.tsv"
        worker.seeds = list(range(52, 62))
        worker.run()
        del worker

    if FIG_5D:
        # Figure 5D: MTL
        worker = ws.set_up_fig5a()
        worker.append_to_path('output_dir', 'figure_5d_mtl')
        worker.priors_file = "YEASTRACT_Both_20181118.tsv"
        worker.cv_workflow_type = "amusr"
        worker.cv_regression_type = "amusr"
        worker.cv_result_processor_type = ResultsProcessorMultiTask
        worker.seeds = list(range(52, 62))
        worker.task_expression_filter = "intersection"
        worker.run()
        del worker

    if FIG_6:
        utils.Debug.vprint("Generating Fig 6", level=0)
        # Figure 6: Final Network
        worker = ws.set_up_workflow(workflow.inferelator_workflow(regression="amusr", workflow="amusr"))
        worker.append_to_path('output_dir', 'figure_6_final')
        worker.priors_file = "YEASTRACT_Both_20181118.tsv"
        worker.gold_standard_file = "YEASTRACT_Both_20181118.tsv"
        worker.split_gold_standard_for_crossvalidation = False
        worker.split_priors_for_gold_standard = False
        worker.cv_split_ratio = None
        worker.num_bootstraps = 50
        worker.random_seed = 100
        worker.task_expression_filter = "intersection"
        worker.run()
        del worker
