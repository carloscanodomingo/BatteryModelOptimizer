
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib
import plotly.express as px
from enum import Enum
class TypeAgregation(Enum):
    deltaV = 0
    deltaC = 1
    Discharge = 2



def plot_av_at_by_cycle(df, step_index, type_agregation = TypeAgregation.deltaV):
    """
    Plots the average rate of change of V with respect to T for each cycle at a given step index.

    Parameters:
    - df: pandas DataFrame with 'Cycle', 'Time', and 'V' columns.
    - step_index: int, the step index to filter the DataFrame on.
    """
    # Filter the DataFrame for the given step index
    filtered_df = df[df["Step"] == step_index]

    # Group the filtered DataFrame by 'Cycle'
    grouped_by_cycle = filtered_df.groupby('Cycle')

    # Define the colormap
    cmap = cm.get_cmap('viridis')

    # Get the total number of cycles to normalize the cycle number to [0, 1]
    num_cycles = len(grouped_by_cycle)
    norm = mcolors.Normalize(vmin=0, vmax=num_cycles)

    # Create a plot and specify axes
    fig, ax = plt.subplots(figsize=(12, 8))
    output_var = np.zeros(num_cycles)
    cycles = np.zeros(num_cycles)

    # Calculate Av/At for each cycle
    for i, (cycle_number, group) in enumerate(grouped_by_cycle):
        time = group['Time'].to_numpy()
        V = group['V'].to_numpy()
        cycles[i] = cycle_number


        if len(time) == 0:
            output_var[i] = 0
            continue
        # Calculate the average rate of change of V with respect to T
        if type_agregation == type_agregation.deltaV:
            output_var[i] = (-np.diff(V) / np.diff(time)).mean()
        elif type_agregation == type_agregation.deltaC:
            C = group['C'].to_numpy()
            output_var[i] = (np.diff(C) / np.diff(time)).mean()

            # Plot
    colors = cmap(norm(cycles))
    sc = ax.scatter(cycles, output_var, c=cycles)
    
    # Create a colorbar with the correct axes and set label
   # cbar = plt.colorbar(sc, ax=ax)
    #cbar.set_label('Cycle Number', rotation=270, labelpad=15)
    plt.title(f'Average \u0394V / \u0394T for Step {step_index} by Cycle')
    plt.xlabel('Cycle')
    plt.ylabel('Average \u0394V / \u0394T')

    plt.show()

# Example usage:
# plot_av_at_by_cycle(df, 6)



def plot_variable_vs_capacity(df, variable_name, step_index = None,  capacity_type='charge'):
    """
    Plots a specified variable vs. Capacity (Charge or Discharge) for a given Step Index, 
    with each cycle as a different line.

    Parameters:
    - df: pandas DataFrame with columns that include 'Cycle_Number', 'Step_Index', and the specified variable and capacity columns.
    - step_index: int, the Step Index to filter the DataFrame on.
    - variable_name: str, the name of the variable to plot against capacity.
    - capacity_type: str, 'charge' or 'discharge' to specify which capacity to plot against the variable.
    """
    
    # Filter the DataFrame for the specified Step_Index
    if step_index != None:
        df = df[df['Step'] == step_index]
    
    # Determine the capacity column based on the capacity_type parameter
    capacity_column = 'C_cap' if capacity_type == 'charge' else 'D_cap'
    plot_title = f'{variable_name} vs. {capacity_column} for Step {step_index} by Cycle'
    x_label = f'{capacity_column} (Ah)'


    # Get the total number of cycles to normalize the cycle number to [0, 1]
   # num_cycles = len(grouped)
    #norm = mcolors.Normalize(vmin=0, vmax=num_cycles)
    rgb = px.colors.convert_colors_to_same_type(px.colors.sequential.RdBu)[0]

    colorscale = []
    n_steps = int(len(df["Cycle"].unique()) /8)  # Control the number of colors in the final colorscale
    for i in range(len(rgb) - 1):
        for step in np.linspace(0, 1, n_steps):
            colorscale.append(px.colors.find_intermediate_color(rgb[i], rgb[i + 1], step, colortype='rgb'))

    fig = px.line(df, x=f"{capacity_column}", y=f"{variable_name}", color=f"Cycle", color_discrete_sequence=colorscale, height=900)
    return fig# Example usage:
# plot_variable_vs_capacity(df, step_index=9, variable_name='V', capacity_type='charge')


def plot_variable_vs_time(df, variable_name, step_index = None):
    """
    Plots a specified variable vs. Capacity (Charge or Discharge) for a given Step Index, 
    with each cycle as a different line.

    Parameters:
    - df: pandas DataFrame with columns that include 'Cycle_Number', 'Step_Index', and the specified variable and capacity columns.
    - step_index: int, the Step Index to filter the DataFrame on.
    - variable_name: str, the name of the variable to plot against capacity.
    - capacity_type: str, 'charge' or 'discharge' to specify which capacity to plot against the variable.
    """
    
    # Filter the DataFrame for the specified Step_Index
    if step_index != None:
        df = df[df['Step'] == step_index]
  # Asumiendo que 'df' es tu DataFrame y ya está definido

    for i in np.unique(df["Cycle"]):
    # Seleccionar los índices donde 'Cycle' es igual a i
        current_index = df["Cycle"] == i
        
        # Calcular el valor mínimo de 'relative_time' para el ciclo actual
        min_value = df.loc[current_index, "relative_time"].min()
        
        # Restar ese valor mínimo de 'relative_time' para todas las filas del ciclo actual
        df.loc[current_index, "relative_time"] = df.loc[current_index, "relative_time"] - min_value

    # Determine the capacity column based on the capacity_type parameter

    plot_title = f'{variable_name} vs. time for Step {step_index} by Cycle'
    x_label = f'Time (h)'


    # Get the total number of cycles to normalize the cycle number to [0, 1]
   # num_cycles = len(grouped)
    #norm = mcolors.Normalize(vmin=0, vmax=num_cycles)
    rgb = px.colors.convert_colors_to_same_type(px.colors.sequential.RdBu)[0]

    colorscale = []
    n_steps = int(len(df["Cycle"].unique()) /8)  # Control the number of colors in the final colorscale
    for i in range(len(rgb) - 1):
        for step in np.linspace(0, 1, n_steps):
            colorscale.append(px.colors.find_intermediate_color(rgb[i], rgb[i + 1], step, colortype='rgb'))


    fig = px.line(df, x=f"relative_time", y=f"{variable_name}", color=f"Cycle", color_discrete_sequence=colorscale, height=900)
    return fig


def plot_variable_vs_time_by_cycle(df, variable_name, n_cycle ):
    """
    Plots a specified variable vs. Capacity (Charge or Discharge) for a given Step Index, 
    with each cycle as a different line.

    Parameters:
    - df: pandas DataFrame with columns that include 'Cycle_Number', 'Step_Index', and the specified variable and capacity columns.
    - step_index: int, the Step Index to filter the DataFrame on.
    - variable_name: str, the name of the variable to plot against capacity.
    - capacity_type: str, 'charge' or 'discharge' to specify which capacity to plot against the variable.
    """
    
    # Determine the capacity column based on the capacity_type parameter
    df = df[df["Cycle"] == n_cycle]
    plot_title = f'{variable_name} vs. time for Cycle {n_cycle} '
    x_label = f'Time (h)'
    y_label = f"{variable_name}"

    fig = px.line(df, x="relative_time", y=f"{variable_name}", color='Step', title=f'Voltage vs Step for cycle {n_cycle}',height=600)
    fig.update_layout(
        font_family="Courier New",
        font_color="blue",
        title_font_family="Times New Roman",
        title_font_color="red",
        legend_title_font_color="green",
        xaxis_title=x_label,
        title=plot_title,
        yaxis_title=y_label,
    )
    return fig
def plot_voltage_current_by_cycle(df, n_cycle ):
    """
    Plots a specified variable vs. Capacity (Charge or Discharge) for a given Step Index, 
    with each cycle as a different line.

    Parameters:
    - df: pandas DataFrame with columns that include 'Cycle_Number', 'Step_Index', and the specified variable and capacity columns.
    - step_index: int, the Step Index to filter the DataFrame on.
    - variable_name: str, the name of the variable to plot against capacity.
    - capacity_type: str, 'charge' or 'discharge' to specify which capacity to plot against the variable.
    """
    
    # Determine the capacity column based on the capacity_type parameter
    df = df[df["Cycle"] == n_cycle]
    plot_title = f'Voltage & Current for Cycle {n_cycle} '
    x_label = f'Time (h)'
    y_label = f"Voltage (V)"

    fig = px.line(df, x="relative_time", y="V")  
    fig2 = px.line(df,x="relative_time", y="C",color_discrete_sequence=["red"])  
    fig2.update_traces(yaxis ="y2")
    # one more step, config second axis
    fig.add_traces(fig2.data).update_layout(yaxis2={"overlaying":"y", "side":"right"})
    fig.update_layout(
        font_family="Courier New",
        font_color="blue",
        title_font_family="Times New Roman",
        title_font_color="red",
        legend_title_font_color="green",
        xaxis_title=x_label,
        title=plot_title,
        yaxis_title=y_label,
    )
    return fig
