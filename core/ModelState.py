import logging
import os
import pickle
from dataclasses import dataclass
from pathlib import Path

import h5py
import pybamm
from core.ModelInfo import ArrayPybammMetrics, PybammInfo
from core.utils import PybammOutput, get_base_path


def get_state_path(id_battery, id_configuration) -> str:
    path = f"{get_base_path(id_battery, id_configuration)}_state.WPs"
    return path


@dataclass
class StateModel:
    first_pybamm_output: PybammOutput
    last_ModelState: pybamm.Solution
    array_pybamm_metric: ArrayPybammMetrics = ArrayPybammMetrics()

    def add_solution(self, output, last_state, cycle, info: PybammInfo):
        self.array_pybamm_metric[cycle] = info
        self.last_ModelState = last_state
        if cycle == 0:
            self.first_pybamm_output = output

    def __len__(self):
        return len(self.array_pybamm_metric)

    def __getitem__(self, index) -> PybammInfo:
        return self.array_pybamm_metric[index]

    def metric_calculated(self):
        return len(self.array_pybamm_metric)

    def save_state(self, state_path):
        logging.info(f"Save state in file {state_path}")
        with open(state_path, "wb") as file_handle:
            pickle.dump(self, file_handle)
        df = self.array_pybamm_metric.to_dataframe()
        df.to_csv(f"{state_path}_.csv")
        # with h5py.File(f"{state_path}h5", "w") as h5file:
        #     pickle.dump(self, file_handle)

    @staticmethod
    def read_state(state_path):
        state_file = Path(state_path)
        if state_file.exists():
            logging.info(f"State file exists in {state_path}")
            with state_file.open("rb") as file:
                return pickle.load(file)
        else:
            logging.info(f"Not State file found in {state_path}")
            return None
