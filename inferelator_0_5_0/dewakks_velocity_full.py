from inferelator import crossvalidation_workflow
from inferelator import utils
from inferelator.distributed.inferelator_mp import MPControl
from inferelator.preprocessing import single_cell
from inferelator.workflow import inferelator_workflow
from inferelator.velocity_workflow import VelocityWorkflow
import os

utils.Debug.set_verbose_level(1)

DATA_FILE = "YPD_LOCAL_OPT_PV_DEXFORM.h5ad"

CONDA_ACTIVATE_PATH = '~/.local/anaconda3/bin/activate'
EXPRESSION_MATRIX_METADATA = ['Genotype', 'Genotype_Group', 'Replicate', 'Condition', 'tenXBarcode']

YEASTRACT_PRIOR = "YEASTRACT_20190713_BOTH.tsv"

TF_NAMES = "tf_names_gold_standard.txt"
YEASTRACT_TF_NAMES = "tf_names_yeastract.txt"

INPUT_DIR = '/mnt/ceph/users/cjackson/inferelator/data/yeast'
OUTPUT_PATH = '/mnt/ceph/users/cjackson/jackson_2019_inferelator_v050/'

if __name__ == '__main__':
    MPControl.set_multiprocess_engine("dask-cluster")
    MPControl.client.use_default_configuration("rusty_preempt")
    MPControl.client.set_job_size_params(n_jobs=1)
    MPControl.client.add_worker_conda("source ~/.local/anaconda3/bin/activate inferelator")
    MPControl.connect()

wkf = inferelator_workflow("stars", VelocityWorkflow)
wkf.set_file_paths(input_dir=INPUT_DIR,
                   output_dir=os.path.join(OUTPUT_PATH, "full_calculated_network"),
                   gold_standard_file='gold_standard.tsv',
                   priors_file=YEASTRACT_PRIOR,
                   tf_names_file=YEASTRACT_TF_NAMES)
wkf.set_expression_file(h5ad=DATA_FILE, h5_layer="smooth_count")
wkf.set_velocity_parameters(velocity_file_name=DATA_FILE, velocity_file_type="h5ad", velocity_file_layer="pv")
wkf.set_count_minimum(0.05)
wkf.add_preprocess_step("ftt")

wkf.run()
