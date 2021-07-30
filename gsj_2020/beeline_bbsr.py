from re import sub
from inferelator import utils
from inferelator import workflow
from inferelator import crossvalidation_workflow
from inferelator.preprocessing import single_cell
from inferelator.postprocessing import MetricHandler
from inferelator.distributed.inferelator_mp import MPControl

import glob
import os
import csv
import pandas as pd
import tempfile
import time
import warnings 

METHOD = "bbsr"

INPUT_DIR = '/home/chris/PycharmProjects/Beeline/BEELINE-data/inputs/Synthetic'
OUTPUT_PATH = '/home/chris/PycharmProjects/Beeline/BEELINE-results-' + METHOD

EXPR_FILE = "ExpressionData.csv"
GS_FILE = "refNetwork.csv"

CSV_HEAD = ["Run", "N_Samples", "N_Genes", "Prior", "Shuffle"]
CSV_HEAD.extend(MetricHandler.get_metric(workflow.WorkflowBase.metric).all_names())

MPControl.set_multiprocess_engine("local")
MPControl.connect()

utils.Debug.set_verbose_level(0)

td = tempfile.TemporaryDirectory()
os.makedirs(OUTPUT_PATH, exist_ok=True)

def reprocess_gs(gs_file, prefix):

    gold_standard = pd.read_csv(gs_file, sep=",")

    print("Generated gold standard for {n} ({x} edges)".format(n=prefix, x=gold_standard.shape[0]))

    gold_standard = gold_standard.pivot(index="Gene2", columns="Gene1")
    gold_standard[~pd.isna(gold_standard)] = 1.
    gold_standard = gold_standard.fillna(0).astype(int)
    gold_standard.columns = gold_standard.columns.droplevel(0)

    out_gs = os.path.join(td.name, prefix + "gold_standard.tsv")
    gold_standard.to_csv(out_gs, sep="\t")
    out_tf = os.path.join(td.name, prefix + "tfs.txt")
    pd.DataFrame(gold_standard.columns.tolist()).to_csv(out_tf, index=False)

    return out_gs, out_tf


def setup_workflow(in_dir, gs_file, tf_file, out_dir):
        worker = workflow.inferelator_workflow(regression=METHOD, workflow="tfa")
        worker.set_file_paths(input_dir=in_dir, output_dir=out_dir, expression_matrix_file=EXPR_FILE,
                              gold_standard_file=gs_file, tf_names_file=tf_file)
        worker.set_file_properties(expression_matrix_columns_are_genes=False)
        worker.set_file_loading_arguments('expression_matrix_file', sep=",")

        return worker

project_paths = glob.glob(os.path.join(INPUT_DIR, "*"))
subproject_paths = {os.path.split(p)[1]: glob.glob(os.path.join(p, "*")) for p in project_paths}

warnings.simplefilter("ignore")
with open(os.path.join(OUTPUT_PATH, "BEELINE_SYNTHETIC.tsv"), mode="w", buffering=1) as csv_handle:
    _csv_writer = csv.writer(csv_handle, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_NONE)
    _csv_writer.writerow(CSV_HEAD)

    for i, pp in enumerate(subproject_paths.keys()):
        for j, sub_pp in enumerate(subproject_paths[pp]):

            k = i * len(project_paths) + j
            name = os.path.split(sub_pp)[1]

            out_dir = os.path.join(OUTPUT_PATH, pp, name)

            sub_pp_gs_reformatted, sub_pp_tfs = reprocess_gs(os.path.join(sub_pp, GS_FILE), name)
            print("Inference for {n}".format(n=name))

            # Run without split or prior
            worker = setup_workflow(sub_pp, sub_pp_gs_reformatted, sub_pp_tfs, out_dir)
            worker.set_network_data_flags(use_no_prior=True)
            worker.set_run_parameters(random_seed=k)
            result = worker.run()
            print(worker.priors_data)

            _csv_writer.writerow([name, worker._num_obs, worker._num_genes, False, False] + [result.all_scores[n] for n in result.all_names])
            time.sleep(0.1)

            # Run with split
            worker = setup_workflow(sub_pp, sub_pp_gs_reformatted, sub_pp_tfs, out_dir)
            worker.set_file_paths(priors_file=sub_pp_gs_reformatted)
            worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True, cv_split_ratio=0.5)
            worker.set_run_parameters(random_seed=k)

            result = worker.run()
            _csv_writer.writerow([name, worker._num_obs, worker._num_genes, True, False] + [result.all_scores[n] for n in result.all_names])

            del worker
            del result
            time.sleep(0.1)

            # Run with split + shuffle
            worker = setup_workflow(sub_pp, sub_pp_gs_reformatted, sub_pp_tfs, out_dir)
            worker.set_file_paths(priors_file=sub_pp_gs_reformatted)
            worker.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True, cv_split_ratio=0.5)
            worker.set_shuffle_parameters(shuffle_prior_axis=0)
            worker.set_run_parameters(random_seed=k)

            result = worker.run()
            print(worker.priors_data)
            print(result.betas)

            _csv_writer.writerow([name, worker._num_obs, worker._num_genes, True, True] + [result.all_scores[n] for n in result.all_names])
            time.sleep(0.1)

            os.remove(sub_pp_gs_reformatted)
            os.remove(sub_pp_tfs)

