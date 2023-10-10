import matplotlib.pyplot as plt
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

from manager_app.models import ParticipantProfile
from survey_app.models import Answer


def get_psychometrics(study):
    all_participant = ParticipantProfile.objects.all().filter(study__name=study)
    participants_all_answers = []
    for participant in all_participant:
        participant_answers_list = []
        if 'condition' in participant.extra_json:
            participant_answers = Answer.objects.all().filter(participant=participant)
            participant_answers_list = create_df_from_participant(participant_answers)
        participants_all_answers += participant_answers_list
    df = pd.DataFrame(participants_all_answers)
    df.to_csv(f"{study}all_answers.csv")


def create_df_from_participant(participant_answers):
    all_answers = []
    for answer in participant_answers:
        all_answers.append(
            [answer.participant.user_id, answer.participant.extra_json['condition'], answer.question.component,
             answer.question.instrument, answer.question.handle,
             answer.session.index, answer.value])
    return all_answers


def filter_condition(df, condition):
    return df[df['condition'] == condition]


def format_questionnaire(df_tlx):
    participants_id = list(set(df_tlx['id']))
    participants_rows = []
    for participant_id in participants_id:
        participant_answers = df_tlx[df_tlx['id'] == participant_id]
        sessions_id = list(set(participant_answers['session_id']))
        for session_id in sessions_id:
            row_participant_session_id = {'id_participant': participant_id, 'session_id': session_id}
            participant_answers_session = participant_answers[participant_answers['session_id'] == session_id]
            for id, ans in participant_answers_session.iterrows():
                # If component already in row just add the value
                if ans.component in row_participant_session_id:
                    row_participant_session_id[ans.component] = (row_participant_session_id[
                                                                     ans.component] + ans.value) / 2
                else:
                    row_participant_session_id[ans.component] = ans.value
            participants_rows.append(copy.deepcopy(row_participant_session_id))
    return pd.DataFrame(participants_rows)


def display_cols_value(df_baseline_mean, df_baseline_std, df_zpdes_mean, df_zpdes_std, dir):
    for col in df_baseline_mean.columns:
        plt.errorbar(df_baseline_mean[col].index, df_baseline_mean[col], yerr=df_baseline_std[col], label='baseline',
                     color='blue')
        plt.scatter(df_baseline_mean[col].index, df_baseline_mean[col], color='blue')

        plt.scatter(df_zpdes_mean[col].index, df_zpdes_mean[col], color='red')
        plt.errorbar(df_zpdes_mean[col].index, df_zpdes_mean[col], yerr=df_zpdes_std[col], label='zpdes', color='red')
        plt.legend()
        plt.title(col)
        plt.savefig(f"{dir}/{col}_old.png")
        plt.close()


def create_dir(name):
    if not os.path.isdir(name):
        os.mkdir(name)


def transform_session_id(row):
    if row['session_id'] < 4:
        row['session_id'] = 0
    else:
        row['session_id'] = 1
    return row


def plot_boxplots(df, subscales, instrument):
    df_tmp = df.apply(transform_session_id, axis=1)
    for col in subscales:
        sub_dict = df_tmp[df_tmp['component'] == col].groupby(['id', 'session_id', 'condition']).mean().reset_index()
        sub_dict = sub_dict.set_index("id")[sub_dict.groupby('id').size() == 2]
        sub_dict.boxplot(column="value", by=['condition', 'session_id'])
        plt.suptitle(col)
        # plt.show()
        plt.savefig(f"{instrument}/{col}.png")
        plt.close()


def plot_questionnaire(instrument, subscales):
    df_tmp = df[df['instrument'] == instrument]
    plot_boxplots(df_tmp, subscales, instrument)
    create_dir(instrument)
    # split into groups:
    df_tlx_baseline = filter_condition(df_tmp, 'baseline')
    df_tlx_zpdes = filter_condition(df_tmp, 'zpdes')
    # get format:
    df_baseline_mean = format_questionnaire(df_tlx_baseline).groupby('session_id').mean()
    df_baseline_std = format_questionnaire(df_tlx_baseline).groupby('session_id').std()
    df_zpdes_mean = format_questionnaire(df_tlx_zpdes).groupby('session_id').mean()
    df_zpdes_std = format_questionnaire(df_tlx_zpdes).groupby('session_id').std()
    # Drop participant_id col
    df_baseline_mean.drop(columns=['id_participant'], inplace=True)
    df_baseline_std.drop(columns=['id_participant'], inplace=True)
    df_zpdes_mean.drop(columns=['id_participant'], inplace=True)
    df_zpdes_std.drop(columns=['id_participant'], inplace=True)
    display_cols_value(df_baseline_mean, df_baseline_std, df_zpdes_mean, df_zpdes_std, instrument)


def plot_all_questionnaires():
    # Read all answers:
    df = pd.read_csv('../outputs/old_v0/all_answers.csv')
    df.drop(columns=['Unnamed: 0'], inplace=True)
    df.columns = ['id', 'condition', 'component', 'instrument', 'handle', 'session_id', 'value']

    # Share according to questionnaire:
    os.mkdir('../outputs/old_v0/mot-NASA-TLX')
    plot_questionnaire('mot-NASA-TLX',
                       subscales=['Mental Demand', 'Physical demand', 'Temporal demand', 'Performance', 'Effort',
                                  'Frustration'])
    os.mkdir('../outputs/old_v0/mot-SIMS')
    plot_questionnaire('mot-SIMS',
                       subscales=['Intrinsic motivation', 'Identified regulation', 'External regulation',
                                  'Amotivation'])
    os.mkdir('../outputs/old_v0/mot-TENS')
    plot_questionnaire('mot-TENS', subscales=['Competence', 'Autonomy'])
    os.mkdir('../outputs/old_v0/mot-UES')
    plot_questionnaire('mot-UES',
                       subscales=['FA-S.1', 'FA-S.2', 'FA-S.3', 'PU-S.1', 'PU-S.2', 'PU-S.3', 'AE-S.1', 'AE-S.2',
                                  'AE-S.3',
                                  'RW-S.1', 'RW-S.2', 'RW-S.3'])


study = 'v3_utl'
get_psychometrics(study)
