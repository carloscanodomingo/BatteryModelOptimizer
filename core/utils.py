import json
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
import pybamm


def get_base_path(battery_id, id_configuration):
    return f"{battery_id}_{id_configuration}"


def ensure_common_folder_exists(input_path, dataset_id, battery_id):
    """
    Constructs a common folder path based on input_path, dataset_id, and battery_id,
    ensures the folder exists, and returns the path.

    Parameters:
    - input_path: The base path for inputs.
    - dataset_id: Identifier for the dataset.
    - battery_id: Identifier for the battery.

    Returns:
    The path to the common folder.
    """
    folder_path = os.path.join(input_path, dataset_id, battery_id)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def read_json_file(file_path):
    """
    Attempts to read a JSON file and return its contents.

    Parameters:
    - file_path: The path to the file to read.

    Returns:
    The contents of the JSON file or None if the file couldn't be read.
    """
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
    return None


def get_file_path(common_folder_path, id_configuration, filename):
    """
    Attempts to read the parameter file from the common folder.

    Parameters:
    - common_folder_path: The path to the common folder.
    - filename: The name of the parameter file.
    Returns:
    The contents of the parameter file or None if it couldn't be read.
    """
    return os.path.join(common_folder_path, f"{id_configuration}_{filename}")


def get_parameter_path(common_folder_path, id_configuration):
    """
    Attempts to read the parameter file from the common folder.

    Parameters:
    - common_folder_path: The path to the common folder.
    - filename: The name of the parameter file.
    Returns:
    The contents of the parameter file or None if it couldn't be read.
    """
    return get_file_path(
        common_folder_path, id_configuration=id_configuration, filename="param.json"
    )


def get_state_path(common_folder_path, id_configuration):
    """
    Attempts to read the parameter file from the common folder.

    Parameters:
    - common_folder_path: The path to the common folder.
    - filename: The name of the parameter file.
    Returns:
    The contents of the parameter file or None if it couldn't be read.
    """
    return get_file_path(
        common_folder_path, id_configuration=id_configuration, filename="state.Wp"
    )


def get_log_path(common_folder_path, id_configuration):
    """
    Attempts to read the parameter file from the common folder.

    Parameters:
    - common_folder_path: The path to the common folder.
    - filename: The name of the parameter file.
    Returns:
    The contents of the parameter file or None if it couldn't be read.
    """
    return get_file_path(
        common_folder_path, id_configuration=id_configuration, filename="info.log"
    )


def get_result_path(common_folder_path, id_configuration):
    """
    Attempts to read the parameter file from the common folder.

    Parameters:
    - common_folder_path: The path to the common folder.
    - filename: The name of the parameter file.
    Returns:
    The contents of the parameter file or None if it couldn't be read.
    """
    return get_file_path(
        common_folder_path, id_configuration=id_configuration, filename="results.Wp"
    )


def save_to_json_file(data, file_path):
    """
    Saves the given data to a JSON file at the specified path.

    Parameters:
    - data: The Python object to save (must be serializable to JSON).
    - file_path: The path to the file where data should be saved.
    """
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully saved to {file_path}")
    except Exception as e:
        print(f"Failed to save data to {file_path}: {e}")


def save_parameter_file(common_folder_path, data, filename="param.json"):
    """
    Saves the given data to a parameter file in the common folder.

    Parameters:
    - common_folder_path: The path to the common folder.
    - data: The Python object to save as the parameter file content.
    - filename: The name of the parameter file. Defaults to "param.json".
    """
    param_file_path = os.path.join(common_folder_path, filename)
    save_to_json_file(data, param_file_path)


def get_common_path(inputs_path, dataset_id, battery_id, additional_parts=None):
    """
    Constructs a common path used throughout the system.

    Parameters:
    - inputs_path: Base input path.
    - dataset_id: ID of the dataset.
    - battery_id: ID of the battery.
    - additional_parts: List of additional path parts or None.

    Returns:
    A string representing the constructed path.
    """
    parts = [inputs_path, dataset_id, battery_id]
    if additional_parts:
        parts.extend(additional_parts)
    return os.path.join(*parts)


@dataclass
class PybammOutput:
    df: pd.DataFrame

    def __init__(self, solution: pybamm.Solution):
        relative_time = solution["Time [h]"].entries - np.min(
            solution["Time [h]"].entries
        )
        C = solution["Current [A]"].entries
        V = solution["Battery voltage [V]"].entries
        Dis = solution["Discharge capacity [A.h]"].entries
        data = solution.get_data_dict(None)
        Cycle = data["Cycle"]
        Step = data["Step"][-len(Cycle) :]

        # Extract the data for the current cycle
        cycle_relative_time = relative_time - np.min(relative_time)

        # Create a dataframe for the current cycle
        self.df = pd.DataFrame(
            {
                "relative_time": cycle_relative_time,
                "C": C,
                "Dis": Dis,
                "V": V,
                "Step": Step,
            }
        )
