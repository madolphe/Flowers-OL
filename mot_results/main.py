from mot_results.get_bandits.wrapper import bandit_values_to_csv
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
import json


if __name__ == '__main__':
    bandit_values_to_csv()
    # with open('get_bandits/bandit_values.json') as json_file:
    #    data = json.load(json_file)
    # print((data['nb2'][0]))
