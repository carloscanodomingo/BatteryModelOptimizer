import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
import pybamm
from core.utils import PybammOutput


@dataclass
class HyperparameterDatabase:
    hyperparameters: Dict[str, float]


@dataclass
class Experiments:
    init: pybamm.Experiment
    main: pybamm.Experiment
    end: pybamm.Experiment
    capacity: pybamm.Experiment


def SoC_termination(threshold):
    SoC_init = 1

    def SoC(variables):
        return (SoC_init - variables["SoC"]) - threshold

    return pybamm.step.CustomTermination(
        name=f"State of Charge Threshold {threshold}", event_function=SoC
    )


class PyBammSol:
    solution: pybamm.Solution
    n_cycle = 0


# This serves as a conceptual contract, not for direct inheritance.
class BaseBatteryID(Enum):
    # Define expected behavior or values here
    # Example: ID1 = auto(), ID2 = auto()
    pass


class DatasetID(Enum):
    Dataset_EV = 1
    Dataset_Not_Valid = 2

    @classmethod
    def get_dataset_id(cls, database_string_id):
        if database_string_id == "EV":
            return DatasetID.Dataset_EV
        else:
            return DatasetID.Dataset_Not_Valid


class AbstractBaseDataset(ABC):
    def __init__(self, results_path, dataset_path, instance_id, battery_id):
        self.results_path = results_path
        self.dataset_path = dataset_path
        self.instance_id = instance_id
        self.battery_id = battery_id
        logging.info(f"battery_id { battery_id}")

    @abstractmethod
    def setup_experiment(self) -> Experiments:
        """
        Set up experiment specifics such as parameters and initial conditions.
        """
        pass

    @abstractmethod
    def run(self):
        """
        Run the experiment simulation and return results.
        """
        pass

    @abstractmethod
    def save_results(self, output: PybammOutput, n_cycle):
        """
        Analyze the results of the simulation and compare with experimental data.
        """
        pass

    @abstractmethod
    def get_metric_non_degradation(
        self, output: PybammOutput, n_cycle
    ) -> Optional[float]:
        """
        Analyze the results of the simulation and compare with experimental data.
        """
        pass

    @abstractmethod
    def get_metric_capacity_experiment(
        self, output: PybammOutput, n_cycle
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Analyze the results of the simulation and compare with experimental data.
        """
        pass

    @abstractmethod
    def get_metric_degradation(self, output: PybammOutput, n_cycle) -> Optional[float]:
        """
        Analyze the results of the simulation and compare with experimental data.
        """
        pass
