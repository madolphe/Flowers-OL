let prompt_start, prompt_question_direction, prompt_question_input, prompt_question_contrast, prompt_button_here,
prompt_gratitude, prompt_button_end, prompt_button_restart;

if(language_code==='fr'){
    prompt_start = "Cliquez sur la souris pour débuter l'activité";
    prompt_question_direction = "Direction de la ligne la plus longue: verticale ou horizontale?";
    prompt_question_input = "Verticale: appuyer sur \"f\"     Horizontale: appuyer sur \"j\"";
    prompt_question_contrast = "Quelle cible était la plus contrastée ?";
    prompt_button_here = "Ici!";
    prompt_gratitude = "Merci d'avoir participé à l'expérience";
    prompt_button_end = "END";
    prompt_button_restart = "Redémarrer";

}else{
    prompt_start = "Please click the mouse to start this experiment";
    prompt_question_direction = "Which line was longer, vertical or horizontal?";
    prompt_question_input = "Vertical:press key \"f\"     Horizontal:press key\"j\"";
    prompt_question_contrast = "Which target contrast was strong?";
    prompt_button_here = "Here!";
    prompt_gratitude = "Thank you for joining the experiment.";
    prompt_button_end = "END";
    prompt_button_restart = "RESTART";
}