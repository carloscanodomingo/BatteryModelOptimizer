# Assuming all necessary libraries are installed; if not, they should be installed outside of this function.
library(dplyr)
library(ggplot2)
library(tidyr)
library(viridis)
library(ggthemes)
library(ggthemr)

# Define the function
plot_irace_best_config <- function(iraceResults) {
  # Load and prepare data from irace log file
  configurations <- iraceResults$allConfigurations
  experiments <- iraceResults$experiments
  
  # Prepare an empty dataframe to store the results
  results_df <- data.frame(matrix(ncol = 15, nrow = nrow(configurations)))
  col_names <- c("W04_C01", "W09_C01", "W08_C01",
                 "W04_C02", "W09_C02", "W08_C02",
                 "W04_C03", "W09_C03", "W08_C03",
                 "W04_C04", "W09_C04", "W08_C04",
                 "W04_C05", "W09_C05", "W08_C05")
  colnames(results_df) <- col_names
  
  # Fill the dataframe with the corresponding experiments data
  for (i in 1:nrow(configurations)) {
    results_df[i, ] <- experiments[1:15, as.character(i)]
  }
  
  results_df[] <- lapply(results_df, function(x) replace(x, is.na(x) | is.infinite(x), NA))
  
  # Calculate Z-scores, ignoring NA values
  z_scores_df <- as.data.frame(lapply(results_df, function(x) scale(x, center = TRUE, scale = TRUE)))
  
  # Filter the results to include only elite configurations using the elite IDs stored in iraceResults
  elite_df <- z_scores_df[iraceResults$iterationElites,] 
  elite_df <- data.frame(Iteration = 1:length(iraceResults$iterationElites), elite_df)
  row.names(elite_df) <- elite_df$Iteration
  elite_df$Iteration <- NULL  # Optionally remove the iteration column if it's redundant with the row names
  
  elite_df$Iteration <- as.numeric(row.names(elite_df))
  
  # Calculate averages for each variable across the 5 cycles
  elite_long <- elite_df %>%
    pivot_longer(cols = -Iteration, names_to = "variable", values_to = "value") %>%
    mutate(variable_group = sub("_C0[1-5]", "", variable))
  
  mean_per_iteration <- elite_long %>%
    group_by(Iteration, variable_group) %>%
    summarise(mean_value = mean(value, na.rm = TRUE), .groups = 'drop')
  
  overall_mean_per_iteration <- mean_per_iteration %>%
    group_by(Iteration) %>%
    summarise(Overall_Mean = mean(mean_value, na.rm = TRUE))
  
  mean_per_iteration_with_overall <- left_join(mean_per_iteration, overall_mean_per_iteration, by = "Iteration")
  
  ggthemr('flat')
  # Plotting the data with ggplot2, including the overall mean
  plot <- ggplot() +
    geom_line(data = mean_per_iteration_with_overall, aes(x = Iteration, y = mean_value, colour = variable_group)) +
    geom_point(data = mean_per_iteration_with_overall, aes(x = Iteration, y = mean_value, colour = variable_group)) +
    geom_line(data = overall_mean_per_iteration, aes(x = Iteration, y = Overall_Mean, colour = "Overall"), size = 1.2, linetype = "dashed") +
    # scale_color_manual(values = c("W4" = "red", "W10" = "blue", "W09" = "green", "W08" = "black", "Overall" = "purple")) +
    #scale_fill_viridis(option="magma") + 
    labs(title = "Average RMSE value of the best configuration in each iteration",
         x = "Iteration",
         y = "Z-score RMSE",
         colour = "Experiment") #+
  
  return(plot)
}