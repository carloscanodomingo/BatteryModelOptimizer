%{
if exist("data","var") == 0
    data = {};
    P = "/home/ccanodom/data/sweep_data/";
    S = dir(fullfile(P,'*.csv'));
    
    for k = 1:numel(S)
        F = fullfile(P,S(k).name);
        data{k} = importfile_pybamm(F);
    end
end
%}


%sweep0 = sweep0_bk;
%sweep3 = sweep3_bk;
%sweep7 = sweep7_bk;
F = "/home/ccanodom/data/sweep_data/_new_current_profile_sweep_0_-5.csv";
data = {};
data{1} = importfile_pybamm(F);


%datos_1 = plot_voltage_time(data{1}, step , cycles_of_interest)
%datos_4 = plot_voltage_time(data{4}, step , cycles_of_interest)
%datos_7 = plot_voltage_time(data{7}, step , cycles_of_interest)
%plot_voltage_time(sweep0, 4 , cycles_of_interest)
%plot_voltage_time(sweep3, 5, cycles_of_interest)
%plot_voltage_time(sweep7, 5, cycles_of_interest)
cycles_of_interest = 4;
step = 5;
current_index = 1;
data1_array = data{current_index}((data{current_index}.Step == step) & (data{current_index}.Cycle == cycles_of_interest), :);
data1_time = table2array(data1_array(:,"relative_time"));
data1_array = table2array(data1_array(:, {'V', 'C'}));
%{
current_index = 8;
data2_array = data{current_index}((data{current_index}.Step == step) & (data{current_index}.Cycle == cycles_of_interest), :);
data2_time = table2array(data2_array(:,"relative_time"));
data2_array = table2array(data2_array(:, {'V', 'C'}));
%}

x = data1_time;
V = data1_array(:,1);
I = data1_array(:,2);


%{
x = t_full_vec_M1_NMC25degC;
V = V_full_vec_M1_NMC25degC;
I = I_full_vec_M1_NMC25degC;

%}
% Define the custom model for a second-degree polynomial plius k*I
ft = fittype(' a*x + b + k*I', 'independent', {'x','I' }, 'dependent', 'V', 'coefficients', {'a', 'b',  'k'});


% Fit the model
[fitresult, gof] = fit([x, I], V, ft);

% Display the fit coefficients
coeffvals = coeffvalues(fitresult);
disp('Coefficients (a, b, k):');
disp(coeffvals);

% Display goodness of fit
disp('Goodness of fit:');
disp(gof);
close all
% Plot the fit with data

hold on 
plot(x, fitresult(x,I), LineStyle='--', Color='r', LineWidth=2)
plot(x, V, LineStyle='-', Color='b', LineWidth=2)
legend(' V Fit', 'V');
xlabel('x');
ylabel('V');
title('Polynomial Fit of V = P(x) + k*I');
hold off


