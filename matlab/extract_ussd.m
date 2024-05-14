if exist("ev_data","var") == 0
    ev_data = import_EV_data(10,1, [1]);
end

close all
step = 5;
current_data = ev_data((ev_data.Step == step), :);
  
% Loop through each cycle to calculate relative time
figure(4)
uniqueCycles = unique(current_data.Cycle);
for i = 1:length(uniqueCycles)
    cycleIndices = current_data.Cycle == uniqueCycles(i);
    cycleStartTimestamp = current_data.t(find(cycleIndices, 1));
    current_data.relative_time(cycleIndices) = current_data.t(cycleIndices) - cycleStartTimestamp;
    plot(current_data.t(cycleIndices) - cycleStartTimestamp, current_data.V(cycleIndices));
    hold on 
end
hold off

%Assume x is your time series data
x = current_data.C(cycleIndices); % Your time series data here
v = current_data.V(cycleIndices); % Your time series data here
t = current_data.relative_time(cycleIndices);
% Calculate the autocorrelation
[acf, lags] = autocorr(x, 'NumLags', round(numel(x)/2));

% Find peaks in the autocorrelation function
[pks, locs] = findpeaks(acf);
figure(1)
stem(locs, pks,"filled",'r')
xlabel("Lag")
ylabel("acf")
[a, idx] = max(pks);
separation = locs(idx); 
V = current_data.V(cycleIndices); % Your time series data here
cells_x = {};
cells_t = {};
figure(2)
for i=1:6
    new_index = 1 + (separation * (i - 1)):((separation * i) );
    cells_x{i} = x(new_index);
    cells_t{i} = t(new_index) - min(t(new_index));
    
    plot(cells_t{i}, cells_x{i}, LineWidth=2)
    title("Mean Value: " + mean(cells_x{i}))
    xlabel("Time (s)")
    ylabel("Current (C)")
    hold on
end
hold off

figure(3)
for i=1:6
    new_index = 1 + (separation * (i - 1)):((separation * i) );
    cells_x{i} = v(new_index);
    cells_t{i} = t(new_index) - min(t(new_index));
    
    plot(cells_t{i}, cells_x{i}, LineWidth=2)
    title("Mean Value: " + mean(cells_x{i}))
    xlabel("Time (s)")
    ylabel("Voltage (C)")
    hold on
end
hold off



ussd_current =  table();
ussd_current.t = xq';
ussd_current.C = result';

writetable(ussd_current, "udds_current.csv")


% Assuming the pattern repeats 5 times, we look for significant peaks
% Filter based on some criteria, e.g., peak height to find potential repeats
%significantPeaks = pks > threshold; % Define threshold based on your data

% The locs(significantPeaks) gives you the lags at which significant peaks occur,
% which could indicate the repeating pattern intervals.