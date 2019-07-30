from inferelator import utils
from inferelator.preprocessing import single_cell

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

if __name__ == '__main__':
    ws.start_mpcontrol_dask()

    utils.Debug.vprint("Generating Support Fig 5A", level=0)
    worker = ws.set_up_fig5a()
    worker.append_to_path('output_dir', '5a_no_norm')
    worker.run()
    del worker

    worker = ws.set_up_fig5a()
    worker.append_to_path('output_dir', '5a_log2')
    worker.add_preprocess_step(single_cell.log2_data)
    worker.run()
    del worker

    worker = ws.set_up_fig5a()
    worker.append_to_path('output_dir', '5a_umi_norm')
    worker.add_preprocess_step(single_cell.normalize_sizes_within_batch)
    worker.run()
    del worker

    worker = ws.set_up_fig5a()
    worker.append_to_path('output_dir', '5a_umi_norm_log2')
    worker.add_preprocess_step(single_cell.normalize_sizes_within_batch)
    worker.add_preprocess_step(single_cell.log2_data)
    worker.run()
    del worker

    worker = ws.set_up_fig5a()
    worker.append_to_path('output_dir', '5a_tf_sqrt')
    worker.add_preprocess_step(single_cell.tf_sqrt_data)
    worker.run()
    del worker
