from inferelator import utils
from inferelator import workflow
from inferelator import crossvalidation_workflow
from inferelator.distributed.inferelator_mp import MPControl

EXPRESSION_FILE = "MZ_2022_{sp}_EXPRESSION_DATA.h5ad"
MOTIF_PRIOR = "EGRIN_PRIOR_MOTIF_{sp}.tsv"
INFERRED_PRIOR = "EGRIN_PRIOR_INFERRED_{sp}.tsv"

INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/rice'
OUTPUT_PATH = '/mnt/ceph/users/cjackson/mz82_rice_2022'

OUTPUT_FOLDER = "{sp}_{pr}_{method}"

utils.Debug.set_verbose_level(1)

SPECIES_NAMES = {
    "OSI": "Oryza sativa indica",
    "OSJ": "Oryza sativa japonica",
    "OG": "Oryza glabarrima"
}


def set_up_workflow(wkf, prior_file, expression_file):
    wkf.set_file_paths(input_dir=INPUT_DIR,
                       output_dir=OUTPUT_PATH)

    wkf.set_file_paths(priors_file=prior_file, gold_standard_file=prior_file)
    wkf.set_expression_file(h5ad=expression_file)


    wkf.set_crossvalidation_parameters(split_gold_standard_for_crossvalidation=True,
                                       cv_split_ratio=0.2)
    wkf.set_run_parameters(num_bootstraps=5)
    wkf.drd_driver = None

def set_up_cv_seeds(wkf):
    cv = crossvalidation_workflow.CrossValidationManager(wkf)
    cv.add_gridsearch_parameter('random_seed', list(range(42, 52)))
    return cv


def set_up_dask(n_jobs=0):
    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.use_default_configuration("rusty_ccb", n_jobs=n_jobs)
    MPControl.client.add_worker_conda("source ~/.local/anaconda3/bin/activate inferelator")
    MPControl.client.add_slurm_command_line("--constraint=broadwell")
    MPControl.connect()

def set_up_multithreading():
    MPControl.set_multiprocess_engine("multiprocessing")
    MPControl.client.set_processes(38)
    MPControl.connect()

if __name__ == '__main__':
    set_up_multithreading()

    for sp in ["OSI", "OSJ", "OG"]:
        for pr in ["MOTIF", "INFERRED"]:
            expression_file = EXPRESSION_FILE.format(sp=sp)
            prior_file = MOTIF_PRIOR if pr == "MOTIF" else INFERRED_PRIOR
            prior_file = prior_file.format(sp=sp)

            for method in ["stars", "bbsr"]:

                print(f"Testing {pr} prior for {SPECIES_NAMES[sp]} ({method})")

                out_folder = OUTPUT_FOLDER.format(sp=sp, pr=pr, method=method)

                worker = workflow.inferelator_workflow(regression=method, workflow="tfa")
                set_up_workflow(worker, prior_file, expression_file)
                worker.append_to_path('output_dir', out_folder)

                cv_wrap = set_up_cv_seeds(worker)
                cv_wrap.run()

                del cv_wrap
                del worker

                worker = workflow.inferelator_workflow(regression=method, workflow="tfa")
                set_up_workflow(worker, prior_file, expression_file)
                worker.append_to_path('output_dir', out_folder + "_shuffle")
                worker.set_shuffle_parameters(shuffle_prior_axis=0)

                cv_wrap = set_up_cv_seeds(worker)
                cv_wrap.run()

                del cv_wrap
                del worker
