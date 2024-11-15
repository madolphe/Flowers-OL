import json

import pandas as pd


def parse_to_fixture(path_to_csv, path_to_save):
    table = pd.read_csv(path_to_csv)
    table.loc[:, "reverse"] = table.reverse.astype(bool)
    output = []
    for i, row in table.iterrows():
        row_dict = dict(row)
        entry = {}
        entry["model"] = "experiment_manager_app.Question"
        # entry['pk'] = i + 1
        entry["fields"] = row_dict
        output.append(entry)
    json_string = json.dumps(output)
    with open(path_to_save, "w") as json_out:
        json.dump(output, json_out)


if __name__ == "__main__":
    parse_to_fixture("questions_mot.csv", "../../survey_app/fixtures/MOTQuestions.json")
