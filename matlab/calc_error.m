function [calc_rmse] = calc_error(EV_data,PB_data, step,cycle, var, to_plot, interp_points)
    arguments
        EV_data table;
        PB_data table;
        step uint32 {mustBeNumeric};
        cycle uint32 {mustBeNumeric};
        var char {mustBeMember(var, {'C', 'V'})}
        to_plot {mustBeNumericOrLogical} = false;
        interp_points uint32 {mustBeNumeric} = 100;
    end    
    %CALC_ERROR Summary of this function goes here
    %   Detailed explanation goes here

    % get data under study for electric vehicle
    compEV = EV_data((EV_data.Cycle == cycle) & (EV_data.Step == step),:);
    compEV.relative_time = compEV.relative_time - min(compEV.relative_time);
    
    % get data under study for PyBamm simulation
    compPB = PB_data(PB_data.Cycle == cycle & PB_data.Step == step,:);
    compPB.relative_time = compPB.relative_time - min(compPB.relative_time);

    % Range to normalize the importance of each segment
    range_min = min(min(compPB{:,var}) ,min(compEV{:,var}));
    range_max = max(max(compPB{:,var}) ,max(compEV{:,var}));
    range = range_max - range_min;

    % Extract common time between the two curves
    min_time = max(min(compPB.relative_time) ,min(compEV.relative_time));
    max_time = min(max(compPB.relative_time) ,max(compEV.relative_time));
    trunc_time = linspace(min_time, max_time, interp_points);

    %Interpolate in the common time vector
    EV_y = interp1(compEV.relative_time, compEV{:,var}, trunc_time);
    PB_y = interp1(compPB.relative_time, compPB{:,var}, trunc_time);
    

    % Calculate the error between the 2 curves
    calc_rmse =  rmse(PB_y, EV_y) / range;

    if (to_plot == true)
        hold on
        plot(trunc_time, PB_y, LineWidth=2, Color="cyan")
        plot(trunc_time, EV_y, LineWidth=2, Color="red")
        legend(' PyBamm', 'EV data');
        title("Step = " + step + " Cycle = " + cycle + " RMSE: " + calc_rmse)
        xlabel("Relative Time (h)");
        ylabel(sprintf('(%s)',var));
        hold off
    end
end

