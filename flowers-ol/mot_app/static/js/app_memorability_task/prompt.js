let prompt_start, prompt_gratitude , prompt_correct, prompt_wrong ,prompt_button_end, prompt_button_restart;

if(language_code==='fr'){
    prompt_start = "Cliquez sur la souris pour débuter l'activité";
    prompt_gratitude = "Merci d'avoir participé à l'expérience";
    prompt_correct = "Correct";
    prompt_wrong = "Incorrect";
    prompt_button_end = "END";
    prompt_button_restart = "Redémarrer";

}else{
    prompt_start = "Please click the mouse to start this experiment";
    prompt_gratitude = "Thank you for joining the experiment.";
    prompt_correct = "Correct Answer";
    prompt_wrong = "Wrong Answer";
    prompt_button_end = "END";
    prompt_button_restart = "RESTART";
}