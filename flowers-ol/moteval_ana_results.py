import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from get_cog_assessment_results import delete_uncomplete_participants


if __name__ == '__main__':
    csv_path = "results/gonogo/gonogo.csv"
    dataframe = pd.read_csv(csv_path)
    dataframe = delete_uncomplete_participants(dataframe)
