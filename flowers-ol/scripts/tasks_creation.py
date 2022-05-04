import json
import copy

json_body = []

nb_questions = 40

prefix_task = 'curiosity_questionnaire'

common_parameter_dict = {
    'description': 'Description of curiosity_questionnaire',
    'prompt': 'Start',
    'view_name': 'questionnaire',
    'info_templates_csv': 'Questionnaire=generic_instructions.html,Exemples=example_widgets.html-'
}

task_stack = ""

for i in range(nb_questions):
    tmp_dict = copy.deepcopy(common_parameter_dict)
    tmp_dict['name'] = f'{prefix_task}_{i}'
    tmp_dict['extra_json'] = {'instruments': ['curiosity'], 'context__handle': f'curiosity_ctx_{i}'}
    json_body.append({'model': 'manager_app.Task', 'fields': copy.deepcopy(tmp_dict)})
    task_stack += f',{prefix_task}_{i}'

experiment_session = {'model': 'manager_app.ExperimentSession',
                      'fields': {
                          'study': 'curiosity_study',
                          'task_csv': task_stack,
                          'index': 0,
                      }}

json_body.append(experiment_session)

file_name = 'tasks_curiosity'

with open(f"{file_name}.json", "w") as outfile:
    json.dump(json_body, outfile)
