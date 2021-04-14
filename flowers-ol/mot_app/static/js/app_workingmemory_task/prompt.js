let prompt_start, prompt_gratitude, prompt_button_end, prompt_button_restart, prompt_button_click;

if(language_code==='fr'){
    prompt_start = "Cliquez sur la souris pour débuter l'activité";
    prompt_gratitude = "Merci d'avoir participé à l'expérience";
    prompt_button_end = "FIN";
    prompt_button_restart = "Redémarrer";
    prompt_button_click = "Cliquer dans l'ordre";

}else{
    prompt_start = "Please click the mouse to start this experiment";
    prompt_gratitude = "Thank you for joining the experiment.";
    prompt_button_end = "END";
    prompt_button_restart = "RESTART";
    prompt_button_click = "Click in order";
}