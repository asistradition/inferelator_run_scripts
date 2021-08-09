from re import sub
from inferelator import utils
from inferelator import workflow
from inferelator import crossvalidation_workflow
from inferelator.postprocessing import MetricHandler
from inferelator.distributed.inferelator_mp import MPControl

import glob
import os
import csv
import pandas as pd
import tempfile
import time
import warnings 
import numpy as np

METHOD = "bbsr"

INPUT_DIR = '/scratch/cj59/beeline/BEELINE-data/inputs/Synthetic'
OUTPUT_PATH = '/scratch/cj59/beeline/BEELINE-results-' + METHOD

EXPR_FILE = "ExpressionData.csv"
GS_FILE = "refNetwork.csv"

CSV_HEAD = ["Run", "N_Samples", "N_Genes", "Prior", "Shuffle"]
CSV_HEAD.extend(MetricHandler.get_metric(workflow.WorkflowBase.metric).all_names())

MPControl.set_multiprocess_engine("local")
MPControl.connect()

utils.Debug.set_verbose_level(0)

td = tempfile.TemporaryDirectory()
os.makedirs(OUTPUT_PATH, exist_ok=True)

def reprocess_gs(gs_file, prefix, expr_file):

    gold_standard = pd.read_csv(gs_file, sep=",")
    expr = pd.read_csv(expr_file, index_col=0, sep=",")

    print("Generated gold standard for {n} ({x} edges)".format(n=prefix, x=gold_standard.shape[0]))

    gold_standard = gold_standard.pivot(index="Gene2", columns="Gene1")
    gold_standard[~pd.isna(gold_standard)] = 1.
    gold_standard = gold_standard.fillna(0).astype(int)
    gold_standard.columns = gold_standard.columns.droplevel(0)
    gold_standard = gold_standard.reindex(expr.index, axis=1).reindex(expr.index, axis=0).fillna(0).astype(int)

    out_gs = os.path.join(td.name, prefix + "gold_standard.tsv")
    gold_standard.to_csv(out_gs, sep="\t")
    out_tf = os.path.join(td.name, prefix + "tfs.txt")
    pd.DataFrame(expr.index.tolist()).to_csv(out_tf, index=False)

    return out_gs, out_tf


def setup_workflow(in_dir, gs_file, tf_file, out_dir):
        worker = workflow.inferelator_workflow(regression=METHOD, workflow="tfa")
        worker.set_file_paths(input_dir=in_dir, output_dir=out_dir, expression_matrix_file=EXPR_FILE,
                              gold_standard_file=gs_file, tf_names_file=tf_file)
        worker.set_file_properties(expression_matrix_columns_are_genes=False)
        worker.set_file_loading_arguments('expression_matrix_file', sep=",")
        worker.set_run_parameters(num_bootstraps=5)
        worker.set_output_file_names(nonzero_coefficient_file_name=None, pdf_curve_file_name=None,
                                     curve_data_file_name=None)

        return worker

def get_median_scores(wkf):
    cv = crossvalidation_workflow.CrossValidationManager(wkf)
    cv.add_gridsearch_parameter('random_seed', list(range(42, 52)))
    res = cv.run()
    medians = [np.median([result[1].all_scores[n] for result in res]) for n in res[0][1].all_names]
    print(dict(zip(res[0][1].all_names, medians)))
    return medians

project_paths = glob.glob(os.path.join(INPUT_DIR, "*"))
subproject_paths = {os.path.split(p)[1]: glob.glob(os.path.join(p, "*")) for p in project_paths}

warnings.simplefilter("ignore")
with open(os.path.join(OUTPUT_PATH, "BEELINE_SYNTHETIC.tsv"), mode="a", buffering=1) as csv_handle:
    _csv_writer = csv.writer(csv_handle, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_NONE)
    _csv_writer.writerow(CSV_HEAD)

    for i, pp in enumerate(subproject_paths.keys()):
        for j, sub_pp in enumerate(subproject_paths[pp]):

            k = i * len(project_paths) + j
            name = os.path.split(sub_pp)[1]

            out_dir = os.path.join(OUTPUT_PATH, pp, name)

            sub_pp_gs_reformatted, sub_pp_tfs = reprocess_gs(os.path.join(sub_pp, GS_FILE), name, os.path.join(sub_pp, EXPR_FILE))
            print("Inference for {n}".format(n=name))

            # Run without split or prior
            worker = setup_workflow(sub_pp, sub_pp_gs_reformatted, sub_pp_tfs, out_dir)
            worker.append_to_path('output_dir', "no_prior")

            worker.set_network_data_flags(use_no_prior=True)
            worker.set_run_parameters(random_seed=k)
            worker.get_data()

            _csv_writer.writerow([name, worker._num_obs, worker._num_genes, False, False] + get_median_scores(worker))

            del worker
            time.sleep(0.1)

            # Run with split
            worker = setup_workflow(sub_pp, sub_pp_gs_reformatted, sub_pp_tfs, out_dir)
            worker.append_to_path('output_dir', "prior")

            worker.set_file_paths(priors_file=sub_pp_gs_reformatted)
            worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True, cv_split_ratio=0.5)
            worker.set_run_parameters(random_seed=k)
            worker.get_data()

            _csv_writer.writerow([name, worker._num_obs, worker._num_genes, True, False] + get_median_scores(worker))

            del worker
            time.sleep(0.1)

            # Run with split + shuffle
            worker = setup_workflow(sub_pp, sub_pp_gs_reformatted, sub_pp_tfs, out_dir)
            worker.append_to_path('output_dir', "prior_shuffle")

            worker.set_file_paths(priors_file=sub_pp_gs_reformatted)
            worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True, cv_split_ratio=0.5)
            worker.set_shuffle_parameters(shuffle_prior_axis=-1)
            worker.set_run_parameters(random_seed=k)
            worker.get_data()

            _csv_writer.writerow([name, worker._num_obs, worker._num_genes, True, True] + get_median_scores(worker))

            del worker
            time.sleep(0.1)

            os.remove(sub_pp_gs_reformatted)
            os.remove(sub_pp_tfs)

