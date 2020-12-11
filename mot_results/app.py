# @TODO: Laetitia --> 371
# @TODO: markdown réécrire équations et qualité et choix réel

import streamlit as st
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import hiplot as hip


st.set_page_config(initial_sidebar_state="expanded")

# TITLE:
st.title('Space exploration by ZPDES')


@st.cache
def load_data():
    with open('get_bandits/laetitia_values.json') as json_file:
        data = json.load(json_file)
        data_full = pd.read_csv('get_bandits/camille.csv')
        col_list = ['episode_number', 'n_targets', 'speed_max', 'n_distractors', 'probe_time', 'tracking_time',
                    'nb_target_retrieved', 'nb_distract_retrieved']
        data_full = data_full[col_list]
    values = {'n_targets': np.array([2, 3, 4, 5, 6, 7], dtype=float),
              'speed_max': np.linspace(2, 7, 11, dtype=float),
              'tracking_time': np.linspace(3, 7, 9, dtype=float),
              'probe_time': np.linspace(4, 2, 11, dtype=float),
              'n_distractors': np.linspace(1, 4, 4, dtype=float)}
    return values, data, data_full


data_load_state = st.text('Loading data...')
values, data, data_full = load_data()
data_load_state.text('Loading data...done!')

# SIDEBAR:
st.sidebar.title('Parameters')
step = st.sidebar.slider('step size', 1, 20, 1, 1)
episode_number = st.sidebar.number_input('episode_number', 0, len(data['MAIN']['nb'])-1, 0, step)
if st.sidebar.button('+'):
    episode_number += step
if st.sidebar.button('-'):
    episode_number -= step
st.sidebar.write("Episode number: ", episode_number)
nb = st.sidebar.radio("Which target nb ?", ('nb2', 'nb3', 'nb4', 'nb5', 'nb6', 'nb7'))
st.header('Sampled exercices')
episodes = []

for i in range(-5, 5):
    if 0 <= episode_number+i < len(data['MAIN']['nb']):
        dict_ep = {}
        ep = data_full[data_full['episode_number'] == (episode_number+i)]
        ep = ep.drop(columns=['nb_target_retrieved', 'nb_distract_retrieved', 'episode_number'])
        dict_ep['uid'] = 'uid_'+str(episode_number+i)
        for col in ep.columns:
            try:
                dict_ep[col] = float(ep[col].iloc[0])
            except IndexError:
                st.write(ep)
                st.write(col)
        episodes.append(dict_ep)
xp = hip.Experiment.from_iterable(episodes)
ret_val = xp.display_st(ret="brush_extents", key="hip")

st.header('Performances')
performances = []
for i in range(-5, 5):
    if episode_number + i >= 0:
        ep = pd.DataFrame(data_full[data_full['episode_number'] == (episode_number + i)])
        ep.drop(columns=['speed_max', 'probe_time', 'tracking_time'], inplace=True)
        ep['sucess'] = 0
        if any(ep.nb_target_retrieved == ep.n_targets):
            if any(ep.nb_distract_retrieved == ep.n_distractors):
                ep['sucess'] = 1
        for index, row in ep.iterrows():
            performances.append(row.to_dict())
        # st.write(ep)
performances = pd.DataFrame(performances)
performances = performances.rename(columns={'episode_number': 'ep', 'nb_target_retrieved': 't_retri',
                                            'nb_distract_retrieved': 'd_retri'})
st.write(performances)

st.header("Bandit states:")
# FIRST PANNEL:
objects = ('nb2', 'nb3', 'nb4', 'nb5', 'nb6', 'nb7')
y_pos = np.arange(len(objects))
col, col0 = st.beta_columns(2)
with st.beta_container():
    fig, ax = plt.subplots()
    ax.set_title("MAIN DIMENSION")
    ax.bar(y_pos, data['MAIN']['nb'][episode_number], align='center', alpha=0.5)
    with col:
        st.pyplot(fig)
    with col0:
        pass


col1, col2 = st.beta_columns(2)
with st.beta_container():
    with col1:
        fig, ax = plt.subplots()
        y_pos = values['speed_max']
        ax.set_title("Speed_max")
        ax.bar(y_pos, data[nb]['speed_max'][episode_number])
        st.pyplot(fig)
    with col2:
        fig, ax = plt.subplots()
        y_pos = values['tracking_time']
        ax.set_title("Tracking time")
        ax.bar(y_pos, data[nb]['tracking_time'][episode_number])
        st.pyplot(fig)

col3, col4 = st.beta_columns(2)
with st.beta_container():
    with col3:
        fig, ax = plt.subplots()
        y_pos = values['probe_time']
        ax.set_title("Probe time")
        ax.bar(y_pos, data[nb]['probe_time'][episode_number])
        st.pyplot(fig)
    with col4:
        fig, ax = plt.subplots()
        y_pos = values['n_distractors']
        ax.set_title("N distractors")
        ax.bar(y_pos, data[nb]['n_distractors'][episode_number])
        st.pyplot(fig)
