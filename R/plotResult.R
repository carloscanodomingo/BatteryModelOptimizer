library(iraceplot)
library(irace)
library(dplyr)
data = "DEGRADATION_FIX_80_20_irace.Rdata"
data = "/home/ccanodom/data/irace_results/congres_no_de_irace.Rdata"
data = "/home/ccanodom/data/irace_results/Definitivo_no_degradacion_irace.Rdata"
# Source the script file
data = "/home/ccanodom/data/irace_results/Definitivo/congres_no_de_irace.Rdata"
data = "Definitivo_all_irace.Rdata"
data = "/home/ccanodom/data/irace_results/Definitivo/Definitivo_degradation_irace.Rdata"
data = "/home/ccanodom/data/irace_results/Definitivo/Definitivo_all_irace.Rdata"
data = "/home/ccanodom/data/irace_results/Definitivo/Definitivo_all_irace.Rdata"
data = "/home/ccanodom/data/irace_results/Definitivo/Definitivo_all_irace.Rdata"
data = "/home/ccanodom/data/irace_results/DEGRADATION_FIX_80_20_irace.Rdata"
iraceResults <- irace::read_logfile(data)
report <- report(irace_results = iraceResults)
source("/home/ccanodom/dev/nextbat_ai/phase_1/R/plot_irace_best_config.R")
iraceResults <- irace::read_logfile(data)
experiments <- iraceResults$experiments
m = experiments
# Columns to exclude
rows_to_exclude <- c(3, 7, 11, 15, 19)
# Create a vector of all row indices
all_rows <- 1:nrow(m)
# Determine which rows to keep
rows_to_keep <- all_rows[!all_rows %in% rows_to_exclude]

# Select the rows
m_selected <- m[rows_to_keep, ]
iraceResults$experiments = m_selected
plot_irace_best_config(iraceResults = iraceResults)
data = "/home/ccanodom/data/irace_results/congress_mn5/seconds/MN5_congres_degradation1_irace.Rdata"
iraceResults <- irace::read_logfile(data)
plot_irace_best_config(iraceResults = iraceResults)

library(readr)
data <- read_csv("~/data/irace_results/final/degrdation_metric.csv")
library(ggplot2)
# Melt the data for plotting with ggplot
data$Cycle <- seq_len(nrow(data))
# Function to remove outliers based on the IQR
# Function to calculate IQR and filter out the outliers
filter_outliers <- function(x) {
  # Calculate the IQR
  Q1 <- quantile(x, 0.25, na.rm = TRUE)
  Q3 <- quantile(x, 0.75, na.rm = TRUE)
  IQR <- Q3 - Q1
  
  # Define the upper and lower bounds to identify the outliers
  upper <- Q3 + 1.5 * IQR
  lower <- Q1 - 1.5 * IQR
  
  # Replace outliers with NA
  x[x < lower | x > upper] <- NA
  return(x)
}
# Apply the outlier filter function to each battery type series
data$Default <- filter_outliers(data$Default)
data$ND <- filter_outliers(data$ND)
data$ALL <- filter_outliers(data$ALL)
data$D <- filter_outliers(data$D)

library(reshape2)
melted_data <- melt(data, id.vars = "Cycle", na.rm = TRUE)
# Change the factor levels to match desired legend labels
melted_data$variable <- factor(melted_data$variable, 
                               levels = c("Default", "ND", "ALL", "D"),
                               labels = c("Default", "Non-degradation", "All", "Degradation"))

ggthemr('flat')
# Plot the data
# Plot the data
p <- ggplot(melted_data, aes(x = Cycle, y = value, colour = variable, group = variable)) +
  geom_line() +
  scale_x_continuous(limits = c(1, 120)) + # Limiting x-axis to 120 cycles
  labs(x = "Cycle", y = "Metric Value", color = "Parameter set type") +
  ggtitle("Metric Value by Parameter set type") 
# Print the plot
print(p)
# Prepare an empty dataframe to store the results
results_df <- data.frame(matrix(ncol = 20, nrow = nrow(configurations)))
col_names <- c("W4_C01", "W10_C01", "W09_C01", "W08_C01",
                 "W04_C02", "W10_C02", "W09_C02", "W08_C02",  # Add additional names as needed
                 "W04_C03", "W10_C03", "W09_C03", "W08_C03",
                 "W04_C04", "W10_C04", "W09_C04", "W08_C04",
               "W04_C05", "W10_C05", "W09_C05", "W08_C05")
# Assigning column names for clarity (Optional, replace these with meaningful names)
colnames(results_df) <- col_names# Define specific column names


# Fill the dataframe with the corresponding experiments data
for (i in 1:nrow(configurations)) {
  # Assuming each column in experiments directly corresponds to a configuration
  # and that there are exactly 20 experiments per configuration
  results_df[i, ] <- experiments[1:20, as.character(i)]
}
results_df[] <- lapply(results_df, function(x) {
  replace(x, is.na(x) | is.infinite(x), NA)
})
# Calculate Z-scores, ignoring NA values
# scale() function by default centers and scales (calculates Z-score)
z_scores_df <- as.data.frame(lapply(results_df, function(x) scale(x, center = TRUE, scale = TRUE)))

# Filter the results to include only elite configurations using the elite IDs stored in iraceResults
# iraceResults$iterationElites holds the configuration IDs that are elites for each iteration
elite_df <- z_scores_df[iraceResults$iterationElites,] 

# Create a new DataFrame where the index is the iteration number
# This assumes that each entry in iraceResults$iterationElites corresponds to an iteration
# and that these are in the same order as the iterations themselves
elite_df <- data.frame(Iteration = 1:length(iraceResults$iterationElites), elite_df)

# Set the row names of the DataFrame to be the iteration numbers
row.names(elite_df) <- elite_df$Iteration
elite_df$Iteration <- NULL  # Optionally remove the iteration column if it's redundant with the row names

# Load necessary libraries
library(ggplot2)
library(dplyr)

# Assuming elite_df is indexed by iteration numbers as row names
elite_df$Iteration <- as.numeric(row.names(elite_df))

# Calculate averages for each variable across the 5 cycles
# Assuming column names follow the pattern "Wx_C0y" where x varies and y is from 01 to 05
# Calculate the mean for each variable for each unique iteration
averages_df <- elite_df %>%
  group_by(Iteration) %>%
  summarise(across(everything(), mean, na.rm = TRUE))
library(tidyr)
elite_long <- elite_df %>%
  pivot_longer(cols = -Iteration, names_to = "variable", values_to = "value") %>%
  mutate(variable_group = sub("_C0[1-5]", "", variable))  # Remove the cycle number to group by variable prefix

# Now, calculate the mean for each variable group per iteration
mean_per_iteration <- elite_long %>%
  group_by(Iteration, variable_group) %>%
  summarise(mean_value = mean(value, na.rm = TRUE), .groups = 'drop')  # Calculate mean, drop extra grouping


# Plotting the data using ggplot2
plot <- ggplot(data = mean_per_iteration, aes(x = Iteration, y = mean_value, colour = variable_group)) +
  geom_line() +  # Draw lines
  geom_point() +  # Add points to the lines (optional)
  labs(title = "Mean Variable Values Per Iteration",
       x = "Iteration",
       y = "Mean Value",
       colour = "Variable Group") +
  theme_minimal() +
  scale_color_manual(values = c("W4" = "red", "W10" = "blue", "W09" = "green", "W08" = "black"))  # Customize colors

# Display the plot
print(plot)
# Calculate the overall mean per iteration across all variable groups
overall_mean_per_iteration <- mean_per_iteration %>%
  group_by(Iteration) %>%
  summarise(Overall_Mean = mean(mean_value, na.rm = TRUE))

# Merge this overall mean back with the original data for plotting
mean_per_iteration_with_overall <- left_join(mean_per_iteration, overall_mean_per_iteration, by = "Iteration")

library(viridis)


devtools::install_github('Mikata-Project/ggthemr')
library(ggthemr)
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


# Display the plot
plot

print(count)
print(nrow(configurations))
print(valid_ids)

my_data <- valid_configurations
# Removing column B using select()
valid_configurations = configurations[valid_ids, ]
my_data <- configurations %>% select(-c(".ID.",".PARENT."))
y = values
my_data <- cbind(y, my_data)
my_data[iraceResults$iterationElites, 1]
apartments_test = my_data





configurations <- iraceResults$allConfigurations
experiments <- iraceResults$experiments
count <- 0
valid_ids <- c()
means <- c()
for (i in 1:nrow(configurations)){
  current_id <-as.character(i)
  exp <- experiments[, current_id]
  if (any(is.infinite(exp)))
  {
    count = count + 1   
  }else
  {
    valid_ids <- c(valid_ids, i)
    #exp <- na.omit(exp)
    # Select elements at odd positions
    #exp <- exp[seq(0, length(exp), by = 2)]
    # Calculate the mean of these elements
    means <- c(exp[1], means)
    
  }
  
}
print(count)
print(nrow(configurations))
print(valid_ids)

my_data <- valid_configurations
# Removing column B using select()
valid_configurations = configurations[valid_ids, ]
my_data <- valid_configurations %>% select(-c(".ID.",".PARENT."))
y = means
my_data <- cbind(y, my_data)
my_data[iraceResults$iterationElites, 1]
apartments_test = my_data
library("DALEX")
set.seed(1313)
apartments_lm <- lm(y ~ ., data = my_data)

library("randomForest")
set.seed(72)
apartments_rf <- randomForest(m2.price ~ ., data = apartments)

library("e1071")
apartments_svm <- svm(y ~ ., data = my_data)
anova(apartments_lm)

apartments_lm_exp <- explain(model = apartments_lm, 
                             data = apartments_test[,-1], 
                             y = apartments_test$y, 
                             label = "Linear Regression")
apartments_rf_exp <- explain(model = apartments_rf, 
                             data = apartments_test[,-1], 
                             y = apartments_test$m2.price, 
                             label = "Random Forest")
apartments_svm_exp <- explain(model = apartments_svm, 
                              data = apartments_test[,-1], 
                              y = apartments_test$m2.price, 
                              label = "Support Vector Machine")
