import click


def click_config(func):
    # Envolver la función con las opciones y argumentos del comando
    decorators = [
        click.argument("seed", nargs=1, default=123456),
        click.argument("id_instance", nargs=1, default="NO_NAME"),
        click.argument("id_configuration", nargs=1, default="None"),
        click.command(
            context_settings=dict(ignore_unknown_options=True, allow_extra_args=True),
        ),
        click.option(
            "--result_path",
            default="PYBAMM_RESULTS_PATH",
            help="Negative electrode thickness [m]",
        ),
        click.option(
            "--mode",
            type=click.Choice(["degradation", "not_degradation"], case_sensitive=False),
            help="Operation mode.",
        ),
        click.option(
            "--n_cycle",
            default=0,
            help="Next cycle to compute",
        ),
        click.option(
            "--log_to_file", default=True, type=bool, help="Set true to log to a file"
        ),
        click.option(
            "--base_param_path",
            default=None,
            type=str,
            help="Set this value to use a param file as base parameters",
        ),
        click.option(
            "--save_param",
            default=True,
            type=bool,
            help="Whether to save parameters to a file",
        ),
        click.option(
            "--dataset_path",
            default="EV_DATAPATH",
            help="Path where file with battery data is located",
        ),
        click.option(
            "--inputs_path",
            default="INPUTS_PATH",
            help="Path where state and param",
        ),
        click.option(
            "--verbose",
            default=False,
            type=bool,
            help="Set verbose value  ",
        ),
        click.option(
            "--n_cycles_per_experiments",
            default=10,
            type=int,
            help="Cycles per experiments",
        ),
        click.option(
            "--n_experiments",
            default=10,
            type=int,
            help="Cycles per experiments",
        ),
        click.option("--battery_id", default="W04", help="Separator thickness [m]"),
        click.option(
            "--dataset_id", default="EV", help="Positive electrode thickness [m]"
        ),
        click.option(
            "--negative_current_collector_thickness",
            default=None,
            type=float,
            help="Negative current collector thickness [m]",
        ),
        click.option(
            "--negative_electrode_thickness",
            default=None,
            type=float,
            help="Negative electrode thickness [m]",
        ),
        click.option(
            "--separator_thickness",
            default=None,
            type=float,
            help="Separator thickness [m]",
        ),
        click.option(
            "--positive_electrode_thickness",
            default=None,
            type=float,
            help="Positive electrode thickness [m]",
        ),
        click.option(
            "--positive_current_collector_thickness",
            default=None,
            type=float,
            help="Positive current collector thickness [m]",
        ),
        click.option(
            "--electrode_height", default=None, type=float, help="Electrode height [m]"
        ),
        click.option(
            "--electrode_width", default=None, type=float, help="Electrode width [m]"
        ),
        click.option(
            "--cell_cooling_surface_area",
            default=None,
            type=float,
            help="Cell cooling surface area [m2]",
        ),
        click.option(
            "--cell_volume", default=None, type=float, help="Cell volume [m3]"
        ),
        click.option(
            "--cell_thermal_expansion_coefficient",
            default=None,
            type=float,
            help="Cell thermal expansion coefficient [m.K-1]",
        ),
        click.option(
            "--negative_current_collector_conductivity",
            default=None,
            type=float,
            help="Negative current collector conductivity [S.m-1]",
        ),
        click.option(
            "--positive_current_collector_conductivity",
            default=None,
            type=float,
            help="Positive current collector conductivity [S.m-1]",
        ),
        click.option(
            "--negative_current_collector_density",
            default=None,
            type=float,
            help="Negative current collector density [kg.m-3]",
        ),
        click.option(
            "--positive_current_collector_density",
            default=None,
            type=float,
            help="Positive current collector density [kg.m-3]",
        ),
        click.option(
            "--negative_current_collector_specific_heat_capacity",
            default=None,
            type=float,
            help="Negative current collector specific heat capacity [J.kg-1.K-1]",
        ),
        click.option(
            "--positive_current_collector_specific_heat_capacity",
            default=None,
            type=float,
            help="Positive current collector specific heat capacity [J.kg-1.K-1]",
        ),
        click.option(
            "--negative_current_collector_thermal_conductivity",
            default=None,
            type=float,
            help="Negative current collector thermal conductivity [W.m-1.K-1]",
        ),
        click.option(
            "--positive_current_collector_thermal_conductivity",
            default=None,
            type=float,
            help="Positive current collector thermal conductivity [W.m-1.K-1]",
        ),
        click.option(
            "--nominal_cell_capacity",
            default=None,
            type=float,
            help="Nominal cell capacity [A.h]",
        ),
        click.option(
            "--current_function", default=None, type=float, help="Current function [A]"
        ),
        click.option(
            "--contact_resistance",
            default=None,
            type=float,
            help="Contact resistance [Ohm]",
        ),
        click.option(
            "--negative_electrode_conductivity",
            default=None,
            type=float,
            help="Negative electrode conductivity [S.m-1]",
        ),
        click.option(
            "--maximum_concentration_in_negative_electrode",
            default=None,
            type=float,
            help="Maximum concentration in negative electrode [mol.m-3]",
        ),
        click.option(
            "--negative_electrode_porosity",
            default=None,
            type=float,
            help="Negative electrode porosity",
        ),
        click.option(
            "--negative_electrode_active_material_volume_fraction",
            default=None,
            type=float,
            help="Negative electrode active material volume fraction",
        ),
        click.option(
            "--negative_particle_radius",
            default=None,
            type=float,
            help="Negative particle radius [m]",
        ),
        click.option(
            "--negative_electrode_bruggeman_coefficient_electrolyte",
            default=None,
            type=float,
            help="Negative electrode Bruggeman coefficient (electrolyte),",
        ),
        click.option(
            "--negative_electrode_bruggeman_coefficient_electrode",
            default=None,
            type=float,
            help="Negative electrode Bruggeman coefficient (electrode),",
        ),
        click.option(
            "--negative_electrode_charge_transfer_coefficient",
            default=None,
            type=float,
            help="Negative electrode charge transfer coefficient",
        ),
        click.option(
            "--negative_electrode_double_layer_capacity",
            default=None,
            type=float,
            help="Negative electrode double-layer capacity [F.m-2]",
        ),
        click.option(
            "--negative_electrode_density",
            default=None,
            type=float,
            help="Negative electrode density [kg.m-3]",
        ),
        click.option(
            "--negative_electrode_specific_heat_capacity",
            default=None,
            type=float,
            help="Negative electrode specific heat capacity [J.kg-1.K-1]",
        ),
        click.option(
            "--negative_electrode_thermal_conductivity",
            default=None,
            type=float,
            help="Negative electrode thermal conductivity [W.m-1.K-1]",
        ),
        click.option(
            "--negative_electrode_ocp_entropic_change",
            default=None,
            type=float,
            help="Negative electrode OCP entropic change [V.K-1]",
        ),
        click.option(
            "--positive_electrode_conductivity",
            default=None,
            type=float,
            help="Positive electrode conductivity [S.m-1]",
        ),
        click.option(
            "--maximum_concentration_in_positive_electrode",
            default=None,
            type=float,
            help="Maximum concentration in positive electrode [mol.m-3]",
        ),
        click.option(
            "--positive_electrode_porosity",
            default=None,
            type=float,
            help="Positive electrode porosity",
        ),
        click.option(
            "--positive_electrode_active_material_volume_fraction",
            default=None,
            type=float,
            help="Positive electrode active material volume fraction",
        ),
        click.option(
            "--positive_particle_radius",
            default=None,
            type=float,
            help="Positive particle radius [m]",
        ),
        click.option(
            "--positive_electrode_bruggeman_coefficient_electrolyte",
            default=None,
            type=float,
            help="Positive electrode Bruggeman coefficient (electrolyte),",
        ),
        click.option(
            "--positive_electrode_bruggeman_coefficient_electrode",
            default=None,
            type=float,
            help="Positive electrode Bruggeman coefficient (electrode),",
        ),
        click.option(
            "--positive_electrode_charge_transfer_coefficient",
            default=None,
            type=float,
            help="Positive electrode charge transfer coefficient",
        ),
        click.option(
            "--positive_electrode_double_layer_capacity",
            default=None,
            type=float,
            help="Positive electrode double-layer capacity [F.m-2]",
        ),
        click.option(
            "--positive_electrode_density",
            default=None,
            type=float,
            help="Positive electrode density [kg.m-3]",
        ),
        click.option(
            "--positive_electrode_specific_heat_capacity",
            default=None,
            type=float,
            help="Positive electrode specific heat capacity [J.kg-1.K-1]",
        ),
        click.option(
            "--positive_electrode_thermal_conductivity",
            default=None,
            type=float,
            help="Positive electrode thermal conductivity [W.m-1.K-1]",
        ),
        click.option(
            "--positive_electrode_ocp_entropic_change",
            default=None,
            type=float,
            help="Positive electrode OCP entropic change [V.K-1]",
        ),
        click.option(
            "--separator_porosity",
            default=None,
            type=float,
            help="Porosidad del separador",
        ),
        click.option(
            "--separator_bruggeman_coefficient_electrolyte",
            default=None,
            type=float,
            help="Coeficiente bruggeman del electrolito en el separador",
        ),
        click.option(
            "--separator_density",
            default=None,
            type=float,
            help="Densidad del separador [kg.m-3]",
        ),
        click.option(
            "--separator_specific_heat_capacity",
            default=None,
            type=float,
            help="Capacidad calorífica específica del separador [J.kg-1.K-1]",
        ),
        click.option(
            "--separator_thermal_conductivity",
            default=None,
            type=float,
            help="Conductividad térmica del separador [W.m-1.K-1]",
        ),
        click.option(
            "--initial_concentration_in_electrolyte",
            default=None,
            type=float,
            help="Concentración inicial en el electrolito [mol.m-3]",
        ),
        click.option(
            "--cation_transference_number",
            default=None,
            type=float,
            help="Número de transferencia de cationes",
        ),
        click.option(
            "--thermodynamic_factor",
            default=None,
            type=float,
            help="Factor termodinámico",
        ),
        click.option(
            "--reference_temperature",
            default=None,
            type=float,
            help="Temperatura de referencia [K]",
        ),
        click.option(
            "--total_heat_transfer_coefficient",
            default=None,
            type=float,
            help="Coeficiente total de transferencia de calor [W.m-2.K-1]",
        ),
        click.option(
            "--ambient_temperature",
            default=None,
            type=float,
            help="Temperatura ambiente [K]",
        ),
        click.option(
            "--number_of_electrodes_connected_in_parallel_to_make_a_cell",
            default=None,
            type=float,
            help="Número de electrodos conectados en paralelo para formar una celda",
        ),
        click.option(
            "--number_of_cells_connected_in_series_to_make_a_battery",
            default=None,
            type=float,
            help="Número de celdas conectadas en serie para formar una batería",
        ),
        click.option(
            "--lower_voltage_cut_off",
            default=None,
            type=float,
            help="Corte de voltaje inferior [V]",
        ),
        click.option(
            "--upper_voltage_cut_off",
            default=None,
            type=float,
            help="Corte de voltaje superior [V]",
        ),
        click.option(
            "--open_circuit_voltage_at_0_soc",
            default=None,
            type=float,
            help="Voltaje de circuito abierto al 0% SOC [V]",
        ),
        click.option(
            "--open_circuit_voltage_at_100_soc",
            default=None,
            type=float,
            help="Voltaje de circuito abierto al 100% SOC [V]",
        ),
        click.option(
            "--initial_concentration_in_negative_electrode",
            default=None,
            type=float,
            help="Concentración inicial en el electrodo negativo [mol.m-3]",
        ),
        click.option(
            "--initial_concentration_in_positive_electrode",
            default=None,
            type=float,
            help="Concentración inicial en el electrodo positivo [mol.m-3]",
        ),
        click.option(
            "--initial_temperature",
            default=None,
            type=float,
            help="Temperatura inicial [K]",
        ),
        click.option(
            "--dead_lithium_decay_constant",
            type=float,
            default=None,
            help="Dead lithium decay constant",
        ),
        click.option(
            "--initial_plated_lithium_concentration",
            type=float,
            default=None,
            help="Initial plated lithium concentration",
        ),
        click.option(
            "--lithium_metal_partial_molar_volume",
            type=float,
            default=None,
            help="Lithium metal partial molar volume",
        ),
        click.option(
            "--lithium_plating_kinetic_rate_constant",
            type=float,
            default=None,
            help="Lithium plating kinetic rate constant",
        ),
        click.option(
            "--lithium_plating_transfer_coefficient",
            type=float,
            default=None,
            help="Lithium plating transfer coefficient",
        ),
        click.option(
            "--negative_electrode_lam_constant_exponential_term",
            type=float,
            default=None,
            help="Negative electrode LAM constant exponential term",
        ),
        click.option(
            "--negative_electrode_lam_constant_proportional_term",
            type=float,
            default=None,
            help="Negative electrode LAM constant proportional term",
        ),
        click.option(
            "--negative_electrode_paris_law_constant_b",
            type=float,
            default=None,
            help="Negative electrode paris law constant b",
        ),
        click.option(
            "--negative_electrode_paris_law_constant_m",
            type=float,
            default=None,
            help="Negative electrode paris law constant m",
        ),
        click.option(
            "--negative_electrode_poissons_ratio",
            type=float,
            default=None,
            help="Negative electrode Poisson's ratio",
        ),
        click.option(
            "--negative_electrode_youngs_modulus",
            type=float,
            default=None,
            help="Negative electrode Young's modulus",
        ),
        click.option(
            "--negative_electrode_critical_stress",
            type=float,
            default=None,
            help="Negative electrode critical stress",
        ),
        click.option(
            "--negative_electrode_initial_crack_length",
            type=float,
            default=None,
            help="Negative electrode initial crack length",
        ),
        click.option(
            "--negative_electrode_initial_crack_width",
            type=float,
            default=None,
            help="Negative electrode initial crack width",
        ),
        click.option(
            "--negative_electrode_number_of_cracks_per_unit_area",
            type=float,
            default=None,
            help="Negative electrode number of cracks per unit area",
        ),
        click.option(
            "--negative_electrode_partial_molar_volume",
            type=float,
            default=None,
            help="Negative electrode partial molar volume",
        ),
        click.option(
            "--negative_electrode_reference_concentration_for_free_of_deformation",
            type=float,
            default=None,
            help="Negative electrode reference concentration for free of deformation",
        ),
        click.option(
            "--positive_electrode_lam_constant_exponential_term",
            type=float,
            default=None,
            help="Positive electrode LAM constant exponential term",
        ),
        click.option(
            "--positive_electrode_lam_constant_proportional_term",
            type=float,
            default=None,
            help="Positive electrode LAM constant proportional term",
        ),
        click.option(
            "--positive_electrode_ocp_entropic_change",
            type=float,
            default=None,
            help="Positive electrode OCP entropic change",
        ),
        click.option(
            "--positive_electrode_paris_law_constant_b",
            type=float,
            default=None,
            help="Positive electrode paris law constant b",
        ),
        click.option(
            "--positive_electrode_paris_law_constant_m",
            type=float,
            default=None,
            help="Positive electrode paris law constant m",
        ),
        click.option(
            "--positive_electrode_poissons_ratio",
            type=float,
            default=None,
            help="Positive electrode Poisson's ratio",
        ),
        click.option(
            "--positive_electrode_youngs_modulus",
            type=float,
            default=None,
            help="Positive electrode Young's modulus",
        ),
        click.option(
            "--positive_electrode_active_material_volume_fraction",
            type=float,
            default=None,
            help="Positive electrode active material volume fraction",
        ),
        click.option(
            "--positive_electrode_critical_stress",
            type=float,
            default=None,
            help="Positive electrode critical stress",
        ),
        click.option(
            "--positive_electrode_initial_crack_length",
            type=float,
            default=None,
            help="Positive electrode initial crack length",
        ),
        click.option(
            "--positive_electrode_initial_crack_width",
            type=float,
            default=None,
            help="Positive electrode initial crack width",
        ),
        click.option(
            "--positive_electrode_number_of_cracks_per_unit_area",
            type=float,
            default=None,
            help="Positive electrode number of cracks per unit area",
        ),
        click.option(
            "--positive_electrode_partial_molar_volume",
            type=float,
            default=None,
            help="Positive electrode partial molar volume",
        ),
        click.option(
            "--positive_electrode_reference_concentration_for_free_of_deformation",
            type=float,
            default=None,
            help="Positive electrode reference concentration for free of deformation",
        ),
        click.option(
            "--typical_plated_lithium_concentration",
            type=float,
            default=None,
            help="Typical plated lithium concentration",
        ),
    ]

    for decorator in reversed(decorators):
        func = decorator(func)

    return func