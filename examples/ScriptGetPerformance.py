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
MAX_TIMEOUT = 60 * 5  # FIve minutes maximum


@click.command()
@click.option("--n_cycles", default=200, help="Cycles to simulate")
@click.option(
    "--log_to_file", default=True, type=bool, help="Set true to log to a file"
)
@click.option(
    "--param_path",
    type=str,
    help="Set this value to use a param file as base parameters",
)
@click.option(
    "--dataset_path",
    default="EV_DATAPATH",
    help="Path where file with battery data is located",
)
@click.option("--inputs_path", default="INPUTS_PATH", help="Path where state and param")
@click.option("--result_path", default="RESULT_PATH", help="Path where state and param")
@click.option("--battery_id", default="W04", type=str, help="Battery ID")
@click.option("--dataset_id", default="EV", type=str, help="Dataset ID")
def cli(
    n_cycles,
    log_to_file,
    param_path,
    battery_id,
    dataset_id,
    result_path,
    dataset_path,
    inputs_path,
):
    """
    This is a CLI tool that takes various parameters to control
    a PyBaMM-based simulation environment.

    It handles operations modes, logging preferences, parameter settings, and dataset management.
    """
    # Your function implementation here
    # Example: click.echo(f"Mode selected: {mode}")
    dataset_path = os.getenv(dataset_path)
    inputs_path = os.getenv(inputs_path)
    result_path = os.getenv(result_path)
    if dataset_path is None or result_path is None or inputs_path is None:
        return 0
    param_id = extract_file_name(param_path)
    log_path = os.path.join(result_path, battery_id)
    os.makedirs(log_path, exist_ok=True)
    log_path = os.path.join(log_path, f"{param_id}.log")
    state_path = os.path.join(inputs_path, battery_id)
    os.makedirs(state_path, exist_ok=True)
    state_path = os.path.join(state_path, f"{param_id}.state")
    setup_logging(log_path, log_to_file)
    logging.info(
        (
            f"START Pybamm Run n cycles {n_cycles} -",
            f"Threads: {len(os.sched_getaffinity(0))}",
            f", Battery {battery_id}",
        )
    )
    external_param = pybamm.ParameterValues("OKane2022")
    model_parameters = ModelParameters.ModelParameters(
        file_path=param_path, external_param=external_param
    )
    current_pybamm = PyBammWrapper(
        id_configuration=param_id,
        seed="911",
        dataset_path=dataset_path,
        result_path=result_path,
        state_path=state_path,
        instance_id="1",
        id_dataset=dataset_id,
        id_battery=battery_id,
        model_parameters=model_parameters,
    )
    current_pybamm.initialize_state()
    for i in range(0, n_cycles):
        current_pybamm.run_pybamm(i)


def extract_file_name(file_path):
    # Get the base name of the file
    base_name = os.path.basename(file_path)
    # Split the base name to remove the extension and get the file name
    file_name, _ = os.path.splitext(base_name)
    return file_name


def setup_logging(log_path: str, log_to_file):
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


if __name__ == "__main__":
    handler_sig = [signal.SIGABRT, signal.SIGSEGV]
    # for sig in handler_sig:
    #     try:
    #         signal.signal(sig, signal_handler)
    #     except OSError:
    #         continue
    # (copy_stdout, copy_std_error) =  suppress_all_output(0)

    # restore_output(copy_stdout, copy_std_error, 0)

    cli()
    sys.exit(0)
