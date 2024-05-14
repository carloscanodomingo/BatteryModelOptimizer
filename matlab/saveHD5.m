EV_data = import_EV_data(9, 30, 1);
hdf5FilePath= "here";
% Get unique cycles
cycles = unique(EV_data.Cycle);

% Loop through each unique cycle
for i = 1:length(cycles)
    cycleNumber = cycles(i);
    
    % Filter data for the current cycle
    cycleData = EV_data(EV_data.Cycle == cycleNumber, :);
    
    % Convert table to a structure for HDF5 storage
    cycleStruct = table2struct(cycleData, 'ToScalar', true);
    
    % Create a group name for the current cycle
    groupName = sprintf('/Cycle%d', cycleNumber);
    
    % Save each field of the structure as a dataset within the group
    fieldNames = fieldnames(cycleStruct);
    for j = 1:numel(fieldNames)
        datasetName = sprintf('%s/%s', groupName, fieldNames{j});
        h5create(hdf5FilePath, datasetName, size(cycleStruct.(fieldNames{j})));
        h5write(hdf5FilePath, datasetName, cycleStruct.(fieldNames{j}));
    end
end