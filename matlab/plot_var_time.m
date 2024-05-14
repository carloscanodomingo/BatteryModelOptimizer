function data = plot_var_time(table, var, step,cycles_of_interest)
%PLOT_VOLTAGE_TIME Summary of this function goes here
%   Detailed explanation goes here
%table = table(table.relative_time ~= 0,:);
table = table(table.Step == step,:);
% Assuming sweep0 is your original table with columns 'Cycle', 'RelativeTime', etc.

% Step 1: Calculate the minimum relative time for each cycle
minRelativeTimeByCycle = groupsummary(table, 'Cycle', @(x) min(x), 'relative_time');
% This creates a table with unique cycles and the minimum relative time for each cycle

% Rename the variable for clarity
minRelativeTimeByCycle.Properties.VariableNames{'fun1_relative_time'} = 'min_relative_time';

% Step 2: Merge the minimum relative time back to the original table
sweep0WithMin = join(table, minRelativeTimeByCycle, 'Keys', 'Cycle');

% Step 3: Create the new column by subtracting the minimum relative time from the relative time
sweep0WithMin.NewRelativeTime = sweep0WithMin.relative_time - sweep0WithMin.min_relative_time;

% Now sweep0WithMin contains your original data plus the new column 'NewRelativeTime'


numCycles = length(cycles_of_interest); % Number of cycles

% Now select_rows is a logical array that you can use to index into sweep0

% Generate a colormap array (numCycles x 3). Here, 'jet' is used, but you can use 'hot', 'cool', etc.
colors = jet(numCycles);
data = {};
figure; % Creates a new figure window
selected_data = sweep0WithMin;
% Loop through each cycle of interest
for i = 1:length(cycles_of_interest)
    cycle = cycles_of_interest(i);
    
    % Filter the data for the current cycle
    cycle_data = selected_data(selected_data.Cycle == cycle, :);
    data{i} = cycle_data;
    % Plot V vs. RelativeTime for the current cycle
    plot(cycle_data.NewRelativeTime, cycle_data{:,var}, 'Color', colors(i, :), 'DisplayName', sprintf('Cycle %d', cycle));
    hold on; % Keeps the plot window open to add more plots
end

% Customize the plot
xlabel('Relative Time');
ylabel(sprintf('(%s)',var));
title('Voltage vs. Relative Time for Selected Cycles');
legend('show'); % Show legend
grid on; % Add a grid for better readability
hold off; % No more plots will be added to this figure

end

