function EV_data = import_EV_data(battery_id, downsampled_rate)
    % Set default value for downsampled_rate if not provided

    EV_data = table();
    P = "/home/ccanodom/data/EV_battery/Complete";
    S = dir(fullfile(P,battery_id + "*.mat"));

    index = 1:numel(S);
    for k = index
        F = fullfile(P,S(k).name);
        file = load(F);
        clearvars "current_table"
        current_table = table(file.t_full_vec_M1_NMC25degC, file.V_full_vec_M1_NMC25degC, ...
        file.I_full_vec_M1_NMC25degC, file.ch_cap_full_vec_M1_NMC25degC, ...
        file.dis_cap_full_vec_M1_NMC25degC,  file.Step_Index_full_vec_M1_NMC25degC);
        %current_table.Properties.VariableNames = ["t", "V","C", "Step"];
        current_table.Properties.VariableNames = ["t", "V","C","D_cap","C_cap", "Step"];
        current_table = downsample(current_table, downsampled_rate);
        EV_data = [EV_data; current_table];
    end
    EV_data.t = EV_data.t / 3600;
    numRows = height(EV_data);
    cycleNum = zeros(numRows, 1);
    currentCycle = 1;
    last_step = false;
    % Assuming 'step' is the name of your column with step numbers
    for i = 2:numRows
        if EV_data.Step(i) == 14 % Detects a reset or cycle completion
            last_step = true;
        elseif last_step == true
            last_step = false;
            currentCycle = currentCycle + 1;
        end
        cycleNum(i) = currentCycle;
    end
    % Add the cycle number as a new column
    EV_data.Cycle = cycleNum;
        % Initialize the RelativeTime column
    EV_data.relative_time = zeros(height(EV_data), 1);
    
    % Loop through each cycle to calculate relative time
    uniqueCycles = unique(EV_data.Cycle);
    for i = 1:length(uniqueCycles)
        cycleIndices = EV_data.Cycle == uniqueCycles(i);
        cycleStartTimestamp = EV_data.t(find(cycleIndices, 1));
        EV_data.relative_time(cycleIndices) = EV_data.t(cycleIndices) - cycleStartTimestamp;
    end
    
original_values =   [ 1  2  3  4  5  6  7 8 9 10 11 12 13 14];
new_values =        [-1 -1 -1 -1 -1 -1  0 1 2  3 -1 -1  4  5];
%new_values = [-1 -1 -1 -1 -1 -1 0 1 2  3  4  5  5  6];
% Initialize the mapped array with zeros or any other default value
mapped_values = zeros(size(original_values));

% For each unique value in the original array, map it to the new value
for i = 1:length(original_values)
    % Find the locations of the current original value in the array
    [isPresent, loc] = ismember(EV_data.Step, original_values(i));
    % Assign the corresponding new value to these locations
    mapped_values(isPresent) = new_values(i);
end
EV_data(EV_data.Step == -1,:) = [];
EV_data.Step = mapped_values';
EV_data.C = -EV_data.C;
EV_data = fix_step_1_error(EV_data);


end 
%% This problem only happen in certain data and is related to the step ==1
% The problem cna be solved just ensuring that in step one, the experiemnt 
% finish when the current is above a threshold, in the experiemnt is set to
% 0.05 wich i would do the same.
function EV_data_output = fix_step_1_error(EV_data)
% Loop through each cycle to calculate relative time
    selected_index = ((EV_data.Step == 1 | EV_data.Step == 3)  & abs(EV_data.C) < 50e-3);
    EV_data_output = EV_data(~selected_index,:);

end

