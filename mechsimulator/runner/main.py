import os
from typing import List

from mechsimulator import parser
from mechsimulator import plotter

from mechsimulator.parser.exp_checker import ALLOWED_SIM_OPTS
from mechsimulator.parser.exp_checker import get_poss_inps

JOB_PATH = '../lib/jobs'
EXP_PATH = '../lib/exps'
MECH_PATH = '../lib/mechs'
SPC_PATH = '../lib/mechs'
OUT_PATH = '../lib/results'

def _mech_opts_lst(exp_set, gases, kwarg_dct) -> List[dict]:
    """ Creates a list of mech_opts, one for each mechanism

        Note: the reason only a single exp_set is required is that the intention
        of this option is to run comparisons against a single set (e.g.,
        trying several values of dP/dt for a single exp_set). There is no way to
        vary some parameter in different ways for different experimental sets.
        However, options can still be used for multiple sets (e.g., mech_names
        for simulating multiple sets)

        :param kwarg_dct:
        :return:
    """

    # Only fill in mech_opts_lst if any kwargs were given
    if kwarg_dct != {}:
        # Initialize
        nmechs = len(gases)

        # populate mech_opts_lst with empty dics
        mech_opts_lst = [{} for _ in range(nmechs)]

        # Get the possible inputs for this reac/meas combination
        meas_type = exp_set['overall']['meas_type']
        reac_type = exp_set['overall']['reac_type']
        poss_inps = get_poss_inps(reac_type, meas_type, 'exps', rm_bad=True)
        # Loop over each keyword argument
        ok_names = tuple(ALLOWED_SIM_OPTS.keys()) + poss_inps + ('mech_names',)
        for inp_idx, (name, vals) in enumerate(kwarg_dct.items()):
            assert name in ok_names, (
                f"Input '{name}' not allowed for reactor '{reac_type}' and "
                f"measurement '{meas_type}'. Options are {ok_names}")
            assert isinstance(vals, (list, tuple)), (
                f"kwarg '{name}' should be list or tuple, not {type(vals)}")
            # Check the list length
            assert len(vals) == nmechs, (
                f'Entries in kwarg_dct, {kwarg_dct}, should all be the length '
                f'of the number of mechanisms, {nmechs}')

            # Add each value for the kwarg to each mech_opts dict
            for mech_idx, val in enumerate(vals):
                mech_opts_lst[mech_idx][name] = val
    # If no kwargs, return None
    else:
        mech_opts_lst = None

    return mech_opts_lst


def check_inputs(job_dct, exp_sets):
    """ Check a few things on the input job parameters/exp_sets

        :param job_dct: dictionary describing the job
        :type job_dct: dict
        :param exp_sets: list of experiment objects
        :type exp_sets: list
    """

    # If there are zero experiments in a set (i.e., only the 'plot' field has
    # information), then check that the conds_src is not 'exps'
    for set_idx, exp_set in enumerate(exp_sets):
        nexps = exp_set['overall']['num_exps']
        cond_src = job_dct['cond_srcs'][set_idx]
        if nexps == 0:
            assert cond_src != 'exps', ("With zero experiments in the set, the"
                                        " condition source cannot be 'exps'")

def run_jobs(job_files, job_path=None):
    """ Runs multiple jobs

        :param job_files: list of job file names
        :type job_files: list [str]
        :param job_path: path where job files are located
        :type job_path: str
    """

    for job_file in job_files:
        run_job(job_file, job_path=job_path)


def run_job(job_file, job_path=None):
    """ Runs a single job

        :param job_file: job file name
        :type job_file: str
        :param job_path: path where job file is located
        :type job_path: str
    """

    job_path = job_path or JOB_PATH
    # CLEAN UP - too many calls
    # job_dct = parser.main.single_file(job_path, job_file, 'job')
    filename = os.path.join(job_path, job_file)
    job_dct = parser.job.load_job(filename)
    # END CLEANUP
    job_type = job_dct['job_type']

    # Not sure how other job types will work...
    if job_type == 'plot':
        # Get filenames and other info from the job_dct
        exp_filenames = job_dct['exp_filenames']
        mech_filenames = job_dct['mech_filenames']
        spc_filenames = job_dct['spc_filenames']
        calc_types = job_dct['calc_types']
        x_srcs = job_dct['x_srcs']
        cond_srcs = job_dct['cond_srcs']
        # Load objects using the filenames
        exp_sets = [ parser.exp.load_exp_set(os.path.join(EXP_PATH, filename)) for filename in exp_filenames ] #parser.main.mult_exp_files(EXP_PATH, exp_filenames)
        gases = [ parser.mech.load_solution_obj(os.path.join(MECH_PATH, filename)) for filename in mech_filenames ] #parser.main.mult_mech_files(MECH_PATH, mech_filenames)
        mech_spc_dcts = [ parser.spc.load_mech_spc_dct(os.path.join(MECH_PATH, filename)) for filename in spc_filenames ] #parser.main.mult_files(SPC_PATH, spc_filenames, 'spc')
        check_inputs(job_dct, exp_sets)  # run some checks

        # Load the mech_opts_lst
        mech_opts_lst = _mech_opts_lst(exp_sets[0], gases, job_dct['kwarg_dct'])
        # TODO! Move below into calling function

        # Run the plotter code
        figs_axes = plotter.main.mult_sets(exp_sets, gases, mech_spc_dcts,
                                           calc_types, x_srcs, cond_srcs,
                                           mech_opts_lst=mech_opts_lst)
        plotter.util.build_pdf(figs_axes)
    else:
        raise NotImplementedError(f"job_type {job_type}")
