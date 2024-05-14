import json
import logging
from dataclasses import dataclass, fields
from typing import Optional

import pybamm


@dataclass
class DegradationParameters:
    # Fields with default values
    dead_lithium_decay_constant: float = 1e-06
    initial_plated_lithium_concentration: float = 0.0
    lithium_metal_partial_molar_volume: float = 1.3e-05
    lithium_plating_kinetic_rate_constant: float = 1e-09
    lithium_plating_transfer_coefficient: float = 0.65
    negative_electrode_lam_constant_exponential_term: float = 2.0
    negative_electrode_lam_constant_proportional_term: float = 2.7778e-07
    negative_electrode_paris_law_constant_b: float = 1.12
    negative_electrode_paris_law_constant_m: float = 2.2
    negative_electrode_poissons_ratio: float = 0.3
    negative_electrode_youngs_modulus: float = 15000000000.0
    negative_electrode_critical_stress: float = 60000000.0
    negative_electrode_initial_crack_length: float = 2e-08
    negative_electrode_initial_crack_width: float = 1.5e-08
    negative_electrode_number_of_cracks_per_unit_area: float = 3180000000000000.0
    negative_electrode_partial_molar_volume: float = 3.1e-06
    negative_electrode_reference_concentration_for_free_of_deformation: float = 0.0
    positive_electrode_lam_constant_exponential_term: float = 2.0
    positive_electrode_lam_constant_proportional_term: float = 2.7778e-07
    positive_electrode_ocp_entropic_change: float = 0.0
    positive_electrode_paris_law_constant_b: float = 1.12
    positive_electrode_paris_law_constant_m: float = 2.2
    positive_electrode_poissons_ratio: float = 0.2
    positive_electrode_youngs_modulus: float = 375000000000.0
    positive_electrode_active_material_volume_fraction: float = 0.665
    positive_electrode_critical_stress: float = 375000000.0
    positive_electrode_initial_crack_length: float = 2e-08
    positive_electrode_initial_crack_width: float = 1.5e-08
    positive_electrode_number_of_cracks_per_unit_area: float = 3180000000000000.0
    positive_electrode_partial_molar_volume: float = 1.25e-05
    positive_electrode_reference_concentration_for_free_of_deformation: float = 0.0
    typical_plated_lithium_concentration: float = 1000.0
    # Complete class-level attribute mapping with verbose keys first
    attribute_map = {
        "Dead lithium decay constant [s-1]": "dead_lithium_decay_constant",
        "Initial plated lithium concentration [mol.m-3]": "initial_plated_lithium_concentration",
        "Lithium metal partial molar volume [m3.mol-1]": "lithium_metal_partial_molar_volume",
        "Lithium plating kinetic rate constant [m.s-1]": "lithium_plating_kinetic_rate_constant",
        "Lithium plating transfer coefficient": "lithium_plating_transfer_coefficient",
        "Negative electrode LAM constant exponential term": "negative_electrode_lam_constant_exponential_term",
        "Negative electrode LAM constant proportional term [s-1]": "negative_electrode_lam_constant_proportional_term",
        "Negative electrode Paris' law constant b": "negative_electrode_paris_law_constant_b",
        "Negative electrode Paris' law constant m": "negative_electrode_paris_law_constant_m",
        "Negative electrode Poisson's ratio": "negative_electrode_poissons_ratio",
        "Negative electrode Young's modulus [Pa]": "negative_electrode_youngs_modulus",
        "Negative electrode critical stress [Pa]": "negative_electrode_critical_stress",
        "Negative electrode initial crack length [m]": "negative_electrode_initial_crack_length",
        "Negative electrode initial crack width [m]": "negative_electrode_initial_crack_width",
        "Negative electrode number of cracks per unit area [m-2]": "negative_electrode_number_of_cracks_per_unit_area",
        "Negative electrode partial molar volume [m3.mol-1]": "negative_electrode_partial_molar_volume",
        "Negative electrode reference concentration for free of deformation [mol.m-3]": "negative_electrode_reference_concentration_for_free_of_deformation",
        "Positive electrode LAM constant exponential term": "positive_electrode_lam_constant_exponential_term",
        "Positive electrode LAM constant proportional term [s-1]": "positive_electrode_lam_constant_proportional_term",
        "Positive electrode OCP entropic change [V.K-1]": "positive_electrode_ocp_entropic_change",
        "Positive electrode Paris' law constant b": "positive_electrode_paris_law_constant_b",
        "Positive electrode Paris' law constant m": "positive_electrode_paris_law_constant_m",
        "Positive electrode Poisson's ratio": "positive_electrode_poissons_ratio",
        "Positive electrode Young's modulus [Pa]": "positive_electrode_youngs_modulus",
        "Positive electrode active material volume fraction": "positive_electrode_active_material_volume_fraction",
        "Positive electrode critical stress [Pa]": "positive_electrode_critical_stress",
        "Positive electrode initial crack length [m]": "positive_electrode_initial_crack_length",
        "Positive electrode initial crack width [m]": "positive_electrode_initial_crack_width",
        "Positive electrode number of cracks per unit area [m-2]": "positive_electrode_number_of_cracks_per_unit_area",
        "Positive electrode partial molar volume [m3.mol-1]": "positive_electrode_partial_molar_volume",
        "Positive electrode reference concentration for free of deformation [mol.m-3]": "positive_electrode_reference_concentration_for_free_of_deformation",
        "Typical plated lithium concentration [mol.m-3]": "typical_plated_lithium_concentration",
        # Continue for any additional attributes...
    }
    def _compose_param(self, source: Optional['DegradationParameters']) -> 'DegradationParameters':
        """
        Update the attributes of the current instance with those from source where they are not None.
        """
        if source:
            for field_in_object in fields(self):
                new_value = getattr(source, field_in_object.name)
                if new_value is not None:
                    setattr(self, field_in_object.name, new_value)
        return self

    def validate_fields(self):
        """Validate that all fields are real numbers from 0 to ∞ or None."""
        for field in fields(self):
            value = getattr(self, field.name)
            # Skip validation if the value is None
            if value is None:
                continue
            # Proceed with validation if the value is not None
            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError(
                    f"{field.name} must be a real number from 0 to infinity or None. Got {value}."
                )

    def is_empty(self) -> bool:
        """
        Checks if all the attributes of the instance are set to None.

        Returns:
        - bool: True if all attributes are None, False otherwise.
        """
        for field_info in fields(self):
            if getattr(self, field_info.name) is not None:
                return False
        return True

    def __post_init__(self):
        # This method is called automatically after dataclass's __init__
        # It's useful for additional initialization.
        logging.info(f"An instance of {type(self).__name__} has been initialized.")

        # Validate that all parameters are real numbers from 0 to infinity.
        self.validate_fields()

    def update_from_kwargs(self, **kwargs):
        """Dynamically update attributes from kwargs if they exist in the class."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.validate_fields()

    @classmethod
    def create_instance(cls, external_param: pybamm.ParameterValues, **kwargs):
        """Create an instance of NonDegradationParameters, setting fields from kwargs if provided."""
        instance = cls()
        instance.update_from_kwargs(**kwargs)
        # instance.update_from_external_param(external_param)
        return instance

    def to_json(self) -> str:
        """Serialize the instance to a JSON string."""
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_json(cls, json_str: str):
        """Deserialize an instance from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self):
        # Inverse the attribute_map to use it for deserialization
        inverse_map = {v: k for k, v in self.attribute_map.items()}

        return {inverse_map[attr]: getattr(self, attr) for attr in inverse_map}

    @classmethod
    def from_dict(cls, data: dict):
        """
        Deserializes a dictionary into an instance of NonDegradationParameters,
        looking for specific keys and setting the corresponding class attributes.

        Parameters:
        - data (dict): A dictionary with keys corresponding to the verbose descriptions
                       of the NonDegradationParameters attributes.

        Returns:
        - An instance of NonDegradationParameters populated with the data from the dictionary.
        """
        instance = cls()

        for key, attr_name in cls.attribute_map.items():
            if key in data:
                setattr(instance, attr_name, data[key])

        return instance

    def update_param(self, param: pybamm.ParameterValues):
        param.update(self.to_dict(), check_already_exists=False)
        return param

    def update_param(self, param: pybamm.ParameterValues):
        """
        Updates the given PyBaMM ParameterValues instance with attributes of this class,
        skipping attributes that have None values. This method constructs a filtered
        dictionary of attributes that are not None and then updates the param instance in one call.

        Parameters:
        - param (pybamm.ParameterValues): The parameter values to be updated.

        Returns:
        - pybamm.ParameterValues: The updated parameter values.
        """
        # Generate the dictionary representation
        param_dict = self.to_dict()

        # Filter out any key-value pairs where the value is None
        filtered_param_dict = {
            key: value for key, value in param_dict.items() if value is not None
        }

        # Update the param with the filtered dictionary if it's not empty
        if filtered_param_dict:
            param.update(filtered_param_dict, check_already_exists=False)

        return param

    def update_from_external_param(self, param: pybamm.ParameterValues):
        """
        Updates attributes of this class with values from an external PyBaMM ParameterValues instance,
        for attributes that are currently None.

        Parameters:
        - param (pybamm.ParameterValues): The external parameter values to use for updating.
        """
        inverse_map = {v: k for k, v in self.attribute_map.items()}
        # Iterate over the class attributes using the attribute map for mapping keys
        for attr, param_key in inverse_map.items():
            external_value = param.__dict__["_dict_items"][param_key]
            # If the current attribute value is None and the param_key exists in the external parameters
            if getattr(self, attr) is None and external_value is not None:
                # Update the current attribute with the value from the external parameters
                setattr(self, attr, external_value)


def get_okane2022_degradation_parameters():
    degradation_parameters = {
        "Dead lithium decay constant [s-1]": 1e-06,
        "Initial plated lithium concentration [mol.m-3]": 0.0,
        "Lithium metal partial molar volume [m3.mol-1]": 1.3e-05,
        "Lithium plating kinetic rate constant [m.s-1]": 1e-09,
        "Lithium plating transfer coefficient": 0.65,
        "Negative electrode LAM constant exponential term": 2.0,
        "Negative electrode LAM constant proportional term [s-1]": 2.7778e-07,
        "Negative electrode Paris' law constant b": 1.12,
        "Negative electrode Paris' law constant m": 2.2,
        "Negative electrode Poisson's ratio": 0.3,
        "Negative electrode Young's modulus [Pa]": 15000000000.0,
        "Negative electrode critical stress [Pa]": 60000000.0,
        "Negative electrode initial crack length [m]": 2e-08,
        "Negative electrode initial crack width [m]": 1.5e-08,
        "Negative electrode number of cracks per unit area [m-2]": 3180000000000000.0,
        "Negative electrode partial molar volume [m3.mol-1]": 3.1e-06,
        "Negative electrode reference concentration for free of deformation [mol.m-3]": 0.0,
        "Positive electrode LAM constant exponential term": 2.0,
        "Positive electrode LAM constant proportional term [s-1]": 2.7778e-07,
        "Positive electrode OCP entropic change [V.K-1]": 0.0,
        "Positive electrode Paris' law constant b": 1.12,
        "Positive electrode Paris' law constant m": 2.2,
        "Positive electrode Poisson's ratio": 0.2,
        "Positive electrode Young's modulus [Pa]": 375000000000.0,
        "Positive electrode active material volume fraction": 0.665,
        "Positive electrode critical stress [Pa]": 375000000.0,
        "Positive electrode initial crack length [m]": 2e-08,
        "Positive electrode initial crack width [m]": 1.5e-08,
        "Positive electrode number of cracks per unit area [m-2]": 3180000000000000.0,
        "Positive electrode partial molar volume [m3.mol-1]": 1.25e-05,
        "Positive electrode reference concentration for free of deformation [mol.m-3]": 0.0,
        "Typical plated lithium concentration [mol.m-3]": 1000.0,
    }
    return degradation_parameters
