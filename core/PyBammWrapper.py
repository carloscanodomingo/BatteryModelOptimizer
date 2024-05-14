import logging
import os
from dataclasses import InitVar, dataclass, field
from enum import Enum
from typing import Optional

import pybamm
from core.DatasetBase import AbstractBaseDataset, DatasetID, Experiments
from core.ModelInfo import ModelMetrics, ModelStatus, PybammInfo
from core.ModelParameters import ModelParameters
from core.ModelState import StateModel
from core.utils import PybammOutput
from databases.DatasetEV import DatasetEV

# os.environ["OPENBLAS_NUM_THREADS"] = "1"


class SimFailedException(Exception):
    pass


class ExperimentError(Exception):
    """Exception raised when an experiment fails."""

    def __init__(self, message="Experiment failed"):
        self.message = message
        super().__init__(self.message)


class TypeSolver(Enum):
    deltaC = 1
    Discharge = 2


@dataclass
class PyBammWrapper:
    """
    A wrapper class for setting up and running PyBaMM simulations with specific model configurations,
    experiments, and parameters.

    Attributes:
        model_parameters (InitVar[ModelParameters]): Model parameters passed during initialization.
        param (pybamm.ParameterValues): Parameters for the PyBaMM simulation.
        model (pybamm.BaseModel): The PyBaMM model to be used for simulations.
        dataset (AbstractBaseDataset): The dataset to be used in the simulation setup.
        experiments (Experiments): The experimental setup for the simulation.
        state (Optional[StateModel]): The initial state of the model, if any.
        id_configuration (str): Identifier for the configuration.
        seed (str): Seed value for random number generation in simulations.
        degradation (bool): Indicates if degradation effects are considered in the model.
        var_pts (Optional[dict]): Variable points for the simulation discretization.
        solver (Optional[pybamm.BaseSolver]): Solver to be used for the simulation.
        success (bool): Flag indicating if the simulation ran successfully.
        n_cycles_per_experiments (int): Number of cycles per experiment.
        dataset_path (Optional[str]): Path to the dataset.
        state_path (Optional[str]): Path to the model state.
        result_path (Optional[str]): Path for saving simulation results.
        instance_id (Optional[str]): Instance identifier.
        dataset_id (Optional[DatasetID]): Enum specifying the dataset ID.
        id_battery (Optional[str]): Identifier for the battery model.
    """

    # Paths and identifiers
    dataset_path: str
    state_path: str
    result_path: str
    instance_id: str
    id_dataset: DatasetID
    id_battery: str
    # Model and simulation parameters
    max_discharge: float = field(init=False)
    min_discharge: float = field(init=False)
    model_parameters: InitVar[ModelParameters]
    param: pybamm.ParameterValues = field(init=False)
    model: pybamm.BaseModel = field(init=False)
    dataset: AbstractBaseDataset = field(init=False)
    experiments: Experiments = field(init=False)
    state: StateModel = field(init=False)
    id_configuration: str
    seed: str
    degradation: bool = field(init=False)
    var_pts: Optional[dict] = None
    solver: Optional[pybamm.BaseSolver] = None
    success: bool = True
    state

    def __post_init__(self, model_parameters):
        """
        Post-initialization method to setup dataset, model parameters, solver configuration,
        and custom variables after the dataclass has been initialized.
        """

        self.initialize_dataset()
        self.experiments = self.dataset.setup_experiment()
        self.initialize_param_and_model(model_parameters)
        self.model_callback = self.ExperimentCallback(self)
        self.configure_solver_and_varpts()
        self.add_custom_variables()

    def initialize_state(self):
        state = self.read_state()
        if state is None:
            logging.info("Running initialization experiment.")
            initial_state = self.initialize_experiment()
            if initial_state is None:  # Checks if initialization was unsuccessful
                raise ExperimentError(
                    "Initial experiment fail"
                )  # Error already logged in initialize_experiment()
            state = initial_state
        return state
        self.state = state
        # self.update_discharge_capacity()

    def get_metrics_capacity(self, cycle) -> Optional[float]:
        sol = self.run_test_capacity()
        if sol is None:
            return None
        metrics = self.dataset.get_metric_capacity_experiment(
            PybammOutput(sol), n_cycle=cycle
        )
        return metrics

    def get_real_capacity(self, output_capacity):
        df_capacity_test = output_capacity.df
        discharge_vector = df_capacity_test[df_capacity_test["Step"] == 4][
            "Dis"
        ].to_numpy()
        return discharge_vector.max() - discharge_vector.min()

    def update_discharge_capacity(self, output_capacity):
        df_capacity_test = PybammOutput(output_capacity).df
        discharge_vector = df_capacity_test[df_capacity_test["Step"] == 4][
            "Dis"
        ].to_numpy()
        min_discharge = discharge_vector[0]
        max_discharge = discharge_vector[-1]

        logging.info(f"min discharge { min_discharge}- max_discharge {max_discharge}")
        self.__add_variables(
            "SoC",
            (self.model.variables["Discharge capacity [A.h]"] - min_discharge)
            / (max_discharge - min_discharge),
        )
        #     # - self.min_discharge / (self.max_discharge - self.min_discharge),
        # )

    def update_state(self):
        state = self.read_state()
        if state is not None:
            self.state = state

    def initialize_dataset(self):
        """
        Initializes the dataset based on the dataset ID. Currently, only supports 'Dataset_EV'.
        """
        if not os.path.exists(self.dataset_path):
            logging.error(f"Dataset file {self.dataset_path} does not exist.")
            raise FileNotFoundError(f"Dataset file {self.dataset_path} does not exist.")

        self.id_dataset = DatasetID.get_dataset_id(self.id_dataset)

        if self.id_dataset.value == DatasetID.Dataset_EV.value:
            self.dataset = DatasetEV(
                dataset_path=self.dataset_path,
                results_path=self.result_path,
                instance_id=self.instance_id,
                battery_id=DatasetEV.get_battery_by_name(self.id_battery),
            )
        else:
            logging.error(f"Not Valid dataset id {self.id_dataset.value}")
            raise KeyError(f"Not Valid dataset id {self.id_dataset.value}")

    def initialize_param_and_model(self, model_parameters: ModelParameters):
        """
        Initializes the simulation parameters and selects the appropriate model based on the presence of degradation.
        """
        # Placeholder for parameter values - consider making this configurable
        param = pybamm.ParameterValues("OKane2022")
        self.degradation = model_parameters.degradation_parameters is not None
        logging.info(f"Mode degradation: {self.degradation}")
        self.param = model_parameters.update_param(param)
        self.model = self.select_model_based_on_degradation()

    def select_model_based_on_degradation(self):
        """
        Selects the simulation model. Returns a non-degradation model by default and a degradation model if applicable.
        """
        base_config = {"calculate discharge energy": "true"}
        if not self.degradation:
            return pybamm.lithium_ion.DFN(base_config)
        else:
            degradation_config = {
                "SEI": "solvent-diffusion limited",
                "SEI porosity change": "true",
                "lithium plating": "partially reversible",
                "lithium plating porosity change": "true",
                "particle mechanics": ("swelling and cracking", "swelling only"),
                "SEI on cracks": "true",
                "loss of active material": "stress-driven",
            }
            return pybamm.lithium_ion.DFN({**base_config, **degradation_config})

    def configure_solver_and_varpts(self):
        """
        Configures the solver with predefined accuracy and variable points for the simulation discretization.
        """
        if self.degradation:
            tolerance = 1e-6
        else:
            tolerance = 1e-4
        atol, rtol = tolerance, tolerance  # Absolute and relative tolerances
        self.solver = pybamm.CasadiSolver(atol=atol, rtol=rtol, mode="safe")
        # options = {
        #     # Number of threads available for OpenMP
        #     "num_threads": 10,
        # }
        # self.solver = pybamm.IDAKLUSolver(atol=atol, rtol=rtol, options=options)
        # Discretization points
        self.var_pts = {
            "x_n": 5,  # negative electrode
            "x_s": 5,  # separator
            "x_p": 5,  # positive electrode
            "r_n": 30,  # negative particle
            "r_p": 30,  # positive particle
        }

    def read_state(self):
        """
        Reads the initial state of the model, if available.
        """
        # Assumes implementation of read_state elsewhere
        return StateModel.read_state(self.state_path)

    def add_custom_variables(self):
        """
        Adds custom variables to the model, such as State of Charge (SoC).
        """
        self.min_discharge = 0
        self.max_discharge = self.param["Nominal cell capacity [A.h]"]
        self.__add_variables(
            "Current_capacity [A.h]",
            self.param["Nominal cell capacity [A.h]"],
        )
        # self.model.variables["min_discharge"] = pybamm.surf(
        #     pybamm.Variable("min_discharge")
        # )
        # self.__add_variables(
        #     "SoC",
        #     self.model.variables["Discharge capacity [A.h]"]
        #     - self.model.variables["min_discharge"]
        #     / (self.max_discharge - self.min_discharge),
        #     # - self.min_discharge / (self.max_discharge - self.min_discharge),
        # )

    def __len_metrics__(self):
        return len(self.state.array_pybamm_metric)

    def __add_variables(self, name_variable, variable):
        self.model.variables[name_variable] = variable

    class ExperimentCallback(pybamm.callbacks.Callback):
        def __init__(self, wrap_instance):
            super().__init__()
            self.wrap_instance = wrap_instance

        def on_experiment_error(self, logs):
            self.wrap_instance.success = False

        def on_experiment_infeasible(self, logs):
            self.wrap_instance.success = False

    def run_experiment(self, last_state, experiment, initial_soc):
        """
        Runs a battery simulation experiment with specified initial conditions and experiment protocol.

        Utilizes the model, parameters, and solver already configured in the class to execute the simulation.
        Allows continuation from a previous state and setting an initial state of charge (SoC).

        Parameters:
        - last_state: Previous simulation's final state, or None to start fresh.
        - experiment: PyBaMM experiment object defining the simulation protocol.
        - initial_soc: Starting state of charge as a fraction (e.g., 0.8 for 80%).

        Returns:
        The simulation result as a pybamm.Solution object.
        """
        sim = pybamm.Simulation(
            self.model,
            parameter_values=self.param,
            experiment=experiment,
            var_pts=self.var_pts,
            solver=self.solver,
        )
        new_solution = sim.solve(
            callbacks=self.model_callback,
            starting_solution=last_state,
            initial_soc=initial_soc,
            calc_esoh=False
        )
        return new_solution

    def run_test_capacity(self):
        return self.run_experiment(
            experiment=self.experiments.capacity,
            last_state=self.state.last_ModelState,
            initial_soc=1,
        )

    def run_pybamm(self, cycle):
        """
        Runs a PyBaMM simulation for a specific cycle, handling initial setup if necessary.

        If the state has not been initialized, it runs an initialization experiment. It then
        checks whether the requested cycle has already been calculated and, if not, proceeds
        to run the main experiment for the specified cycle. This method also handles
        logging and error checking throughout the process.

        Parameters:
        - cycle (int): The target simulation cycle number.

        Returns:
        - The relevant metric output for the specified cycle, or None if an error occurs
          during the simulation or metric extraction.
        """
        # Initialize state with the first experiment if it doesn't exist

        # Return calculated metric if cycle is already simulated
        if cycle < len(self.state):
            logging.info("Requested cycle has already been simulated.")
            return self.extract_metric(
                cycle
            )  # Adjusted to use extract_metric for consistency
        elif cycle > len(self.state):  # Changed to >= for correct boundary condition
            logging.error(
                f"Invalid cycle requested: {cycle}. Last cycle: {len(self.state) - 1}."
            )
            return None
        # Run main experiment for the current cycle
        # if not self.update_discharge_capacity():
        #     return None

        if not self.run_main_experiment(cycle):
            return None  # Errors logged in run_main_experiment()

        logging.info(f"Finishing Simulation with metrics len {len(self.state)}")
        # Extract and return the appropriate metric
        return self.extract_metric(cycle)

    def initialize_experiment(self) -> Optional[StateModel]:
        """
        Initializes the simulation state by running an initial experiment.

        Returns:
        - StateModel if the initialization succeeded, otherwise False.
        """
        solution = self.run_experiment(
            experiment=self.experiments.init, last_state=None, initial_soc=1
        )
        self.log_time_sol(solution)
        if not self.success:
            logging.error("Error occurred during the initialization experiment.")
            return None

        return StateModel(solution, solution.last_state)

    def run_capacity_experiment(self, output_capacity, cycle):
        return self.dataset.get_metric_capacity_experiment(output_capacity, cycle)

    def run_main_experiment(self, cycle):
        """
        Runs the main experiment for the given cycle and updates the state.

        Parameters:
        - cycle (int): The cycle number to run the main experiment for.

        Returns:
        - bool: True if the experiment ran successfully, False otherwise.
        """
        sol_capacity = self.run_test_capacity()
        if sol_capacity is None:
            return None
        self.update_discharge_capacity(sol_capacity)
        logging.info("Updated discharge capacity")

        solution = self.run_experiment(
            experiment=self.experiments.main,
            last_state=self.state.last_ModelState,
            initial_soc=None,
        )
        if not self.success:
            logging.error("Error running main experiment.")
            return False

        self.log_time_sol(solution)
        self.update_state_with_solution(solution, sol_capacity, cycle)
        return True

    def update_state_with_solution(self, solution, solution_capacity, cycle):
        """
        Updates the simulation state with the results from the latest experiment.

        Parameters:
        - solution: The solution object from the latest PyBaMM simulation.
        - cycle (int): The cycle number of the simulation.
        """
        output = PybammOutput(solution)
        output_capacity = PybammOutput(solution_capacity)
        info = self.get_info(output, output_capacity, cycle)
        logging.info(info)
        if info is None:
            logging.error("Failed to obtain metrics from the solution.")
            self.success = False
            return

        logging.info(f"State metric len START {len(self.state)}")

        self.state.add_solution(
            output=output, last_state=solution.last_state, cycle=cycle, info=info
        )
        self.state.save_state(state_path=self.state_path)
        logging.info(f"State metric len END {len(self.state)}")
        self.param

    def extract_metric(self, cycle):
        """
        Extracts the relevant metric from the state for the given cycle, considering whether
        degradation effects are taken into account.

        Parameters:
        - cycle (int): The cycle number to extract metrics for.

        Returns:
        - The appropriate metric output for the cycle, considering degradation, or None if an error occurs.
        """
        if self.state is None:
            raise ValueError("Metrics Not found in state")
        metrics = self.state[cycle].model_metrics
        return (
            metrics.degradation_metrics
            if self.degradation
            else metrics.non_degradation_metric
        )

    def get_info(self, output, output_capacity, cycle) -> Optional[PybammInfo]:
        if self.dataset is not None:
            non_degradation_metric = self.dataset.get_metric_non_degradation(
                output, cycle
            )
            degradation_metric = self.dataset.get_metric_degradation(output, cycle)
            (capacity_metric, experimental_capacity) = self.run_capacity_experiment(
                output_capacity, cycle
            )
            model_metrics = ModelMetrics(
                non_degradation_metric=non_degradation_metric,
                degradation_metrics=degradation_metric,
                capacity_metric=capacity_metric,
                experimental_capacity=experimental_capacity,
            )
        else:
            model_metrics = ModelMetrics()

        capacity_value = self.get_real_capacity(output_capacity)
        model_status = ModelStatus(real_capacity=capacity_value)
        return PybammInfo(model_metrics=model_metrics, model_status=model_status)

    @staticmethod
    def log_time_sol(sol):
        logging.info(
            f"took {sol.solve_time} " + f"(integration time: {sol.integration_time})"
        )
