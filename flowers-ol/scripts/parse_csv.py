import csv
import copy
import json

file_name = "Rania_questions-context_questions"
model = "survey_app.ContextQuestionnaire"
json_body = []

with open(f"{file_name}.csv", newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for index_row, row in enumerate(spamreader):
        if index_row == 0:
            header = copy.deepcopy(row)
        else:
            new_question = {}
            new_question["model"] = model
            new_question["fields"] = {}
            for key, value in zip(header,row):
                new_question["fields"][key] = value
            json_body.append(new_question)

with open(f"{file_name}.json", "w") as outfile:
    json.dump(json_body, outfile)
