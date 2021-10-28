let button_answer_label, button_play_label, button_exit_label,
    button_pause_label, button_next_episode_label, button_keep_label, end_game_label;
let prompt_remaining_time, prompt_msg_0_0, prompt_msg_0_1, prompt_msg_1_0, prompt_msg_congrats, prompt_msg_2_0,
    prompt_msg_2_1, prompt_final_msg, prompt_msg_3_0, prompt_msg_3_1;
if (language_code === 'fr') {
    button_answer_label = 'REPONSE';
    button_play_label = 'DEMARRER';
    button_exit_label = 'SORTIE';
    button_pause_label = 'PAUSE';
    button_next_episode_label = 'EPISODE SUIVANT';
    button_keep_label = 'JOUER';
    end_game_label = 'Fin du jeu: '
    prompt_remaining_time = 'TEMPS RESTANT';
    prompt_msg_0_0 = 'Vous avez retrouvé ';
    prompt_msg_0_1 = ' cible(s).';
    prompt_msg_1_0 = '\n Malheureusement, il en manque ';
    prompt_msg_congrats = '\n Bien joué!';
    prompt_msg_2_0 = '\n Vous avez oublié ';
    prompt_msg_2_1 = ' cible(s).'
    prompt_msg_3_0 = 'Malheureusement, vous avez aussi sélectionné ';
    prompt_msg_3_1 = ' guarde(s)! Évitez les la prochaine fois.';
    prompt_final_msg = ' épisode(s) consécutif(s) joués. Continuez !'
} else {
    button_answer_label = 'ANSWER';
    button_play_label = 'START';
    button_exit_label = 'EXIT';
    button_pause_label = 'BREAK';
    button_next_episode_label = 'NEXT EPISODE';
    button_keep_label = 'PLAY';
    end_game_label = 'End game: '
    prompt_remaining_time = 'TIME';
    prompt_msg_0_0 = 'You have retrieved ';
    prompt_msg_0_1 = ' target(s).';
    prompt_msg_1_0 = '\n Unfortunately, you missed '
    prompt_msg_congrats = '\n Congratulations! ';
    prompt_msg_2_0 = '\n You have missed ' ;
    prompt_msg_2_1 = ' target(s).';
    prompt_msg_3_0 = 'Unfortunately, you have also selected ';
    prompt_msg_3_1 = ' guard(s)! Try to avoid them next time.';
    prompt_final_msg = ' played episodes. Keep practicing !'
}