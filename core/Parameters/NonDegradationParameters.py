import json
import logging
from typing import Optional
from dataclasses import InitVar, dataclass, field, fields

import pybamm


@dataclass
class NonDegradationParameters:
    # Cell
    negative_current_collector_thickness: float = 1.2e-05
    negative_electrode_thickness: float = 8.52e-05
    separator_thickness: float = 1.2e-05
    positive_electrode_thickness: float = 7.56e-05
    positive_current_collector_thickness: float = 1.6e-05
    electrode_height: float = 0.065
    electrode_width: float = 1.58
    cell_cooling_surface_area: float = 0.00531
    cell_volume: float = 2.42e-05
    cell_thermal_expansion_coefficient: float = 1.1e-06
    negative_current_collector_conductivity: float = 58411000.0
    positive_current_collector_conductivity: float = 36914000.0
    negative_current_collector_density: float = 8960.0
    positive_current_collector_density: float = 2700.0
    negative_current_collector_specific_heat_capacity: float = 385.0
    positive_current_collector_specific_heat_capacity: float = 897.0
    negative_current_collector_thermal_conductivity: float = 401.0
    positive_current_collector_thermal_conductivity: float = 237.0
    nominal_cell_capacity: float = 5.0
    current_function: float = 5.0
    contact_resistance: float = 0

    # Negative electrode
    negative_electrode_conductivity: float = 215.0
    maximum_concentration_in_negative_electrode: float = 33133.0
    negative_electrode_porosity: float = 0.25
    negative_electrode_active_material_volume_fraction: float = 0.75
    negative_particle_radius: float = 5.86e-06
    negative_electrode_bruggeman_coefficient_electrolyte: float = 1.5
    negative_electrode_bruggeman_coefficient_electrode: float = 1.5
    negative_electrode_charge_transfer_coefficient: float = 0.5
    negative_electrode_double_layer_capacity: float = 0.2
    negative_electrode_density: float = 1657.0
    negative_electrode_specific_heat_capacity: float = 700.0
    negative_electrode_thermal_conductivity: float = 1.7
    negative_electrode_ocp_entropic_change: float = 0.0

    # Positive electrode
    positive_electrode_conductivity: float = 0.18
    maximum_concentration_in_positive_electrode: float = 63104.0
    positive_electrode_porosity: float = 0.335
    positive_particle_radius: float = 5.22e-06
    positive_electrode_bruggeman_coefficient_electrolyte: float = 1.5
    positive_electrode_bruggeman_coefficient_electrode: float = 1.5
    positive_electrode_charge_transfer_coefficient: float = 0.5
    positive_electrode_double_layer_capacity: float = 0.2
    positive_electrode_density: float = 3262.0
    positive_electrode_specific_heat_capacity: float = 700.0
    positive_electrode_thermal_conductivity: float = 2.1

    # Separator
    separator_porosity: float = 0.47
    separator_bruggeman_coefficient_electrolyte: float = 1.5
    separator_density: float = 397.0
    separator_specific_heat_capacity: float = 700.0
    separator_thermal_conductivity: float = 0.16

    # Electrolyte
    initial_concentration_in_electrolyte: float = 1000.0
    cation_transference_number: float = 0.2594
    thermodynamic_factor: float = 1.0

    # Experiment
    reference_temperature: float = 298.15
    total_heat_transfer_coefficient: float = 10.0
    ambient_temperature: float = 298.15
    number_of_electrodes_connected_in_parallel_to_make_a_cell: float = 1.0
    number_of_cells_connected_in_series_to_make_a_battery: float = 1.0
    lower_voltage_cut_off: float = 2.5
    upper_voltage_cut_off: float = 4.2
    open_circuit_voltage_at_0_soc: float = 2.5
    open_circuit_voltage_at_100_soc: float = 4.2
    initial_concentration_in_negative_electrode: float = 29866.0
    initial_concentration_in_positive_electrode: float = 17038.0
    initial_temperature: float = 298.15
    attribute_map = {
        "Negative current collector thickness [m]": "negative_current_collector_thickness",
        "Negative electrode thickness [m]": "negative_electrode_thickness",
        "Separator thickness [m]": "separator_thickness",
        "Positive electrode thickness [m]": "positive_electrode_thickness",
        "Positive current collector thickness [m]": "positive_current_collector_thickness",
        "Electrode height [m]": "electrode_height",
        "Electrode width [m]": "electrode_width",
        "Cell cooling surface area [m2]": "cell_cooling_surface_area",
        "Cell volume [m3]": "cell_volume",
        "Cell thermal expansion coefficient [m.K-1]": "cell_thermal_expansion_coefficient",
        "Negative current collector conductivity [S.m-1]": "negative_current_collector_conductivity",
        "Positive current collector conductivity [S.m-1]": "positive_current_collector_conductivity",
        "Negative current collector density [kg.m-3]": "negative_current_collector_density",
        "Positive current collector density [kg.m-3]": "positive_current_collector_density",
        "Negative current collector specific heat capacity [J.kg-1.K-1]": "negative_current_collector_specific_heat_capacity",
        "Positive current collector specific heat capacity [J.kg-1.K-1]": "positive_current_collector_specific_heat_capacity",
        "Negative current collector thermal conductivity [W.m-1.K-1]": "negative_current_collector_thermal_conductivity",
        "Positive current collector thermal conductivity [W.m-1.K-1]": "positive_current_collector_thermal_conductivity",
        "Nominal cell capacity [A.h]": "nominal_cell_capacity",
        "Current function [A]": "current_function",
        "Contact resistance [Ohm]": "contact_resistance",
        "Negative electrode conductivity [S.m-1]": "negative_electrode_conductivity",
        "Maximum concentration in negative electrode [mol.m-3]": "maximum_concentration_in_negative_electrode",
        "Negative electrode porosity": "negative_electrode_porosity",
        "Negative electrode active material volume fraction": "negative_electrode_active_material_volume_fraction",
        "Negative particle radius [m]": "negative_particle_radius",
        "Negative electrode Bruggeman coefficient (electrolyte)": "negative_electrode_bruggeman_coefficient_electrolyte",
        "Negative electrode Bruggeman coefficient (electrode)": "negative_electrode_bruggeman_coefficient_electrode",
        "Negative electrode charge transfer coefficient": "negative_electrode_charge_transfer_coefficient",
        "Negative electrode double-layer capacity [F.m-2]": "negative_electrode_double_layer_capacity",
        "Negative electrode density [kg.m-3]": "negative_electrode_density",
        "Negative electrode specific heat capacity [J.kg-1.K-1]": "negative_electrode_specific_heat_capacity",
        "Negative electrode thermal conductivity [W.m-1.K-1]": "negative_electrode_thermal_conductivity",
        "Negative electrode OCP entropic change [V.K-1]": "negative_electrode_ocp_entropic_change",
        "Positive electrode conductivity [S.m-1]": "positive_electrode_conductivity",
        "Maximum concentration in positive electrode [mol.m-3]": "maximum_concentration_in_positive_electrode",
        "Positive electrode porosity": "positive_electrode_porosity",
        "Positive particle radius [m]": "positive_particle_radius",
        "Positive electrode Bruggeman coefficient (electrolyte)": "positive_electrode_bruggeman_coefficient_electrolyte",
        "Positive electrode Bruggeman coefficient (electrode)": "positive_electrode_bruggeman_coefficient_electrode",
        "Positive electrode charge transfer coefficient": "positive_electrode_charge_transfer_coefficient",
        "Positive electrode double-layer capacity [F.m-2]": "positive_electrode_double_layer_capacity",
        "Positive electrode density [kg.m-3]": "positive_electrode_density",
        "Positive electrode specific heat capacity [J.kg-1.K-1]": "positive_electrode_specific_heat_capacity",
        "Positive electrode thermal conductivity [W.m-1.K-1]": "positive_electrode_thermal_conductivity",
        "Separator porosity": "separator_porosity",
        "Separator Bruggeman coefficient (electrolyte)": "separator_bruggeman_coefficient_electrolyte",
        "Separator density [kg.m-3]": "separator_density",
        "Separator specific heat capacity [J.kg-1.K-1]": "separator_specific_heat_capacity",
        "Separator thermal conductivity [W.m-1.K-1]": "separator_thermal_conductivity",
        "Initial concentration in electrolyte [mol.m-3]": "initial_concentration_in_electrolyte",
        "Cation transference number": "cation_transference_number",
        "Thermodynamic factor": "thermodynamic_factor",
        "Reference temperature [K]": "reference_temperature",
        "Total heat transfer coefficient [W.m-2.K-1]": "total_heat_transfer_coefficient",
        "Ambient temperature [K]": "ambient_temperature",
        "Number of electrodes connected in parallel to make a cell": "number_of_electrodes_connected_in_parallel_to_make_a_cell",
        "Number of cells connected in series to make a battery": "number_of_cells_connected_in_series_to_make_a_battery",
        "Lower voltage cut-off [V]": "lower_voltage_cut_off",
        "Upper voltage cut-off [V]": "upper_voltage_cut_off",
        "Open-circuit voltage at 0% SOC [V]": "open_circuit_voltage_at_0_soc",
        "Open-circuit voltage at 100% SOC [V]": "open_circuit_voltage_at_100_soc",
        "Initial concentration in negative electrode [mol.m-3]": "initial_concentration_in_negative_electrode",
        "Initial concentration in positive electrode [mol.m-3]": "initial_concentration_in_positive_electrode",
        "Initial temperature [K]": "initial_temperature",
    }

    def _compose_param(self, source: Optional['NonDegradationParameters']) -> 'NonDegradationParameters':
        """
        Update the attributes of the current instance with those from source where they are not None.
        """
        if source:
            for field_in_object in fields(self):
                logging.info(f"Get attribute before {field_in_object}")
                new_value = getattr(source, field_in_object.name)
                logging.info(f"Get attribute {field_in_object}")
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

    def other(
        self,
        negative_current_collector_thickness,
        negative_electrode_thickness,
        separator_thickness,
        positive_electrode_thickness,
        positive_current_collector_thickness,
        electrode_height,
        electrode_width,
        cell_cooling_surface_area,
        cell_volume,
        cell_thermal_expansion_coefficient,
        negative_current_collector_conductivity,
        positive_current_collector_conductivity,
        negative_current_collector_density,
        positive_current_collector_density,
        negative_current_collector_specific_heat_capacity,
        positive_current_collector_specific_heat_capacity,
        negative_current_collector_thermal_conductivity,
        positive_current_collector_thermal_conductivity,
        nominal_cell_capacity,
        current_function,
        contact_resistance,
        negative_electrode_conductivity,
        maximum_concentration_in_negative_electrode,
        negative_electrode_porosity,
        negative_electrode_active_material_volume_fraction,
        negative_particle_radius,
        negative_electrode_bruggeman_coefficient_electrolyte,
        negative_electrode_bruggeman_coefficient_electrode,
        negative_electrode_charge_transfer_coefficient,
        negative_electrode_double_layer_capacity,
        negative_electrode_density,
        negative_electrode_specific_heat_capacity,
        negative_electrode_thermal_conductivity,
        negative_electrode_ocp_entropic_change,
        positive_electrode_conductivity,
        maximum_concentration_in_positive_electrode,
        positive_electrode_porosity,
        positive_electrode_active_material_volume_fraction,
        positive_particle_radius,
        positive_electrode_bruggeman_coefficient_electrolyte,
        positive_electrode_bruggeman_coefficient_electrode,
        positive_electrode_charge_transfer_coefficient,
        positive_electrode_double_layer_capacity,
        positive_electrode_density,
        positive_electrode_specific_heat_capacity,
        positive_electrode_thermal_conductivity,
        positive_electrode_ocp_entropic_change,
        separator_porosity,
        separator_bruggeman_coefficient_electrolyte,
        separator_density,
        separator_specific_heat_capacity,
        separator_thermal_conductivity,
        initial_concentration_in_electrolyte,
        cation_transference_number,
        thermodynamic_factor,
        reference_temperature,
        total_heat_transfer_coefficient,
        ambient_temperature,
        number_of_electrodes_connected_in_parallel_to_make_a_cell,
        number_of_cells_connected_in_series_to_make_a_battery,
        lower_voltage_cut_off,
        upper_voltage_cut_off,
        open_circuit_voltage_at_0_soc,
        open_circuit_voltage_at_100_soc,
        initial_concentration_in_negative_electrode,
        initial_concentration_in_positive_electrode,
        initial_temperature,
    ):
        self.negative_current_collector_thickness = negative_current_collector_thickness
        self.negative_electrode_thickness = negative_electrode_thickness
        self.separator_thickness = separator_thickness
        self.positive_electrode_thickness = positive_electrode_thickness
        self.positive_current_collector_thickness = positive_current_collector_thickness
        self.electrode_height = electrode_height
        self.electrode_width = electrode_width
        self.cell_cooling_surface_area = cell_cooling_surface_area
        self.cell_volume = cell_volume
        self.cell_thermal_expansion_coefficient = cell_thermal_expansion_coefficient
        self.negative_current_collector_conductivity = (
            negative_current_collector_conductivity
        )
        self.positive_current_collector_conductivity = (
            positive_current_collector_conductivity
        )
        self.negative_current_collector_density = negative_current_collector_density
        self.positive_current_collector_density = positive_current_collector_density
        self.negative_current_collector_specific_heat_capacity = (
            negative_current_collector_specific_heat_capacity
        )
        self.positive_current_collector_specific_heat_capacity = (
            positive_current_collector_specific_heat_capacity
        )
        self.negative_current_collector_thermal_conductivity = (
            negative_current_collector_thermal_conductivity
        )
        self.positive_current_collector_thermal_conductivity = (
            positive_current_collector_thermal_conductivity
        )
        self.nominal_cell_capacity = nominal_cell_capacity
        self.current_function = current_function
        self.contact_resistance = contact_resistance

        self.negative_electrode_conductivity = negative_electrode_conductivity
        self.maximum_concentration_in_negative_electrode = (
            maximum_concentration_in_negative_electrode
        )
        self.negative_electrode_porosity = negative_electrode_porosity
        self.negative_electrode_active_material_volume_fraction = (
            negative_electrode_active_material_volume_fraction
        )
        self.negative_particle_radius = negative_particle_radius
        self.negative_electrode_bruggeman_coefficient_electrolyte = (
            negative_electrode_bruggeman_coefficient_electrolyte
        )
        self.negative_electrode_bruggeman_coefficient_electrode = (
            negative_electrode_bruggeman_coefficient_electrode
        )
        self.negative_electrode_charge_transfer_coefficient = (
            negative_electrode_charge_transfer_coefficient
        )
        self.negative_electrode_double_layer_capacity = (
            negative_electrode_double_layer_capacity
        )
        self.negative_electrode_density = negative_electrode_density
        self.negative_electrode_specific_heat_capacity = (
            negative_electrode_specific_heat_capacity
        )
        self.negative_electrode_thermal_conductivity = (
            negative_electrode_thermal_conductivity
        )
        self.negative_electrode_ocp_entropic_change = (
            negative_electrode_ocp_entropic_change
        )

        # Positive electrode
        self.positive_electrode_conductivity = positive_electrode_conductivity
        self.maximum_concentration_in_positive_electrode = (
            maximum_concentration_in_positive_electrode
        )
        self.positive_electrode_porosity = positive_electrode_porosity
        self.positive_electrode_active_material_volume_fraction = (
            positive_electrode_active_material_volume_fraction
        )
        self.positive_particle_radius = positive_particle_radius
        self.positive_electrode_bruggeman_coefficient_electrolyte = (
            positive_electrode_bruggeman_coefficient_electrolyte
        )
        self.positive_electrode_bruggeman_coefficient_electrode = (
            positive_electrode_bruggeman_coefficient_electrode
        )
        self.positive_electrode_charge_transfer_coefficient = (
            positive_electrode_charge_transfer_coefficient
        )
        self.positive_electrode_double_layer_capacity = (
            positive_electrode_double_layer_capacity
        )
        self.positive_electrode_density = positive_electrode_density
        self.positive_electrode_specific_heat_capacity = (
            positive_electrode_specific_heat_capacity
        )
        self.positive_electrode_thermal_conductivity = (
            positive_electrode_thermal_conductivity
        )
        self.positive_electrode_ocp_entropic_change = (
            positive_electrode_ocp_entropic_change
        )

        # Separator
        self.separator_porosity = separator_porosity
        self.separator_bruggeman_coefficient_electrolyte = (
            separator_bruggeman_coefficient_electrolyte
        )
        self.separator_density = separator_density
        self.separator_specific_heat_capacity = separator_specific_heat_capacity
        self.separator_thermal_conductivity = separator_thermal_conductivity

        # Electrolyte
        self.initial_concentration_in_electrolyte = initial_concentration_in_electrolyte
        self.cation_transference_number = cation_transference_number
        self.thermodynamic_factor = thermodynamic_factor

        # Experiment
        self.reference_temperature = reference_temperature
        self.total_heat_transfer_coefficient = total_heat_transfer_coefficient
        self.ambient_temperature = ambient_temperature
        self.number_of_electrodes_connected_in_parallel_to_make_a_cell = (
            number_of_electrodes_connected_in_parallel_to_make_a_cell
        )
        self.number_of_cells_connected_in_series_to_make_a_battery = (
            number_of_cells_connected_in_series_to_make_a_battery
        )
        self.lower_voltage_cut_off = lower_voltage_cut_off
        self.upper_voltage_cut_off = upper_voltage_cut_off
        self.open_circuit_voltage_at_0_soc = open_circuit_voltage_at_0_soc
        self.open_circuit_voltage_at_100_soc = open_circuit_voltage_at_100_soc
        self.initial_concentration_in_negative_electrode = (
            initial_concentration_in_negative_electrode
        )
        self.initial_concentration_in_positive_electrode = (
            initial_concentration_in_positive_electrode
        )
        self.initial_temperature = initial_temperature
        # return {
        #     "Negative current collector thickness [m]": self.negative_current_collector_thickness,
        #     "Negative electrode thickness [m]": self.negative_electrode_thickness,
        #     "Separator thickness [m]": self.separator_thickness,
        #     "Positive electrode thickness [m]": self.positive_electrode_thickness,
        #     "Positive current collector thickness [m]": self.positive_current_collector_thickness,
        #     "Electrode height [m]": self.electrode_height,
        #     "Electrode width [m]": self.electrode_width,
        #     "Cell cooling surface area [m2]": self.cell_cooling_surface_area,
        #     "Cell volume [m3]": self.cell_volume,
        #     "Cell thermal expansion coefficient [m.K-1]": self.cell_thermal_expansion_coefficient,
        #     "Negative current collector conductivity [S.m-1]": self.negative_current_collector_conductivity,
        #     "Positive current collector conductivity [S.m-1]": self.positive_current_collector_conductivity,
        #     "Negative current collector density [kg.m-3]": self.negative_current_collector_density,
        #     "Positive current collector density [kg.m-3]": self.positive_current_collector_density,
        #     "Negative current collector specific heat capacity [J.kg-1.K-1]": self.negative_current_collector_specific_heat_capacity,
        #     "Positive current collector specific heat capacity [J.kg-1.K-1]": self.positive_current_collector_specific_heat_capacity,
        #     "Negative current collector thermal conductivity [W.m-1.K-1]": self.negative_current_collector_thermal_conductivity,
        #     "Positive current collector thermal conductivity [W.m-1.K-1]": self.positive_current_collector_thermal_conductivity,
        #     "Nominal cell capacity [A.h]": self.nominal_cell_capacity,
        #     "Current function [A]": self.current_function,
        #     "Contact resistance [Ohm]": self.contact_resistance,
        #     "Negative electrode conductivity [S.m-1]": self.negative_electrode_conductivity,
        #     "Maximum concentration in negative electrode [mol.m-3]": self.maximum_concentration_in_negative_electrode,
        #     "Negative electrode porosity": self.negative_electrode_porosity,
        #     "Negative electrode active material volume fraction": self.negative_electrode_active_material_volume_fraction,
        #     "Negative particle radius [m]": self.negative_particle_radius,
        #     "Negative electrode Bruggeman coefficient (electrolyte)": self.negative_electrode_bruggeman_coefficient_electrolyte,
        #     "Negative electrode Bruggeman coefficient (electrode)": self.negative_electrode_bruggeman_coefficient_electrode,
        #     "Negative electrode charge transfer coefficient": self.negative_electrode_charge_transfer_coefficient,
        #     "Negative electrode double-layer capacity [F.m-2]": self.negative_electrode_double_layer_capacity,
        #     "Negative electrode density [kg.m-3]": self.negative_electrode_density,
        #     "Negative electrode specific heat capacity [J.kg-1.K-1]": self.negative_electrode_specific_heat_capacity,
        #     "Negative electrode thermal conductivity [W.m-1.K-1]": self.negative_electrode_thermal_conductivity,
        #     "Negative electrode OCP entropic change [V.K-1]": self.negative_electrode_ocp_entropic_change,
        #     "Positive electrode conductivity [S.m-1]": self.positive_electrode_conductivity,
        #     "Maximum concentration in positive electrode [mol.m-3]": self.maximum_concentration_in_positive_electrode,
        #     "Positive electrode porosity": self.positive_electrode_porosity,
        #     "Positive electrode active material volume fraction": self.positive_electrode_active_material_volume_fraction,
        #     "Positive particle radius [m]": self.positive_particle_radius,
        #     "Positive electrode Bruggeman coefficient (electrolyte)": self.positive_electrode_bruggeman_coefficient_electrolyte,
        #     "Positive electrode Bruggeman coefficient (electrode)": self.positive_electrode_bruggeman_coefficient_electrode,
        #     "Positive electrode charge transfer coefficient": self.positive_electrode_charge_transfer_coefficient,
        #     "Positive electrode double-layer capacity [F.m-2]": self.positive_electrode_double_layer_capacity,
        #     "Positive electrode density [kg.m-3]": self.positive_electrode_density,
        #     "Positive electrode specific heat capacity [J.kg-1.K-1]": self.positive_electrode_specific_heat_capacity,
        #     "Positive electrode thermal conductivity [W.m-1.K-1]": self.positive_electrode_thermal_conductivity,
        #     "Positive electrode OCP entropic change [V.K-1]": self.positive_electrode_ocp_entropic_change,
        #     "Separator porosity": self.separator_porosity,
        #     "Separator Bruggeman coefficient (electrolyte)": self.separator_bruggeman_coefficient_electrolyte,
        #     "Separator density [kg.m-3]": self.separator_density,
        #     "Separator specific heat capacity [J.kg-1.K-1]": self.separator_specific_heat_capacity,
        #     "Separator thermal conductivity [W.m-1.K-1]": self.separator_thermal_conductivity,
        #     "Initial concentration in electrolyte [mol.m-3]": self.initial_concentration_in_electrolyte,
        #     "Cation transference number": self.cation_transference_number,
        #     "Thermodynamic factor": self.thermodynamic_factor,
        #     "Reference temperature [K]": self.reference_temperature,
        #     "Total heat transfer coefficient [W.m-2.K-1]": self.total_heat_transfer_coefficient,
        #     "Ambient temperature [K]": self.ambient_temperature,
        #     "Number of electrodes connected in parallel to make a cell": self.number_of_electrodes_connected_in_parallel_to_make_a_cell,
        #     "Number of cells connected in series to make a battery": self.number_of_cells_connected_in_series_to_make_a_battery,
        #     "Lower voltage cut-off [V]": self.lower_voltage_cut_off,
        #     "Upper voltage cut-off [V]": self.upper_voltage_cut_off,
        #     "Open-circuit voltage at 0% SOC [V]": self.open_circuit_voltage_at_0_soc,
        #     "Open-circuit voltage at 100% SOC [V]": self.open_circuit_voltage_at_100_soc,
        #     "Initial concentration in negative electrode [mol.m-3]": self.initial_concentration_in_negative_electrode,
        #     "Initial concentration in positive electrode [mol.m-3]": self.initial_concentration_in_positive_electrode,
        #     "Initial temperature [K]": self.initial_temperature,
        # }
