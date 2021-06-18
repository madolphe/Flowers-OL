import os
import django
import copy
import pandas as pd
import importlib
import argparse

# Connection to flowers-DB:
flowers_ol = importlib.import_module("flowers-ol.settings")

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "flowers-ol.settings"
)
django.setup()
from mot_app.models import CognitiveResult, CognitiveTask


p = argparse.ArgumentParser("Connector to django DB for cognitive assessment", formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument('-a', '--export_all',action='store_true', help='Boolean flag to export all the cog assessments to CSV')
args = p.parse_args()


def connect_db_python_dict(all_cognitive_results):
    dataset = {}
    for result in all_cognitive_results:
        if result.participant.user_id not in dataset:
            dataset[result.participant.user_id] = [result]
        else:
            dataset[result.participant.user_id].append(result)
    return dataset


def count_number_of_completed_session(dataset):
    completed_session = {}
    half_completed_session = {}
    other = {}
    for key, value in dataset.items():
        if len(value) == 16:
            # print(f"{key} has completed both sessions, ({len(value)} sessions in total)")
            completed_session[key] = value
        elif len(value) >= 8 and len(value) < 16:
            # print(f"{key} has not finished session 2, ({len(value)} sessions in total)")
            half_completed_session[key] = value
        else:
            # print(f"{key} has not finished session 1, ({len(value)} sessions in total)")
            other[key] = value
    return completed_session, half_completed_session, other


def format_dictionnary(dataset):
    for participant, results in dataset.items():
        new_results = []
        for result in results:
            new_result = {}
            new_result[result.cognitive_task.name] = [result.idx, result.results, result.status]
            # new_result[result.cognitive_task.name] = [result.idx, result.status]
            new_results.append(new_result)
        dataset[participant] = new_results
    return dataset


def retrieve_all_results_for_one_task(dataset, task_name):
    return_list = []
    for participant, results in dataset.items():
        tmp = []
        for result in results:
            if task_name in result:
                tmp.append([participant, result[task_name]])
        return_list.append(tmp)
    return return_list


def export_to_csv_for_task(dataset, task_name):
    """
    From dataset specific to a task with format:
    [ [[participant_id, [idx_task, dict_results, status_task] ], [same for POST-test]] , [same for other participant],]
    Returns None BUT export the dict as a csv
    """
    dict_to_export = {'participant_id': [], 'task_idx': [], 'task_status': []}
    # First create columns for results based on participant 1, pre-test results
    for columns in dataset[0][0][1][1].keys():
        dict_to_export[columns] = []
    # Then fill the dict with data:
    for participant, results in enumerate(dataset):
        # results is supposed to be a 2-items array (result to PRE and POST-test)
        for result in results:
            # result[0] is participant id
            # result[1] is participant result for the task, a 2-items vector [task idx, dict of results, task_status]
            dict_to_export['participant_id'].append(result[0])
            dict_to_export['task_idx'].append(result[1][0])
            dict_to_export['task_status'].append(result[1][2])
            dict_results = copy.deepcopy(result[1][1])
            for columns, value in dict_results.items():
                dict_to_export[columns].append(value)
    csv_file = f"results/{task_name}.csv"
    df = pd.DataFrame(dict_to_export)
    if not os.path.isdir("results/"):
        os.mkdir("results")
    df.to_csv(csv_file)
    print(f"Export to CSV {task_name}: success!")


all_cognitive_results = CognitiveResult.objects.all()
# Create a dictionnary with participant_id as key and a list of CognitiveResults objects as values
dataset = connect_db_python_dict(all_cognitive_results)
# Just sort the participant according to their progression and keep just completed_sessions
completed_session, half_completed_session, other = count_number_of_completed_session(dataset)
# Reformat this dictionnary to get {"participant_id":[{'task_name':[idx, {results}, status], ...., }]}
completed_session = format_dictionnary(completed_session)

if __name__ == '__main__':

    print(f"Complete: {len(completed_session)}, Half:{len(half_completed_session)}, Other:{len(other)}")
    # Get multiple tables for each task
    # The format used for one task is: participant_id, [idx, {results}, status], ...., }]
    # (==> better to have separate columns for csv export)
    # print(retrieve_all_results_for_one_task(completed_session, 'workingmemory')[0])
    if args.export_all:
        task_list = ['moteval', 'workingmemory', 'memorability_1', 'memorability_2', 'taskswitch', 'enumeration',
                     'loadblindness', 'gonogo']
        for task_name in task_list:
            dataset = retrieve_all_results_for_one_task(completed_session, task_name)
            export_to_csv_for_task(dataset, task_name)
