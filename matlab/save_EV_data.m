%% 

batteryIDs = ["W03", "W04", "W05", "W07", "W08", "W09", "W10"];
batteryIDs = ['W04',  "W08", "W09", "W10"];
batteryNum = [3,  5, 6, 7];
W04 = [0,25,75,123,132,159,176,179];
W08 = [0,25,75,125,148,150,151,157,185,222,247,272,297,322,347];
W09 = [0,25,75,122,144,145,146,150,179,216,241,266,291,316,341];
W10 = [0,25,75,122,146,148,151,159,188,225,250,275,300,325,350];
hdf5FilePath = "battery.h5";
capacity_test = load("capacity_test.mat");
downsample_rate = 20;
all_batteries = {W04,W08,W09,W10};
figure(1)
for i=1:length(batteryIDs)
    subplot(2,2,i)
    current_battery = batteryNum(i);
    for capacity_test_index = 1:length(all_batteries{i})
        CapacityTestCycle.Cap = capacity_test.cap{capacity_test_index, current_battery};
        CapacityTestCycle.V = capacity_test.vcell{capacity_test_index, current_battery};
        CapacityTestCycle.C = capacity_test.curr{capacity_test_index, current_battery};
        CapacityTestCycle.T = capacity_test.curr{capacity_test_index, current_battery};
         % Create a group name for the current cycle with battery identifier
        groupName = sprintf('/CapTest_%s_Cycle%04d', batteryIDs(i), all_batteries{i}(capacity_test_index));
        display(groupName)
        % Check if the group exists, if not, create a placeholder dataset to establish the group
        try
            h5info(hdf5FilePath, groupName);
        catch
            placeholderPath = sprintf('%s/Placeholder', groupName);
            h5create(hdf5FilePath, placeholderPath, 1);
            h5write(hdf5FilePath, placeholderPath, 0);
        end
         % Save each field of the structure as a dataset within the group
        fieldNames = fieldnames(CapacityTestCycle);
        for j = 1:numel(fieldNames)
            datasetName = sprintf('%s/%s', groupName, fieldNames{j});
            % Create dataset if it doesn't exist
            try
                h5create(hdf5FilePath, datasetName, size(CapacityTestCycle.(fieldNames{j})), 'Datatype', class(CapacityTestCycle.(fieldNames{j})));
            catch ME
                if ~strcmp(ME.identifier, 'MATLAB:imagesci:h5create:datasetAlreadyExists')
                    rethrow(ME);
                end
            end
            h5write(hdf5FilePath, datasetName, CapacityTestCycle.(fieldNames{j}));
        end
    end
    % Convert table to a structure for HDF5 storage
    display("Starting battery ID: " + batteryIDs(i))
    save_battery_to_hdf5(batteryIDs(i), hdf5FilePath, downsample_rate)
end

