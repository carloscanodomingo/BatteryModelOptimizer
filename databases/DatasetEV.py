import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pybamm
from core.DatasetBase import AbstractBaseDataset, Experiments, SoC_termination
from core.utils import PybammOutput
from scipy.integrate import trapz
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit

rsquared_thresshold = 0.6
TO_PLOT = False
MAX_METRIC_VALUE = 10


@dataclass
class ResultFit:
    rsquared: float
    parameters: Dict[str, float]


class BatteryIDEV(Enum):
    W03 = 1
    W04 = 2
    W05 = 3
    W07 = 4
    W09 = 5
    W08 = 6
    W10 = 7
    G01 = 8
    V04 = 9
    V05 = 10


class DatasetEV(AbstractBaseDataset):
    def setup_experiment(self):
        # Implementation specific to Experiment1
        return self.define_experiment()

    def run(self):
        # Implementation specific to Experiment1
        # Simulate some results
        return {"data": "Results from Experiment 1"}

    def save_results(self, output: PybammOutput, n_cycle):
        """
        Analyze the results of the simulation and compare with experimental data.
        """
        self.write_cycles_to_hdf5(output.df)
        pass

    def get_metrics_hyperparameters(
        self, solution: pybamm.Solution, n_cycle
    ) -> np.double:
        return np.double(0.0)

    def get_metric_non_degradation(
        self, output: PybammOutput, n_cycle
    ) -> Optional[float]:
        """
        Analyze the results of the simulation and compare with experimental data.
        """
        discharge_cap = self.__metric_discharge_capacity__(
            n_cycle=n_cycle, output=output
        )
        rmse = self.__metric_rmse__(cycle_number=n_cycle, output=output)
        linear = self.__metric_linear__(n_cycle, output)
        logging.info(
            f"Non degradation metrics: Dischar {discharge_cap}, RMSE {rmse} & linear {linear}"
        )
        return (discharge_cap + rmse + linear) / 3

    def get_metric_capacity_experiment(
        self, output, n_cycle
    ) -> Tuple[Optional[float], Optional[float]]:
        results = self.__metric_total_capacity__(n_cycle, output)
        return results

    def get_metric_degradation(self, output: PybammOutput, n_cycle) -> Optional[float]:
        """
        Analyze the results of the simulation and compare with experimental data.
        """
        discharge_cap = self.__metric_discharge_capacity__(
            n_cycle=n_cycle, output=output
        )
        integral = self.__metric_integral__(cycle_number=n_cycle, output=output)
        linear = self.__metric_linear__(n_cycle, output)
        logging.info(
            f"Degradation metrics: Dischar {discharge_cap}, linear {integral} & linear {linear}"
        )
        return (discharge_cap + integral + linear) / 3

    def define_experiment(self):
        initial_exp = pybamm.Experiment(
            [
                "Rest for 4 hours (5 minute period)",
                "Discharge at 0.5C until 3.5 V",
            ]
        )
        n_ussd = 40
        df_alt_current_profile = pd.read_csv("udds_current.csv")
        df_alt_current_profile = pd.concat(
            [df_alt_current_profile] * n_ussd, ignore_index=True
        )

        udds_current_profile = np.column_stack(
            [df_alt_current_profile.index, -df_alt_current_profile.C]
        )
        main_exp = pybamm.Experiment(
            [
                (
                    self.get_charge_string(),
                    "Hold at 4 V until 50 mA",
                    "Charge at C/4 until 4.2 V",
                    "Hold at 4.2 V until 50 mA",
                    pybamm.step.c_rate(0.25, termination=SoC_termination(0.8)),
                    pybamm.step.current(
                        udds_current_profile, termination=SoC_termination(0.2)
                    ),
                )
            ]
        )
        end_exp = pybamm.Experiment(
            [("Discharge at 0.1C until 2.5 V (5 minute period)")]
        )
        capacity_exp = pybamm.Experiment(
            [
                (
                    "Discharge at C/10 until 2.5V",
                    "Charge at 1C until 4.199 V",
                    "Hold at 4.2 V until 50 mA",
                    "Rest for 30 minutes",
                    "Discharge at C/10 until 2.5V",
                    "Rest for 30 minutes",
                )
            ]
        )

        return Experiments(
            init=initial_exp, main=main_exp, end=end_exp, capacity=capacity_exp
        )

    def get_charge_string(self) -> str:
        charge_map = {
            BatteryIDEV.W03: "Charge at 3C until 4 V",
            BatteryIDEV.W04: "Charge at C/4 until 4 V",
            BatteryIDEV.W05: "Charge at C/2 until 4 V",
            BatteryIDEV.W07: "Charge at C/4 until 4 V",
            BatteryIDEV.W08: "Charge at C/2 until 4 V",
            BatteryIDEV.W09: "Charge at 1C until 4 V",
            BatteryIDEV.W10: "Charge at 3C until 4 V",
            BatteryIDEV.G01: "Charge at 3C until 4 V",
            BatteryIDEV.V04: "Charge at C/4 until 4 V",
            BatteryIDEV.V05: "Charge at 1C until 4 V",
        }
        # Default charge string if battery_id is not in charge_map
        return charge_map.get(
            BatteryIDEV(self.battery_id.value), "Unknown charge string"
        )

    @staticmethod
    def get_battery_by_name(name):
        return BatteryIDEV[name]

    def write_cycles_to_hdf5(self, df_result):
        """
        Writes each cycle's data from a DataFrame to an HDF5 file, under separate keys.

        Parameters:
        - df: pandas DataFrame containing the data.
        - unique_id_column: String name of the column in df that contains a unique identifier for all cycles.
        - filepath: Path to the HDF5 file to write the data to.
        """
        # Open the HDF5 file in append mode
        datapath = self.dataset_path
        # with pd.HDFStore(self.results_path, mode="a") as store:
        # Iterate over each cycle in the new data
        for cycle in df_result["Cycle"].unique():
            cycle_data = df_result[df_result["Cycle"] == cycle]
            key = f"/{self.battery_id.name}_Cycle{int(cycle):04d}"

            # Append this cycle's data to the file
            cycle_data.to_hdf(self.results_path, key=key, mode="a")

    def get_df_capacity_test(self, cycle_number: int) -> Optional[pd.DataFrame]:
        if not os.path.exists(self.dataset_path):
            logging.error(f"File {self.dataset_path} does not exist.")
            return None

        key = f"/CapTest_{self.battery_id.name}_Cycle{cycle_number:04d}"

        try:
            with h5py.File(self.dataset_path, "r") as file:
                if key not in file:
                    logging.info(
                        f"Capacity test data {key} does not exist in the file."
                    )
                    return None

                # Directly creating DataFrame from the arrays
                df = pd.DataFrame(
                    {
                        "Cap": file[key]["Cap"][:].squeeze(),
                        "T": file[key]["T"][:].squeeze(),
                        "C": file[key]["C"][
                            :
                        ].squeeze(),  # Assuming the negation is needed
                        "V": file[key]["V"][:].squeeze(),
                    }
                )

                return df
        except KeyError:
            logging.warning(f"Data for {key} not found in the file.")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

        return None

    def get_df_experimental(self, cycle_number: int) -> Optional[pd.DataFrame]:
        """
        Reads and returns the DataFrame of a specific cycle from an HDF5 file.

        Parameters:
        - battery_id: String representing the battery ID.
        - path: Path to the HDF5 file from which to read the data.
        - cycle_number: Integer representing the cycle number to read.

        Returns:
        - A pandas DataFrame containing the data for the specified cycle, or None if the file or cycle data does not exist.
        """

        if not os.path.exists(self.dataset_path):
            logging.error(f"File {self.dataset_path} does not exist.")
            return None

        key = f"/{self.battery_id.name}_Cycle{cycle_number:04d}"

        try:
            with h5py.File(self.dataset_path, "r") as file:
                if key not in file:
                    logging.warning(f"Cycle data {key} does not exist in the file.")
                    return None

                # Directly creating DataFrame from the arrays
                df = pd.DataFrame(
                    {
                        "Cap": file[key]["C_cap"][:].squeeze(),
                        "relative_time": file[key]["relative_time"][:].squeeze(),
                        "Step": file[key]["Step"][:].squeeze(),
                        "C": file[key]["C"][
                            :
                        ].squeeze(),  # Assuming the negation is needed
                        "V": file[key]["V"][:].squeeze(),
                    }
                )

                return df
        except KeyError:
            logging.warning(f"Data in {key} not valid.")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

        return None

    def __metric_total_capacity__(self, n_cycle, output):
        df_exp = self.get_df_capacity_test(n_cycle)
        if df_exp is None:
            return None, None
        cap_real = df_exp["Cap"].max() - df_exp["Cap"].min()
        df_sim = output.df
        df_sim = df_sim[df_sim.Step == 4]
        df_sim["Cap"] = df_sim.Dis - df_sim.Dis.min()
        interp_points = 1000
        min_cap = max(df_sim["Cap"].min(), df_exp["Cap"].min())
        max_cap = min(df_sim["Cap"].max(), df_exp["Cap"].max())
        trunc_time = np.linspace(min_cap, max_cap, interp_points)
        # Interpolation over the common time vector
        interp_EV = interp1d(
            df_exp["Cap"],
            df_exp["V"],
            bounds_error=False,
            fill_value="extrapolate",
        )
        interp_PB = interp1d(
            df_sim["Cap"],
            df_sim["V"],
            bounds_error=False,
            fill_value="extrapolate",
        )

        var_intrp_exp = interp_EV(trunc_time)
        var_intrp_sim = interp_PB(trunc_time)
        df = pd.DataFrame(
            {"Sim": var_intrp_sim, "Exp": var_intrp_exp}, index=trunc_time
        )
        calc_rmse = np.sqrt(
            np.mean((np.abs(var_intrp_sim) - np.abs(var_intrp_exp)) ** 2)
        )
        return calc_rmse, cap_real

    def __metric_discharge_capacity__(self, n_cycle, output) -> float:
        df_exp = self.get_df_experimental(n_cycle)
        if df_exp is None:
            return MAX_METRIC_VALUE

        exp_start = df_exp[df_exp.Step == 4]["Cap"].min()
        exp_end = df_exp[df_exp.Step == 5]["Cap"].max()
        exp_cap = exp_end - exp_start

        df_sim = output.df
        cap_start = df_sim[df_sim.Step == 4]["Dis"].min()
        cap_end = df_sim[df_sim.Step == 5]["Dis"].max()
        sim_cap = cap_end - cap_start
        logging.info(f"Capacity sim {sim_cap} - exp {exp_cap}")
        return np.sqrt((sim_cap - exp_cap) ** 2)

    def __metric_linear__(self, cycle_number: int, output: PybammOutput) -> float:
        df_experimental = self.get_df_experimental(cycle_number)
        df_simulated = output.df
        linear_metric = get_fit_linear_metric(
            df_experimental, df_simulated, to_plot=TO_PLOT
        )
        return linear_metric

    def __metric_rmse__(self, cycle_number, output) -> float:
        df_experimental = self.get_df_experimental(cycle_number)
        df_simulated = output.df
        if df_experimental is None or df_simulated is None:
            return MAX_METRIC_VALUE
        correct_results = 0
        step_vars = [(1, "C"), (2, "V"), (3, "C"), (4, "V")]
        results = 0.0
        for index, var in step_vars:
            result = calc_error_non_degradation(
                df_experimental, df_simulated, index, var
            )
            if result is None:
                return MAX_METRIC_VALUE
            results += result
            correct_results += 1
        if correct_results == 0:
            return MAX_METRIC_VALUE
        else:
            return results / correct_results

    def __metric_integral__(self, cycle_number, output) -> float:
        df_experimental = self.get_df_experimental(cycle_number)
        df_simulated = output.df
        integral_metric = 0
        integral_metric += get_integral_value(df_experimental, df_simulated, 1) * 2
        integral_metric += get_integral_value(df_experimental, df_simulated, 2) * 0.5
        integral_metric += get_integral_value(df_experimental, df_simulated, 3) * 2
        integral_metric += get_integral_value(df_experimental, df_simulated, 4) * 0.5
        return integral_metric / 5


def get_integral_value(df_experimental, df_simulated, step, to_plot=TO_PLOT):
    df_exp_filtered = df_experimental[df_experimental["Step"] == step].copy()
    df_exp_filtered.loc[:, "relative_time"] = (
        df_exp_filtered["relative_time"] - df_exp_filtered["relative_time"].min()
    )
    df_sim_filtered = df_simulated[df_simulated["Step"] == step].copy()
    df_sim_filtered.loc[:, "relative_time"] = (
        df_sim_filtered["relative_time"] - df_sim_filtered["relative_time"].min()
    )

    AUC_experimental = abs(
        trapz(abs(df_exp_filtered["C"]), df_exp_filtered["relative_time"])
    )
    AUC_simulated = abs(
        trapz(abs(df_sim_filtered["C"]), df_sim_filtered["relative_time"])
    )

    if to_plot:
        # Datos experimentales
        plt.plot(
            df_exp_filtered["relative_time"],
            (df_exp_filtered["C"]),
            label=f"Experimental (AUC={AUC_experimental:.2f})",
            color="blue",
        )

        # Datos simulados
        plt.plot(
            df_sim_filtered["relative_time"],
            (df_sim_filtered["C"]),
            label=f"Simulated (AUC={AUC_simulated:.2f})",
            color="red",
        )

        # Mejorar el gráfico
        plt.title("Experimental vs Simulated Data")
        plt.xlabel("Relative Time")
        plt.ylabel("Absolute C")
        plt.legend()
        plt.grid(True)

        # Mostrar el gráfico
        plt.show()
    return 2 * abs(AUC_experimental - AUC_simulated) / AUC_experimental


def get_fit_linear_metric(df_experimental, df_simulated, to_plot=TO_PLOT):
    fit_result_exp = fit_udds_profile_linear(df_experimental, to_plot)
    fit_result_sim = fit_udds_profile_linear(df_simulated, to_plot)
    if (
        fit_result_sim.rsquared < rsquared_thresshold
        or fit_result_exp.rsquared < rsquared_thresshold
    ):
        fit_linear_metric = MAX_METRIC_VALUE
    else:
        slope_sim = abs(fit_result_sim.parameters["a"])
        slope_exp = abs(fit_result_exp.parameters["a"])
        logging.debug(f"Slope sim {slope_sim} - slope_exp {slope_exp}")
        fit_linear_metric = abs((slope_sim - slope_exp) / 0.1)
    return fit_linear_metric


def fit_udds_profile_linear(df, to_plot=TO_PLOT):
    # Filtrar el DataFrame
    step_ussd = 5
    # Filter data by step
    selected_df = df[df["Step"] == step_ussd].copy()
    selected_df.loc[:, "relative_time"] = (
        selected_df["relative_time"] - selected_df["relative_time"].min()
    )

    # Extraer datos
    x = selected_df["relative_time"].values
    V = selected_df["V"].values
    C = selected_df["C"].values

    # Definir el modelo personalizado
    def custom_model(x_I, a, b, k):
        x, I = x_I
        return a * x + b + k * I

    # Ajustar el modelo
    try:
        popt, pcov = curve_fit(custom_model, (x, C), V, maxfev=10000)

        V_fit = custom_model((x, C), *popt)
        # Calcular R^2
        ss_res = np.sum((V - V_fit) ** 2)
        ss_tot = np.sum((V - np.mean(V)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        result_fit = ResultFit(
            rsquared=r_squared, parameters={"a": popt[0], "b": popt[1], "k": popt[2]}
        )
        if to_plot:
            # Graficar los datos originales y el ajuste
            plt.figure()
            plt.plot(x, custom_model((x, C), *popt), "--r", label="V Fit")
            plt.plot(x, V, "-b", label="V Original")
            plt.legend()
            plt.xlabel("x")
            plt.ylabel("V")
            plt.title("Polynomial Fit of V = a*x + b + k*I - p * x^-n")
            plt.show()
    except Exception as e:
        logging.error(f"Linear Fit Error {e}")
        result_fit = ResultFit(rsquared=0, parameters={})

    # Mostrar los coeficientes
    return result_fit


def calc_error_non_degradation(
    df_experimental: pd.DataFrame,
    df_simulated: pd.DataFrame,
    step: int,
    var: str,
    to_plot: bool = TO_PLOT,
    interp_points: int = 100,
) -> Optional[float]:
    """
    Calculate the RMSE error between electric vehicle data and PyBamm simulation data, or return None if data is insufficient.

    Parameters:
    - df_experimental: DataFrame containing the experimental data.
    - df_simulated: DataFrame containing the PyBamm simulation data.
    - step: Specific step for analysis.
    - var: Variable to analyze ('C' or 'V').
    - to_plot: If True, plots the curves of EV and PB data.
    - interp_points: Number of points for interpolation.

    Returns:
    - Normalized RMSE for the specified variable across the given step, or None if data is insufficient.
    """

    # Check if DataFrames are empty or do not contain the specified step
    if df_experimental.empty or df_simulated.empty:
        logging.info("One of the DataFrames is empty.")
        return None
    if (
        step not in df_experimental["Step"].values
        or step not in df_simulated["Step"].values
    ):
        logging.info("The specified step does not exist in one of the DataFrames.")
        return None
    if var not in df_experimental.columns or var not in df_simulated.columns:
        logging.info("The specified variable does not exist in one of the DataFrames.")
        return None

    # Filter data by step
    df_exp = df_experimental[df_experimental["Step"] == step].copy()
    df_sim = df_simulated[df_simulated["Step"] == step].copy()

    # Ensure there's data after filtering
    if df_exp.empty or df_sim.empty:
        logging.info(
            "Insufficient data for the specified step in one of the DataFrames."
        )
        return None

    df_exp.loc[:, "relative_time"] = (
        df_exp["relative_time"] - df_exp["relative_time"].min()
    )
    df_sim.loc[:, "relative_time"] = (
        df_sim["relative_time"] - df_sim["relative_time"].min()
    )

    # Range to normalize the significance of each segment
    range_min = min(df_sim[var].min(), df_exp[var].min())
    # Common time range between the two curves
    min_time = max(df_sim["relative_time"].min(), df_exp["relative_time"].min())
    max_time = min(df_sim["relative_time"].max(), df_exp["relative_time"].max())

    if min_time >= max_time:  # No overlapping time range
        logging.info("No overlapping time range between datasets.")
        return None

    trunc_time = np.linspace(min_time, max_time, interp_points)

    # Interpolation over the common time vector
    interp_EV = interp1d(
        df_exp["relative_time"],
        df_exp[var],
        bounds_error=False,
        fill_value="extrapolate",
    )
    interp_PB = interp1d(
        df_sim["relative_time"],
        df_sim[var],
        bounds_error=False,
        fill_value="extrapolate",
    )
    var_intrp_exp = interp_EV(trunc_time)
    var_intrp_sim = interp_PB(trunc_time)

    value_range = np.abs(np.mean(var_intrp_exp))
    # Calculate RMSE error
    calc_rmse = (
        np.sqrt(np.mean((np.abs(var_intrp_sim) - np.abs(var_intrp_exp)) ** 2))
        / value_range
    )

    # Optional: plot the curves
    if to_plot:
        plt.figure(figsize=(10, 6))
        plt.plot(trunc_time, var_intrp_exp, label="Experimental Data")
        plt.plot(trunc_time, var_intrp_sim, label="Simulated Data")
        plt.legend()
        plt.xlabel("Relative Time")
        plt.ylabel(var)
        plt.title(f"Comparison of {var} over Time")
        plt.show()

    return calc_rmse
