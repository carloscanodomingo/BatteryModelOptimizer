from dataclasses import dataclass, field, InitVar, fields

import logging
import os
import pybamm
from pathlib import Path
from typing import Optional, TypeVar
from core.Parameters.DegradationParameters import DegradationParameters
from core.Parameters.NonDegradationParameters import NonDegradationParameters
from core.utils import get_base_path
import json


@dataclass
class ModelParameters:
    non_degradation_parameters: NonDegradationParameters = field(init=False)
    degradation_parameters: Optional[DegradationParameters] = field(init=False)

    def __init__(
        self,
        file_path: Optional[str],
        **kwargs,
    ):

        # Extract parameters from kwargs or use saved ones
        json_str = self.read_from_file(file_path) if file_path else None
        saved_non_degradation_parameter, saved_degradation_parameter = (
            self.from_json(json_str) if json_str else (None, None)
        )

        # Extract or use saved non-degradation parameters
        command_non_degradation_parameter = self._extract_parameters(
            NonDegradationParameters, kwargs
        )

        if saved_non_degradation_parameter:
            logging.info(
                "Added Non degradation command to parameters found in param file"
            )
            non_degradation_parameters = saved_non_degradation_parameter._compose_param(
                command_non_degradation_parameter
            )
        else:
            logging.info("Using Non degradation command parameters")
            non_degradation_parameters = command_non_degradation_parameter
        if not non_degradation_parameters:
            raise ValueError("Non-degradation parameters could not be found or loaded.")
        self.non_degradation_parameters = non_degradation_parameters

        # Extract or use saved degradation parameters
        command_degradation_parameter = self._extract_parameters(
            DegradationParameters, kwargs
        )

        if saved_degradation_parameter:
            logging.info("Added degradation command to parameters found in param file")
            self.degradation_parameters = saved_degradation_parameter._compose_param(
                command_degradation_parameter
            )
        else:
            self.degradation_parameters = command_degradation_parameter

    @staticmethod
    def _extract_parameters(param_class, kwargs):
        keys = param_class.__annotations__.keys()
        list_keys = (kwargs.get(key) is not None for key in keys)
        if any(list_keys):
            return param_class.create_instance(**kwargs)
        else:
            return None

    @staticmethod
    def _read_parameters(param_class, json_str: str):
        """Reads a ModelParameters instance from a JSON file."""
        try:
            return param_class.from_json(json_str)
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from the file: {json_str}")
        return None

    def _parameters_match(self, other):
        return (
            self.non_degradation_parameters == other.non_degradation_parameters
            and self.degradation_parameters == other.degradation_parameters
        )

    def update_param(self, param: pybamm.ParameterValues):
        """
        Updates PyBaMM ParameterValues with non-degradation and optional degradation parameters.

        Applies updates sequentially: first from non-degradation parameters, then from
        degradation parameters if they are specified. The operation modifies the input
        ParameterValues in place and returns the modified object.

        Parameters:
        - param (pybamm.ParameterValues): The parameter values to update.

        Returns:
        - pybamm.ParameterValues: The updated parameter values.
        """
        param = self.non_degradation_parameters.update_param(param)
        # Directly attempt to update with degradation_parameters, if it exists.
        return (
            self.degradation_parameters.update_param(param)
            if self.degradation_parameters
            else param
        )

    def update_param_non_degradation(self, **kwargs):
        """Updates non-degradation parameters with provided keyword arguments."""
        self.non_degradation_parameters.update_from_kwargs(**kwargs)

    def update_param_degradation(self, **kwargs):
        """Updates degradation parameters with provided keyword arguments, if they exist."""
        if self.degradation_parameters is not None:
            self.degradation_parameters.update_from_kwargs(**kwargs)
        else:
            logging.warning(
                "Trying to update degradation param when no degradation parameters have been set."
            )

    def to_json(self) -> str:
        """Serializes the ModelParameters instance to a JSON string."""
        model_params_dict = {
            "non_degradation_parameters": self.non_degradation_parameters.to_dict(),
            "degradation_parameters": (
                self.degradation_parameters.to_dict()
                if self.degradation_parameters
                else None
            ),
        }
        return json.dumps(model_params_dict, indent=4)

    @classmethod
    def from_json(cls, json_str: str):
        """Deserializes a ModelParameters instance from a JSON string."""
        data = json.loads(json_str)
        # Manually set the parameters from the deserialized data
        if (
            "non_degradation_parameters" in data
            and data["non_degradation_parameters"] is not None
        ):
            non_deg_params = NonDegradationParameters.from_dict(
                data["non_degradation_parameters"]
            )
        else:
            non_deg_params = None
        if (
            "degradation_parameters" in data
            and data["degradation_parameters"] is not None
        ):
            deg_params = DegradationParameters.from_dict(data["degradation_parameters"])
        else:
            deg_params = None

        return non_deg_params, deg_params

    def check_models_parameter(self, file_path: str):
        """Compare the current object with one saved in a JSON file."""
        try:
            with open(file_path, "r") as f:
                file_content = f.read()
                file_object = self.from_json(file_content)

                # Now, compare the deserialized object with the current instance
                # This assumes you have defined a comparison logic in __eq__ or similar
                return file_object == self
        except FileNotFoundError:
            print(f"The file {file_path} was not found.")
            return False
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the file: {file_path}")
            return False

    def to_dict(self) -> dict:
        """Converts the instance to a dictionary, calling to_dict on inner class instances."""
        result = {
            "non_degradation_parameters": self.non_degradation_parameters.to_dict(),
        }

        # Only include degradation parameters if they are not None
        if self.degradation_parameters is not None:
            result["degradation_parameters"] = self.degradation_parameters.to_dict()

        return result

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def save_param(self, file_path: str):
        """
        Saves the ModelParameters instance to a JSON file only if the file does not exist.

        Parameters:
        - file_path (str): The path to the file where the instance should be saved.
        """
        # Check if the file already exists
        if os.path.exists(file_path):
            logging.info(
                f"File {file_path} already exists. Parameters not saved to avoid overwriting."
            )
            # Optional: Add additional handling here, like asking for user input or creating a backup.
        else:
            # Serialize the instance to a JSON string
            model_params_json = self.to_json()

            # Ensure the directory exists before writing the file
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            # Write the JSON string to the specified file
            with open(file_path, "w") as file:
                file.write(model_params_json)
            logging.info(f"Model parameters saved to {file_path}")

    @staticmethod
    def read_from_file(file_path: str) -> Optional[str]:
        """Reads a ModelParameters instance from a JSON file."""
        try:
            with open(file_path, "r") as file:
                logging.info(f"File found: {file_path}")
                json_str = file.read()
                return json_str

        except FileNotFoundError:
            logging.info(f"File not found: {file_path}")
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from the file: {file_path}")

        return None
