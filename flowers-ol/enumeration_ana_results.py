import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

csv_path = "results/enumeration.csv"
dataframe = pd.read_csv(csv_path)


# Treat data:
def compute_result_exact_answers(row):
    response = row["results_responses"].split(',')
    target = row["results_targetvalue"].split(',')
    return sum(x == y for x, y in zip(response, target))


dataframe['result_response_exact'] = dataframe.apply(compute_result_exact_answers, axis=1)


def compute_mean_per_row(row):
    return_value = np.array(row['results_rt'].split(','), dtype=np.int32)
    return np.mean(return_value)


def compute_std_per_row(row):
    return_value = np.array(row['results_rt'].split(','), dtype=np.int32)
    return np.std(return_value)


dataframe['mean_rt_session'] = dataframe.apply(compute_mean_per_row, axis=1)
dataframe['std_rt_session'] = dataframe.apply(compute_std_per_row, axis=1)


# Reliability of measurement
pre_response_exact = dataframe[dataframe['task_status'] == "PRE_TEST"]['result_response_exact'].values
post_response_exact = dataframe[dataframe['task_status'] == "POST_TEST"]['result_response_exact'].values

pearson_coeff = np.corrcoef(pre_response_exact, post_response_exact)[1, 0]**2

plt.scatter(pre_response_exact, post_response_exact)
plt.title(f"Pearson coefficient: {pearson_coeff}")

# Mean and SD reaction time plots and values:
fig, axs = plt.subplots(1, len(dataframe.task_status.unique()), figsize=(10,  5), sharey=False)
boxplot = dataframe.boxplot(column=['mean_rt_session', 'result_response_exact'], by=['task_status'], layout=(2, 1), ax=axs)
plt.show()

