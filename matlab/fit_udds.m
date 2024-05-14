function fit_udds(df, n_cycle)
%FIT_UDDS Summary of this function goes here
%   Detailed explanation goes here
step_udds = 5;
selected_df = df((df.Step == step_udds) & (df.Cycle == n_cycle), :);
x = table2array(selected_df(:,"relative_time"));
V = table2array(selected_df(:,'V'));
I = table2array(selected_df(:,'C'));



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

end

