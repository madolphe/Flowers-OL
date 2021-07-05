import numpy as np
import pandas as pd

csv_path = "results/gonogo.csv"
dataframe = pd.read_csv(csv_path)

# print(dataframe.head())
# print(dataframe.columns)

participant_data = dataframe[dataframe["participant_id"] == 15]
participant_data = participant_data[participant_data["task_status"] == "PRE_TEST"]

results_targetvalue = participant_data["results_targetvalue"].values #Number displayed when interraction
results_responses = participant_data["results_responses"].values #1 if 3 after 7, 2 if previous is not 7, 0 if not 3 after 7
results_rt = participant_data["results_rt"].values  #RT when interraction could happen (after 7)

print(results_targetvalue)
print(results_responses)
print(results_rt)

# commission errors (i.e., falsely pressing the button in no-go trials; also called false alarms)

# Reaction times in or the number of correct go-trials (i.e., hits):

# omission errors (i.e., falsely not pressing the button in go trials; also called misses):


# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5422529/
#  Some studies have reported indices based on signal detection theory such as discrimination index d' or decision bias
#  C and it has been argued that C is a better indicator of disinhibition than commission errors alone as it takes the number
#  of both hits and false alarms into account (Noël et al., 2005; Mobbs et al., 2008).
# ==> GOT BACK TO THE 3 MEASURES ABOVE IN LATTER WORK


