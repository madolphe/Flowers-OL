import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

csv_path = "results/taskswitch.csv"
dataframe = pd.read_csv(csv_path)
print(dataframe)

# results_ind_switch : remove first element of each row by null
# Number of block? Number of trials in a session ? 4 blocks - 99 responses -
# beggining of each block should be set to null

# results_response: actual answer of the participant
# ind_switch: is it a "reconfiguration answer" 1=lower-even / 2=higher-odd
# results_trial_target: is the question

# First compute the response_correct : 0 false / 1 correct
def compute_correct_answer(row):
    nb_of_correct_answer = 0
    nb_of_correct_relative_answer = 0
    nb_of_correct_parity_answer = 0
    for response, task, target in zip(row.results_responses, row.results_indtask, row.results_trial_target):
        if task == '1':
            flag = target > 4
            if response==1 and flag:
                nb_of_correct_relative_answer += 1
        else:
            flag = (target // 2) == 0
            if response==1 and flag:
                nb_of_correct_parity_answer += 1

# Look at mean per session


tmp = dataframe.results_responses.values[1].split(',')
print(len(tmp))
