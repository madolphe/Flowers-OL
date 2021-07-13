import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import copy
from get_cog_assessment_results import delete_uncomplete_participants
from sklearn.linear_model import LinearRegression


# keyRes1 = F => 1 (ODD impair - LOW)
# keyRes2 = J => 2 (EVEN pair - HIGH)
# task1 = parity (0)
# task2 = relative (1)


def delete_beggining_of_block(row):
    results = row["results_ind_switch"].split(",")
    results = [int(elt) for elt in results]
    new_row = copy.deepcopy(results)
    for idx, elt in enumerate(results):
        if idx % 33 == 0:
            new_row[idx] = 0
    return new_row


def transform_string_to_row(row, column):
    return [int(elt) for elt in row[column].split(',') if elt]


def correct_sequence_of_answers(row):
    seq_answer_relative = []
    seq_answer_parity = []
    seq_relative_switch = []
    seq_parity_switch = []
    for response, task, target, switch in zip(row.results_responses, row.results_indtask, row.results_trial_target,
                                              row.results_ind_switch_clean):
        # First check what activity is requested - if None => do not consider the trial
        if task == 1:
            seq_relative_switch.append(switch)
            if (response == 1 and target < 4) or (response == 2 and target > 4):
                seq_answer_relative.append(1)
            else:
                seq_answer_relative.append(0)
        elif task == 0:
            seq_parity_switch.append(switch)
            if (response == 1 and (target % 2) == 1) or (response == 2 and (target % 2) == 0):
                seq_answer_parity.append(1)
            else:
                seq_answer_parity.append(0)
    return seq_answer_relative, seq_answer_parity, seq_relative_switch, seq_parity_switch


def compute_correct_answer(row, answer_type):
    seq_answer_relative, seq_answer_parity, seq_relative_switch, seq_parity_switch = correct_sequence_of_answers(row)
    if answer_type == "correct_total":
        return seq_answer_relative.count(1) + seq_answer_parity.count(1)
    elif answer_type == "correct_relative":
        return seq_answer_relative.count(1)
    elif answer_type == "correct_parity":
        return seq_answer_parity.count(1)
    elif answer_type == "total_nb":
        return len(seq_answer_parity) + len(seq_answer_relative)
    elif answer_type == "parity_nb":
        return len(seq_answer_parity)
    elif answer_type == "relative_nb":
        return len(seq_answer_relative)
    elif answer_type == "check_switch":
        parity_errors_switch = sum(
            [1 for elt, sw in zip(seq_answer_parity, seq_parity_switch) if (sw == 1 and elt == 0)])
        relative_errors_switch = sum(
            [1 for elt, sw in zip(seq_answer_parity, seq_parity_switch) if (sw == 1 and elt == 0)])
        return parity_errors_switch + relative_errors_switch


def compute_mean(row):
    return np.mean(row["results_rt"])


def boxplot_pre_post(column, figname):
    pre_test = dataframe[dataframe['task_status'] == 'PRE_TEST'][column]
    post_test = dataframe[dataframe['task_status'] == 'POST_TEST'][column]
    plt.boxplot([pre_test.values, post_test.values], positions=[0, 1])
    plt.xticks([0, 1], ['PRE-TEST', 'POST-TEST'])
    plt.savefig(f"results/taskswitch/{figname}.png")
    plt.close()


def linear_reg_and_plot(column, figname):
    post_test = dataframe[dataframe['task_status'] == 'POST_TEST'][column]
    pre_test = dataframe[dataframe['task_status'] == 'PRE_TEST'][column]
    reg = LinearRegression().fit(np.expand_dims(pre_test.values, axis=1), post_test.values)
    score = reg.score(np.expand_dims(pre_test.values, axis=1), post_test.values)
    plt.scatter(x=pre_test, y=post_test, c='red')
    plt.plot([pre_test.values.min(), pre_test.values.max()],
             reg.predict(np.expand_dims([pre_test.values.min(), pre_test.values.max()], axis=1)), color='blue',
             linewidth=3)
    plt.title(f"R**2 : {score}")
    plt.savefig(f"results/taskswitch/{figname}.png")
    plt.close()


if __name__ == '__main__':
    csv_path = "results/taskswitch/taskswitch.csv"
    dataframe = pd.read_csv(csv_path)
    dataframe = delete_uncomplete_participants(dataframe)
    dataframe["results_responses"] = dataframe.apply(lambda row: transform_string_to_row(row, "results_responses"),
                                                     axis=1)
    dataframe["results_trial_target"] = dataframe.apply(
        lambda row: transform_string_to_row(row, "results_trial_target"), axis=1)
    dataframe["results_indtask"] = dataframe.apply(
        lambda row: transform_string_to_row(row, "results_indtask"), axis=1)
    dataframe["results_rt"] = dataframe.apply(
        lambda row: transform_string_to_row(row, "results_rt"), axis=1)
    print(dataframe.info())
    # results_ind_switch : remove first element of each row by null
    # 3 blocks - 99 responses (idx: 0 - 33 - 66 , beggining of each block should be set to null)
    # participant = dataframe[dataframe['task_status'] == "PRE_TEST"]
    # participant = participant[participant['participant_id'] == 15]
    dataframe["results_ind_switch_clean"] = dataframe.apply(delete_beggining_of_block, axis=1)

    # results_response: actual answer of the participant
    # ind_switch: is it a "reconfiguration answer" 1=lower-even / 2=higher-odd
    # results_trial_target: is the question
    dataframe["nb_correct_total_answer"] = dataframe.apply(lambda row: compute_correct_answer(row, "correct_total"),
                                                           axis=1)
    dataframe["nb_correct_relative_answer"] = dataframe.apply(
        lambda row: compute_correct_answer(row, "correct_relative"), axis=1)
    dataframe["nb_correct_parity_answer"] = dataframe.apply(lambda row: compute_correct_answer(row, "correct_parity"),
                                                            axis=1)
    dataframe["nb_total"] = dataframe.apply(lambda row: compute_correct_answer(row, "total_nb"), axis=1)
    dataframe["nb_parity"] = dataframe.apply(lambda row: compute_correct_answer(row, "parity_nb"), axis=1)
    dataframe["nb_relative"] = dataframe.apply(lambda row: compute_correct_answer(row, "relative_nb"), axis=1)
    dataframe["errors_in_switch"] = dataframe.apply(lambda row: compute_correct_answer(row, "check_switch"), axis=1)
    dataframe["total_error"] = dataframe["nb_total"] - dataframe["nb_correct_total_answer"]
    dataframe["accuracy"] = dataframe["nb_correct_total_answer"] / dataframe["nb_total"]

    # Plot accuracy
    boxplot_pre_post("accuracy", "accuracy")

    # Mean RT
    dataframe["mean_RT"] = dataframe.apply(compute_mean, axis=1)
    boxplot_pre_post("mean_RT", "reaction_time_mean")
    linear_reg_and_plot("mean_RT", "linear_reg_RT")

    dataframe.to_csv("results/taskswitch/taskswitch_treatment.csv")

