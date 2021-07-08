# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5422529/

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def delete_uncomplete_participants(dataframe):
    """

    """
    mask = pd.DataFrame(dataframe.participant_id.value_counts() < 2)
    participants_to_delete = mask[mask['participant_id'] == True].index.tolist()
    for id in participants_to_delete:
        dataframe = dataframe[dataframe['participant_id'] != id]
    return dataframe


def parse_to_int(elt: str) -> int:
    """
        Parse string value into int, if string is null parse to 0
        If null; participant has not pressed the key when expected
    """
    if elt == '':
        return 0
    return int(elt)


def compute_nb_commission_errors(row: pd.core.series.Series) -> int:
    """
        Take a dataframe row and returns the number of element 2 in the result response
        2 == commission error
    """
    results_responses = list(map(parse_to_int, row["results_responses"].split(
        ',')))  # 1 is click when expected, 0 no click when expected, 2 is mistake
    return results_responses.count(2)


def transform_2_in_0(elt: int) -> int:
    """
        Take an int and returns the remainder in the euclidean division
        ("0 - 1 - 2" possible values and we want to transform 2 into 0)
    """
    return elt % 2


def list_of_correct_hits(row: pd.core.series.Series) -> list:
    """
        Take a dataframe row and returns a list of rt for hits (not for commission errors)
    """
    results_rt = list(map(parse_to_int, row["results_rt"].split(
        ',')))  # RT when interraction could happen (after 7)
    results_responses = list(map(parse_to_int, row["results_responses"].split(
        ',')))
    mask = list(map(transform_2_in_0, results_responses))
    rt_hits = [a * b for a, b in zip(results_rt, mask)]
    return rt_hits


def compute_means(row: pd.core.series.Series) -> float:
    """
        Useless function that returns the mean on a row (pandas already provides one)
    """
    return np.mean(row['result_clean_rt'])


def compute_number_of_omissions(row: pd.core.series.Series) -> int:
    """
        From the row of results, return the number of 0 if elt is 3 in results_targetvalue
    """
    results_responses = list(map(parse_to_int, row["results_responses"].split(',')))
    results_targetvalue = list(map(parse_to_int, row["results_targetvalue"].split(',')))
    count = 0
    for idx, elt in enumerate(results_targetvalue):
        if elt == 3:
            if results_responses[idx] == 0:
                count += 1
    return count


if __name__ == '__main__':
    csv_path = "results/gonogo.csv"
    dataframe = pd.read_csv(csv_path)
    dataframe = delete_uncomplete_participants(dataframe)

    # commission errors (i.e., falsely pressing the button in no-go trials; also called false alarms)
    dataframe['result_commission_errors'] = dataframe.apply(compute_nb_commission_errors, axis=1)
    dataframe.groupby(["task_status", "result_commission_errors"]).count()["participant_id"].unstack(
        "task_status").plot.bar()
    plt.title("Number of commission errors per participant")
    plt.savefig("results/gonogo/gonogo_commissions.png")
    plt.close()

    # Reaction times in or the number of correct go-trials (i.e., hits):
    dataframe['result_clean_rt'] = dataframe.apply(list_of_correct_hits, axis=1)
    dataframe['mean_result_clean_rt'] = dataframe.apply(compute_means, axis=1)
    post_test = dataframe[dataframe['task_status'] == 'POST_TEST']['mean_result_clean_rt']
    pre_test = dataframe[dataframe['task_status'] == 'PRE_TEST']['mean_result_clean_rt']
    plt.scatter(x=pre_test, y=post_test, c='red')
    plt.show()
    plt.savefig("results/gonogo/rt_pre_post_gonogo.png")
    plt.close()

    # omission errors (i.e., falsely not pressing the button in go trials; also called misses):
    dataframe['result_nb_omission'] = dataframe.apply(compute_number_of_omissions, axis=1)
    dataframe.groupby(["task_status", "result_nb_omission"]).count()["participant_id"].unstack("task_status").plot.bar()
    plt.title("Number of omission errors per participant")
    plt.savefig("results/gonogo/gonogo_ommissions.png")
    plt.close()

    # Save data
    dataframe.to_csv("results/gonogo/gonogo_treatment.csv")
