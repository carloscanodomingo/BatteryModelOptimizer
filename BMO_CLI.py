#!/usr/bin/env python3
import logging
import multiprocessing
import os
import queue
import signal
import sys
import traceback
from multiprocessing import Process, Queue

import click
import pybamm
from click_command import click_config
from core import ModelParameters
from core.Parameters.DegradationParameters import DegradationParameters
from core.Parameters.NonDegradationParameters import NonDegradationParameters
from core.PyBammWrapper import PyBammWrapper
from core.utils import *
from databases.DatasetEV import BatteryIDEV

MAX_VALUE = "Inf"
MAX_TIMEOUT_NO_DEGRADATION = 60 * 60
MAX_TIMEOUT_DEGRADATION = 60 * 60 * 5
MAX_TIMEOUT = MAX_TIMEOUT_NO_DEGRADATION


class suppress_output_context:
    def __init__(self, verbose):
        self.verbose = verbose
        self.original_stdout_fd = sys.stdout.fileno()
        self.original_stderr_fd = sys.stderr.fileno()
        self.original_stdout = None
        self.original_stderr = None
        self.suppressed = False

    def __enter__(self):
        if not self.verbose:
            # Suppress output
            self.original_stdout = os.dup(self.original_stdout_fd)
            self.original_stderr = os.dup(self.original_stderr_fd)
            with open(os.devnull, "wb") as nullfile:
                null_fd = nullfile.fileno()
                os.dup2(null_fd, self.original_stdout_fd)
                os.dup2(null_fd, self.original_stderr_fd)
            self.suppressed = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.suppressed:
            # Restore the original stdout and stderr
            os.dup2(self.original_stdout, self.original_stdout_fd)
            os.dup2(self.original_stderr, self.original_stderr_fd)
            os.close(self.original_stdout)
            os.close(self.original_stderr)
            self.suppressed = False


def force_print_result(value):
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    result = f"{value}"
    print(result)


@click_config  # Apply the imported decorator
def create_and_run_pybamm_simulation(**kwargs):
    """
    Creates the PyBaMM model based on provided parameters and runs the simulation.

    Parameters:
    - kwargs: Dictionary of arguments required for the simulation setup and execution.
    """
    # Setup environment and logging
    # Construct paths and setup parameters
    (
        common_folder_path,
        parameter_file_path,
        result_path,
        state_path,
        log_path,
    ) = setup_paths(kwargs)
    verbose = kwargs.get("verbose")
    log_to_file = kwargs.get("log_to_file")
    setup_logging(log_path, log_to_file, verbose)
    id_configuration = kwargs.get("id_configuration")
    instance_id = kwargs.get("id_instance")
    battery_id = kwargs.get("battery_id")

    n_cycle = kwargs.get("n_cycle")
    logging.info(
        (
            f"START Pybamm run Conf ID {id_configuration} -",
            f"Threads: {len(os.sched_getaffinity(0))}",
            f",Instance {instance_id}, cycle {n_cycle} - Battery {battery_id}",
        )
    )
    cycle = kwargs.get("n_cycle")
    if cycle is None:
        logging.info("N_cycles has not been defined")
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        result = f"{MAX_VALUE}"
        print(result)
        sys.exit(0)
    result = True
    with suppress_output_context(verbose=verbose):
        try:
            setup_environment(kwargs)
            model_parameters, pybamm_wrapper = initialize_pybamm_wrapper(
                parameter_file_path, result_path, state_path, kwargs
            )
            if model_parameters.degradation_parameters is None:
                MAX_TIMEOUT = MAX_TIMEOUT_NO_DEGRADATION
            else:
                MAX_TIMEOUT = MAX_TIMEOUT_DEGRADATION
        except Exception as e:
            logging.error(f"An error occurred during the Initialization: {e}")
            result = False
    if not result:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        result = f"{MAX_VALUE}"
        print(result)
        sys.exit(0)
    init_queue = Queue()
    init_program = Process(
        target=init_pybamm_with_timeout,
        args=(pybamm_wrapper, init_queue),
    )
    init_program.start()
    try:
        logging.info(f"Starting init process")

        result = init_queue.get(timeout=MAX_TIMEOUT)
    except queue.Empty:
        logging.info(f"Init TimeOut Expired seconds: {MAX_TIMEOUT}")
        init_queue.close()
        init_program.terminate()
        del init_program
        result = None
    except Exception as e:
        logging.error(f"An error occurred during the Initialization PyBaMM simulation: {e}")
        result = None

    if result is None:
        logging.error(f"An error occurred during the Initialization object")
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        result = f"{MAX_VALUE}"
        print(result)
        sys.exit(0)
    else:
        pybamm_wrapper.state = result

    # Run PyBaMM simulation
    last_cycle_simulated = pybamm_wrapper.__len_metrics__() - 1
    if last_cycle_simulated >= cycle:
        cycles_to_simulate = [cycle]
    else:
        cycles_to_simulate = range(last_cycle_simulated + 1, cycle + 1)
    result = None
    logging.info(f"Cycles to simulated: {list(cycles_to_simulate)}")
    for current_cycle in cycles_to_simulate:
        pybamm_wrapper.update_state()
        last_cycle_simulated = pybamm_wrapper.__len_metrics__() - 1
        logging.info(
            f"Requested cycle: {cycle} Starting simulation of cycle {current_cycle} -  cicles simulated {last_cycle_simulated}"
        )
        logging.info(f"Starting simulation of cycle {current_cycle}")
        process_queue = Queue()
        program = Process(
            target=run_pybamm_with_timeout,
            args=(pybamm_wrapper, current_cycle, process_queue, verbose),
        )
        program.start()
        try:
            result = process_queue.get(timeout=MAX_TIMEOUT)
        except queue.Empty:
            logging.info(f"TimeOut Expired seconds: {MAX_TIMEOUT}")
            process_queue.close()
            program.terminate()
            del process_queue
            result = None
            break
        except Exception as e:
            logging.error(f"An error occurred during the PyBaMM simulation: {e}")
            result = None
            break

        program.join(timeout=1)
        if program.is_alive():
            program.terminate()
        if result is None:
            break
    if result is None:
        result = f"{MAX_VALUE}"
    else:
        result = f"{result}"
    logging.info(f"Simulation result for cycle {cycle}: {result}")
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    print(result)
    sys.exit(0)


def setup_environment(kwargs):
    """
    Fetches dataset, battery IDs, and paths from environment variables or kwargs.
    """
    dataset_id = kwargs.get("dataset_id")
    battery_id = kwargs.get("battery_id")
    dataset_path = os.getenv(kwargs.get("dataset_path"))
    inputs_path = os.getenv(kwargs.get("inputs_path"))
    result_path = os.getenv(kwargs.get("result_path"))

    # Create a dictionary to easily map variable names to their values
    env_vars = {
        "dataset_path": dataset_path,
        "inputs_path": inputs_path,
        "result_path": result_path,
    }

    # Check each environment variable and collect the names of those that are not set
    missing_vars = [
        var_name for var_name, var_value in env_vars.items() if var_value is None
    ]

    if missing_vars:
        # Raise an error with the names of the missing environment variables
        missing_vars_str = ", ".join(
            missing_vars
        )  # Join the list of missing variable names into a string
        raise ValueError(
            f"Required environment variable(s) not set: {missing_vars_str}"
        )

    # Ensure common folder exists
    common_folder_path = ensure_common_folder_exists(
        inputs_path, dataset_id, battery_id
    )
    return common_folder_path, dataset_path, result_path, inputs_path


def setup_logging(log_path: str, log_to_file, verbose):
    """
    Configures logging based on the verbose flag.
    """
    if log_to_file:
        logging.basicConfig(
            filename=log_path,
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )


def setup_paths(kwargs):
    """
    Constructs paths necessary for the simulation.
    """
    common_folder_path, dataset_path, result_path, inputs_path = setup_environment(
        kwargs
    )
    parameter_file_path = get_parameter_path(
        common_folder_path, id_configuration=kwargs.get("id_configuration")
    )
    result_path = get_result_path(
        common_folder_path, id_configuration=kwargs.get("id_configuration")
    )
    state_path = get_state_path(
        common_folder_path, id_configuration=kwargs.get("id_configuration")
    )
    log_path = get_log_path(
        common_folder_path, id_configuration=kwargs.get("id_configuration")
    )
    return common_folder_path, parameter_file_path, result_path, state_path, log_path


def initialize_pybamm_wrapper(parameter_file_path, result_path, state_path, kwargs):
    """
    Initializes model parameters and PyBaMM wrapper for the simulation.
    """
    base_param_path = kwargs.get("base_param_path")
    external_param = pybamm.ParameterValues("OKane2022")
    model_parameters = ModelParameters.ModelParameters(
        file_path=base_param_path, external_param=external_param, **kwargs
    )

    if kwargs.get("save_param"):
        model_parameters.save_param(parameter_file_path)

    pybamm_wrapper = PyBammWrapper(
        id_configuration=kwargs.get("id_configuration"),
        seed=kwargs.get("seed"),
        dataset_path=str(os.getenv(kwargs.get("dataset_path"))),
        result_path=result_path,
        state_path=state_path,
        instance_id=kwargs.get("id_instance"),
        id_dataset=kwargs.get("dataset_id"),
        id_battery=kwargs.get("battery_id"),
        model_parameters=model_parameters,
    )
    return model_parameters, pybamm_wrapper


def create_degradation_parameters(**kwargs):
    params = DegradationParameters(**kwargs)
    return params


def run_pybamm_with_timeout(
    current_pybamm: PyBammWrapper, n_cycle, queue, verbose=False
):
    results = None
    with suppress_output_context(verbose=verbose):
        try:
            logging.info("Starting model run")
            results = current_pybamm.run_pybamm(n_cycle)
        except Exception as exception:
            logging.info(f"Exception found running model {exception}")
            results = MAX_VALUE
    queue.put(results)

    return 0

def init_pybamm_with_timeout(
    current_pybamm: PyBammWrapper, queue, verbose=False
):
    
    result = None
    with suppress_output_context(verbose=verbose):
        try:
            logging.info("Starting model initiatiation")
            state = current_pybamm.initialize_state()
            result = state
        except Exception as exception:
            logging.info(f"Exception found running model initialization {exception}")
    logging.info("Saliendo")
    queue.put(result)

    return 0
def signal_handler(sig, frame):
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    print(MAX_VALUE + "\n")
    sys.exit(0)


if __name__ == "__main__":
    handler_sig = [signal.SIGABRT, signal.SIGSEGV]
    # for sig in handler_sig:
    #     try:
    #         signal.signal(sig, signal_handler)
    #     except OSError:
    #         continue
    # (copy_stdout, copy_std_error) =  suppress_all_output(0)

    # restore_output(copy_stdout, copy_std_error, 0)

    create_and_run_pybamm_simulation()
    sys.exit(0)
