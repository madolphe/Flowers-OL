import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import copy

csv_path = "results/taskswitch.csv"
dataframe = pd.read_csv(csv_path)
# print(dataframe)

participant = dataframe[dataframe['task_status'] == "PRE_TEST"]
participant = participant[participant['participant_id'] == 15]

print(participant)


def delete_beggining_of_block(row):
    results = row["results_ind_switch"].split(",")
    new_row = copy.deepcopy(results)
    for idx, elt in enumerate(results):
        if idx % 33 == 0:
            new_row[idx] = None
    return new_row


dataframe["results_ind_switch_clean"] = dataframe.apply(delete_beggining_of_block, axis=1)

# results_ind_switch : remove first element of each row by null
# Number of block? Number of trials in a session ? 3 blocks - 99 responses -
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
            if response == 1 and flag:
                nb_of_correct_relative_answer += 1
        else:
            flag = (target // 2) == 0
            if response == 1 and flag:
                nb_of_correct_parity_answer += 1

dataframe["list_correct_answer"] = dataframe.apply()
# Look at mean per session


