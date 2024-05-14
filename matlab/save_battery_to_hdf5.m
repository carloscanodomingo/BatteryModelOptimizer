function save_battery_to_hdf5(batteryID, hdf5FilePath, downsample_rate)
% Import data using the provided function
    EV_data = import_EV_data(batteryID, downsample_rate); % Adjust these parameters as needed

    % Get unique cycles
    cycles = unique(EV_data.Cycle);


    % Loop through each unique cycle
    for i = 3:length(cycles)
        cycleNumber = cycles(i);

        % Filter data for the current cycle
        cycleData = EV_data(EV_data.Cycle == cycleNumber, :);

        % Convert table to a structure for HDF5 storage
        cycleStruct = table2struct(cycleData, 'ToScalar', true);

        % Create a group name for the current cycle with battery identifier
        groupName = sprintf('/%s_Cycle%04d', batteryID, cycleNumber -2 );

        % Check if the group exists, if not, create a placeholder dataset to establish the group
        try
            h5info(hdf5FilePath, groupName);
        catch
            placeholderPath = sprintf('%s/Placeholder', groupName);
            h5create(hdf5FilePath, placeholderPath, 1);
            h5write(hdf5FilePath, placeholderPath, 0);
        end

        % Save each field of the structure as a dataset within the group
        fieldNames = fieldnames(cycleStruct);
        for j = 1:numel(fieldNames)
            datasetName = sprintf('%s/%s', groupName, fieldNames{j});
            % Create dataset if it doesn't exist
            try
                h5create(hdf5FilePath, datasetName, size(cycleStruct.(fieldNames{j})), 'Datatype', class(cycleStruct.(fieldNames{j})));
            catch ME
                if ~strcmp(ME.identifier, 'MATLAB:imagesci:h5create:datasetAlreadyExists')
                    rethrow(ME);
                end
            end
            h5write(hdf5FilePath, datasetName, cycleStruct.(fieldNames{j}));
        end
    end
end