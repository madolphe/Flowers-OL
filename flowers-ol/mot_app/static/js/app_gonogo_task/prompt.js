let prompt_start, prompt_gratitude, prompt_button_restart, prompt_correct, prompt_wrong, prompt_button_end;
let text_title_0, text_tutorial_0_0, text_tutorial_0_1, text_tutorial_0_2, text_tutorial_0_3;
let text_tutorial_1_0,text_tutorial_1_1, text_tutorial_2_0, text_tutorial_3_0, text_tutorial_4_0, text_tutorial_4_1,
    text_tutorial_5_0, text_tutorial_6_1, text_tutorial_6_2;
let text_start, text_end;
let text_button_next, text_button_previous, text_button_start;

if(language_code==='fr'){
    prompt_start = "Cliquez sur la souris pour débuter l'activité";
    prompt_gratitude = "Merci d'avoir participé à l'expérience";
    prompt_button_restart = "Redémarrer";
    prompt_correct = "Correct";
    prompt_wrong = "Incorrect";
    prompt_button_end = "FIN";
    text_title_0 = "INSTRUCTIONS" ;
    text_tutorial_0_0 = "Le but de cette expérience est de mesurer votre capacité à distinguer " ;
    text_tutorial_0_1 = "les informations pertinentes des informations non pertinentes. À chaque essai, vous verrez " ;
    text_tutorial_0_2 = "une séquence de chiffres. Votre tâche consiste à vous concentrer sur le chiffre [7] et " ;
    text_tutorial_0_3 = "répondre si le nombre après le [7] est le [3] ou non" ;
    text_tutorial_1_0 = "Si le nombre est 3 après 7," ;
    text_tutorial_1_1 = "veuillez appuyer sur la touche J de votre clavier le plus rapidement possible" ;
    text_tutorial_2_0 = "Sinon, n'appuyez sur aucune touche." ;
    text_tutorial_3_0 = "Commençons les pratiques." ;
    text_tutorial_3_1 = "Vous obtenez le feedback de la réponse pendant les pratiques." ;
    text_tutorial_4_0 = "Commençons l'expérience principale." ;
    text_tutorial_4_1 = "Pas de retour de réponse pendant cette expérience." ;
    text_tutorial_5_0 = "Temps de pause." ;
    text_tutorial_6_1 = "Merci pour votre effort. Quand vous êtes prêt," ;
    text_tutorial_6_2 = "Veuillez cliquer sur le bouton de démarrage pour redémarrer." ;
    // TASK
    text_start = "Veuillez cliquer sur la souris pour commencer cette expérience" ;
    text_end = "Merci de participer à l'expérience" ;
    text_button_next = "Suivant";
    text_button_previous = "Précédent";
    text_button_start = "Démarrer";

}else{
    prompt_start = "Please click the mouse to start this experiment";
    prompt_gratitude = "Thank you for joining the experiment.";
    prompt_button_restart = "RESTART";
    prompt_correct = "Correct Answer";
    prompt_wrong = "Wrong Answer";
    prompt_button_end = "END";
    // TUTORIAL
    text_title_0 = "INSTRUCTIONS";
    text_tutorial_0_0 = "The goal of this experiment is to measure your ability to distinguish";
    text_tutorial_0_1 = "relevant from irrelevant information. On each trial, you will see ";
    text_tutorial_0_2 = "a sequence of numbers. Your task is to focus on the number [7] and";
    text_tutorial_0_3 = "answer whether the number after the [7] is the [3] or not.";
    text_tutorial_1_0 = "If the number is 3 after 7,";
    text_tutorial_1_1 = "please press the key J on your keyboard as soon as possible.";
    text_tutorial_2_0 = "If not, please don't press any key.";
    text_tutorial_3_0 = "Let's start the practices.";
    text_tutorial_3_1 = "You get the response feedback during the practices.";
    text_tutorial_4_0 = "Let's start the main experiment.";
    text_tutorial_4_1 = "No response feedback during this experiment.";
    text_tutorial_5_0 = "Break time.";
    text_tutorial_6_1 = "Thank you for your effort. When you are ready,";
    text_tutorial_6_2 = "please click the start button to restart.";
    // TASK
    text_start = "Please click the mouse to start this experiment";
    text_end = "Thank you for joining the experiment.";
    text_button_next = "Next";
    text_button_previous = "Previous";
    text_button_start = "Start";
}