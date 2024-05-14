import numpy as np
import pandas as pd
from scipy.io import loadmat
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import warnings
import h5py
warnings.simplefilter(action='ignore', category=FutureWarning)

def read_battery_cycle_data(hdf5_path, batteryID, cycleNumber):
    # Construct the group path for the specified battery and cycle
    group_path = f"/W{batteryID:02d}_Cycle{cycleNumber:04d}"

    with h5py.File(hdf5_path, 'r') as file:
        # Check if the group exists
        if group_path in file:
            group = file[group_path]

            # Initialize an empty dictionary to hold the data
            data = {}

            # Loop through each dataset in the group and read the data
            for name, dset in group.items():
                # Skip placeholder datasets if any
                if name != 'Placeholder':
                    data[name] = dset[:]
            for key in data.keys():
                data[key] = data[key].squeeze()
            # Convert the dictionary to a pandas DataFrame
            df = pd.DataFrame(data)

            return df
        else:
            print(f"Group {group_path} not found in the HDF5 file.")
            return None
mapping = {
            7:0,
        8:1,
        9: 2,
        10: 3,
        11: 4,
        12:5,
        13: 5,
        14: 6
    }
def get_data_EV(data_path):
    data = loadmat(data_path)
    
    # Extracting necessary arrays from the loaded data
    time = data['t_full_vec_M1_NMC25degC'].squeeze()
    step_index = data['Step_Index_full_vec_M1_NMC25degC'].squeeze()
    voltage = data['V_full_vec_M1_NMC25degC'].squeeze()
    charge_capacity = data['ch_cap_full_vec_M1_NMC25degC'].squeeze()
    discharge_capacity = data['dis_cap_full_vec_M1_NMC25degC'].squeeze()
    current = data['I_full_vec_M1_NMC25degC'].squeeze()  # Assuming this is the current data variable

    
    # Mapping dictionary


# Apply the mapping, preserve original values if not in mapping
    # Creating the DataFrame with all variables
    df = pd.DataFrame({
        'Time': time,
        'Step': step_index,
        'V': voltage,
        'C_cap': charge_capacity,
        'D_cap': discharge_capacity,
        'C': current
    })
    default_index = -1
    #df['Step'] = df['Step'].map(lambda x: mapping.get(int(x), default_index))  # Use x if not found in mapping
    return df



def include_cycle_number(df):
        # Initialize a cycle number array with zeros, same length as step_index
    cycle_numbers = np.zeros_like(df['Step'], dtype=int)
    
    # Start with cycle number 1 (or 0 if you prefer indexing from 0)
    current_cycle = 0
    # Loop through the step index array to identify changes indicating a new cycle
    step_index = df['Step'].to_numpy()
    last_index = False
    current_index = 0
    next_index = df['Step'].to_numpy()
    for i in range(1, len(step_index)):
        if step_index[i] > step_index[i-1]:
            current_index += 1
        if step_index[i] == 14:
            last_index = True
        else:
            if last_index == True:
                current_cycle += 1
                last_index= False
                current_index = 0
        cycle_numbers[i] = current_cycle
        next_index[i] = current_index
    df['Cycle'] = cycle_numbers
    # Determine the start time for each cycle
    start_time_per_cycle = df.groupby('Cycle')['Time'].transform('min')

    # Calculate relative time by subtracting start time from each time value
    df.loc[:,'relative_time'] = df.loc[:,'Time'] - start_time_per_cycle
    print(df.columns)
    # Setting a MultiIndex composed of Time, Cycle_Number, and Step_Index

    # Filter out rows where Cycle_Number is 0
    #df = df[df.index.get_level_values('Cycle_Number') != 0]
    return df
def map_index(df):




    default_index = -1
    df['Step'] = df['Step'].map(lambda x: mapping.get(int(x), default_index))  # Use x if not found in mapping
    return df
# Display the first few rows to confirm the DataFrame is correctly setup
def plot_voltage_vs_capacity(df, step_index, capacity_type='charge'):
    """
    Plots Voltage vs. Capacity (Charge or Discharge) for a given Step Index, with each cycle as a different line.

    Parameters:
    - step_index: int, the Step Index to filter the DataFrame on.
    - capacity_type: str, 'charge' or 'discharge' to specify which capacity to plot against voltage.
    """

     # Use .xs to select data for the given Step_Index
    step_df = df.xs(step_index, level='Step')
    # Determine the capacity column based on the capacity_type parameter
    capacity_column = 'C_cap' if capacity_type == 'charge' else 'D_cap'
    plot_title = f'Voltage vs. {capacity_column} for Step {step_index} by Cycle'
    x_label = f'{capacity_column} (Ah)'

    # Group by 'Cycle_Number'
    grouped = step_df.groupby('Cycle')


    # Define the Greys colormap
    cmap = cm.get_cmap('Reds')

    # Get the total number of cycles to normalize the cycle number to [0, 1]
    num_cycles = len(grouped)
    norm = mcolors.Normalize(vmin=0, vmax=num_cycles)
    # Plotting
    plt.figure(figsize=(12, 8))

    for cycle, group in grouped:
        color = cmap(norm(cycle))
        plt.plot(group[capacity_column], group['V'], label=f'Cycle {cycle}', color=color, linewidth=0.1)

    plt.title(plot_title)
    plt.xlabel(x_label)
    plt.ylabel('Voltage (V)')
    plt.grid(True)
    return plt




def plot_capacity_vs_time(df, step_index, capacity_type='charge', cycle = None):
    """
    Plots Voltage vs. Capacity (Charge or Discharge) for a given Step Index, with each cycle as a different line.

    Parameters:
    - step_index: int, the Step Index to filter the DataFrame on.
    - capacity_type: str, 'charge' or 'discharge' to specify which capacity to plot against voltage.
    """

     # Use .xs to select data for the given Step_Index
    step_df =df # df.xs(step_index, level='Step_Index')
    # Determine the capacity column based on the capacity_type parameter
    capacity_column = 'Charge_Capacity' if capacity_type == 'charge' else 'Discharge_Capacity'
    plot_title = f'{capacity_column} vs. Time for Step {step_index} by Cycle'
    y_label = f'{capacity_column} (Ah)'

    if cycle is not None:
        # If a specific cycle is specified, further filter the DataFrame
        df = df.xs(cycle, level='Cycle_Number')

    # Group by 'Cycle_Number' if plotting for all cycles
    grouped = df.groupby('Cycle_Number') if cycle is None else [(cycle, df)]
    # Define the Greys colormap
    cmap = cm.get_cmap('Reds')

    # Get the total number of cycles to normalize the cycle number to [0, 1]
    num_cycles = len(grouped)
    norm = mcolors.Normalize(vmin=0, vmax=num_cycles)
    # Plotting
    plt.figure(figsize=(12, 8))

    for cycle, group in grouped:

        time = group.index.get_level_values('Time')
        adjusted_time = time - time.min()
        color = cmap(norm(cycle))
        plt.plot(adjusted_time, group[capacity_column], label=f'Cycle {cycle}', color=color, linewidth=1)

    plt.title(plot_title)
    plt.xlabel("Time [s]")
    plt.ylabel(y_label)
    plt.grid(True)
    return plt

def extract_discharge_fixed_step(df):
    df_discarge = df.xs(13, level='Step_Index')



def plot_soc_vs_time_for_step(df, total_capacity, cycle=None):
    """
    Calculates State of Charge (SoC) based on charge capacity and plots SoC vs. Time for a given Step Index.
    
    Parameters:
    - step_index: int, the Step Index to select data for.
    - total_capacity: float, the total battery capacity in Ah or Wh (consistent with your data).
    """

    if cycle is not None:
        # If a specific cycle is specified, further filter the DataFrame
        df = df.xs(cycle, level='Cycle_Number')

    # Group by 'Cycle_Number' if plotting for all cycles
    grouped = df.groupby('Cycle_Number') if cycle is None else [(cycle, df)]
    plt.figure(figsize=(14, 7))

    for cycle, group in grouped:
        # Determine which capacity to use based on Step_Index
        # Steps 13 and 14 use Discharge Capacity, others use Charge Capacity
        max_soc = (group["Charge_Capacity"].max() / total_capacity) 

        min_soc = (group["Discharge_Capacity"].max() / total_capacity) 
        norm_soc = max_soc / min_soc
        print(f"max: {max_soc} min: {min_soc} norm_soc {norm_soc}")
        group['SoC'] = group.apply(
            lambda row:norm_soc* (min_soc - (row['Discharge_Capacity'] / total_capacity))* 100 if row.name[1] in [12,13, 14] else (row['Charge_Capacity'] / total_capacity) * 100,
            axis=1
        )
        # Extract 'Time' from the index for plotting
        time = group.index.get_level_values('Time')
        
        adjusted_time = time - time.min()
        # Calculate SoC as a percentage of total capacity
        
        # Plotting SoC vs. Time
        plt.plot(adjusted_time, group['SoC'] , label=f'Cycle {cycle} SoC', linestyle='-', marker='', alpha=0.7)

    plt.title(f'State of Charge vs. Time ')
    plt.xlabel('Time (s)')
    plt.ylabel('State of Charge (%)')
    plt.grid(True)
    plt.show()
